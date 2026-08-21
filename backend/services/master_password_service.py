import os
import uuid
import time

from crypto.encryption import FernetEncryptionService
from crypto.key_derivation import Argon2KeyDerivationService
from database.repository import VaultRepository
from services.vault_service import VaultService
from utils.constants import SCHEMA_VERSION


class InvalidMasterPasswordError(Exception):
    pass


class MasterPasswordService:
    def __init__(
        self,
        repository: VaultRepository,
        *,
        key_derivation_service=None,
        encryption_service_factory=None,
        legacy_key_file: str | None = None,
    ):
        self.repository = repository
        self.key_derivation_service = key_derivation_service or Argon2KeyDerivationService()
        self.encryption_service_factory = encryption_service_factory or self._default_encryption_factory()
        self.legacy_encryption_service_factory = FernetEncryptionService
        self.legacy_key_file = legacy_key_file
        self._failed_attempts = 0

    def is_configured(self) -> bool:
        metadata = self.repository.get_metadata()
        return bool(metadata.salt)

    def create_vault_service(self, master_password: str) -> VaultService:
        if self.is_configured():
            return self.unlock_vault(master_password)

        parameters = self.key_derivation_service.default_parameters()
        salt = self.key_derivation_service.generate_salt(parameters.salt_length)
        encryption_service = self._build_encryption_service(master_password, salt, parameters)
        
        # Derive a backup key using a static salt for disaster recovery portability
        backup_salt = b"mypass_backup_static_salt_v1_000"
        backup_encryption_service = self._build_encryption_service(master_password, backup_salt, parameters)
        
        vault_id = encryption_service.encrypt(str(uuid.uuid4()))
        self.repository.update_metadata_security(
            version=SCHEMA_VERSION,
            vault_id=vault_id,
            argon_parameters=self.key_derivation_service.serialize_parameters(parameters),
            salt=self.key_derivation_service.encode_salt(salt),
        )
        self._migrate_legacy_key_if_present(encryption_service)
        return VaultService(self.repository, encryption_service, backup_encryption_service)

    def unlock_vault(self, master_password: str) -> VaultService:
        if self._failed_attempts > 0:
            delay = min(2 ** (self._failed_attempts - 1), 10)
            time.sleep(delay)

        metadata = self.repository.get_metadata()
        parameters = self.key_derivation_service.deserialize_parameters(metadata.argon_parameters)
        salt = self.key_derivation_service.decode_salt(metadata.salt)
        encryption_service = self._build_encryption_service(master_password, salt, parameters)

        upgraded_legacy_vault = False
        try:
            if self._uses_legacy_fernet(metadata.version):
                legacy_encryption_service = self._build_legacy_encryption_service(
                    master_password,
                    salt,
                    parameters,
                )
                legacy_encryption_service.decrypt(metadata.vault_id)
                self._upgrade_legacy_vault(legacy_encryption_service, encryption_service)
                upgraded_legacy_vault = True
            else:
                encryption_service.decrypt(metadata.vault_id)
        except Exception:
            self._failed_attempts += 1
            raise InvalidMasterPasswordError("Wrong master password.")

        # Success: reset the counter
        self._failed_attempts = 0

        if not upgraded_legacy_vault and self._needs_secure_notes_upgrade(metadata.version):
            self._encrypt_existing_notes(encryption_service)
            self.repository.update_metadata_security(
                version=SCHEMA_VERSION,
                vault_id=metadata.vault_id,
                argon_parameters=metadata.argon_parameters,
                salt=metadata.salt,
            )
            
        backup_salt = b"mypass_backup_static_salt_v1_000"
        backup_encryption_service = self._build_encryption_service(master_password, backup_salt, parameters)
        return VaultService(self.repository, encryption_service, backup_encryption_service)

    def change_master_password(
        self,
        current_password: str,
        new_password: str,
        auth_service=None,
    ) -> VaultService:
        if not current_password or not isinstance(current_password, str):
            raise ValueError("Current master password is required.")

        if not new_password or not isinstance(new_password, str) or len(new_password) < 8:
            raise ValueError("New master password must be at least 8 characters long.")

        if current_password == new_password:
            raise ValueError("New password must be different from current password.")

        metadata = self.repository.get_metadata()
        parameters = self.key_derivation_service.deserialize_parameters(metadata.argon_parameters)
        salt = self.key_derivation_service.decode_salt(metadata.salt)

        if self._failed_attempts > 0:
            delay = min(2 ** (self._failed_attempts - 1), 10)
            time.sleep(delay)

        try:
            old_encryption_service = self._build_encryption_service(current_password, salt, parameters)
            decrypted_vault_id = old_encryption_service.decrypt(metadata.vault_id)
        except Exception:
            self._failed_attempts += 1
            raise InvalidMasterPasswordError("Wrong current master password.")

        self._failed_attempts = 0

        # Validate that the derived vault_id is correct UUID (extra safety)
        try:
            uuid.UUID(decrypted_vault_id)
        except ValueError:
            raise InvalidMasterPasswordError("Vault ID decryption failed. Wrong current master password.")

        # --- Phase 1: Pre-Validation (In-Memory Decryption of 100% of Records) ---
        # Guarantees no database mutation occurs before every existing encrypted record has been successfully decrypted.
        entries = self.repository.list_all_entries()
        decrypted_entries = []
        for entry in entries:
            dec_password = old_encryption_service.decrypt(entry.password)
            dec_notes = old_encryption_service.decrypt(entry.notes) if entry.notes else ""
            decrypted_entries.append((entry.id, dec_password, dec_notes))

        decrypted_history = []
        for entry in entries:
            history = self.repository.list_password_history(entry.id)
            for h in history:
                dec_h_password = old_encryption_service.decrypt(h.password)
                decrypted_history.append((h.id, dec_h_password))

        # --- Phase 2: Derive New Key and Verify Self-Test Roundtrip ---
        new_parameters = self.key_derivation_service.default_parameters()
        new_salt = self.key_derivation_service.generate_salt(new_parameters.salt_length)
        new_encryption_service = self._build_encryption_service(new_password, new_salt, new_parameters)

        encrypted_vault_id = new_encryption_service.encrypt(decrypted_vault_id)
        verify_decrypted = new_encryption_service.decrypt(encrypted_vault_id)
        if verify_decrypted != decrypted_vault_id:
            raise RuntimeError("New encryption service failed validation self-test. Aborting rotation.")

        # --- Phase 3: In-Memory Re-Encryption with New Key ---
        encrypted_entries_data = []
        now = self.repository._timestamp()
        for entry_id, dec_password, dec_notes in decrypted_entries:
            enc_password = new_encryption_service.encrypt(dec_password)
            enc_notes = new_encryption_service.encrypt(dec_notes) if dec_notes else ""
            encrypted_entries_data.append((entry_id, enc_password, enc_notes, now))

        encrypted_history_data = []
        for history_id, dec_h_password in decrypted_history:
            enc_h_password = new_encryption_service.encrypt(dec_h_password)
            encrypted_history_data.append((history_id, enc_h_password))

        # --- Phase 4: Atomic Single-Connection Database Transaction ---
        # The database transaction updates metadata, entries, history, and biometric metadata atomically.
        self.repository.update_vault_crypto_transaction(
            version=SCHEMA_VERSION,
            vault_id=encrypted_vault_id,
            argon_parameters=self.key_derivation_service.serialize_parameters(new_parameters),
            salt=self.key_derivation_service.encode_salt(new_salt),
            encrypted_entries_data=encrypted_entries_data,
            encrypted_history_data=encrypted_history_data,
        )

        # --- Phase 5: Post-Commit Biometric Cleanup ---
        # Only after database transaction has committed successfully, purge the OS biometric secret.
        if auth_service is not None:
            try:
                auth_service.delete_secret()
            except Exception:
                pass

        backup_salt = b"mypass_backup_static_salt_v1_000"
        backup_encryption_service = self._build_encryption_service(new_password, backup_salt, new_parameters)
        return VaultService(self.repository, new_encryption_service, backup_encryption_service)

    def _build_encryption_service(self, master_password: str, salt: bytes, parameters):
        key = self.key_derivation_service.derive_key(master_password, salt, parameters)
        return self.encryption_service_factory(key)

    def _build_legacy_encryption_service(self, master_password: str, salt: bytes, parameters):
        derive_legacy_key = getattr(
            self.key_derivation_service,
            "derive_legacy_fernet_key",
            self.key_derivation_service.derive_key,
        )
        key = derive_legacy_key(master_password, salt, parameters)
        return self.legacy_encryption_service_factory(key)

    def _migrate_legacy_key_if_present(self, new_encryption_service) -> None:
        if not self.legacy_key_file or not os.path.exists(self.legacy_key_file):
            return

        legacy_encryption_service = self.legacy_encryption_service_factory.from_key_file(
            self.legacy_key_file
        )
        for entry in self.repository.list_all_entries():
            decrypted_password = legacy_encryption_service.decrypt(entry.password)
            reencrypted_password = new_encryption_service.encrypt(decrypted_password)
            self.repository.update_entry_password(entry.id, reencrypted_password)
            if entry.notes:
                self.repository.update_entry_notes(entry.id, new_encryption_service.encrypt(entry.notes))
        os.remove(self.legacy_key_file)

    def _default_encryption_factory(self):
        from crypto.encryption import AesGcmEncryptionService

        return AesGcmEncryptionService

    def _upgrade_legacy_vault(self, legacy_encryption_service, new_encryption_service) -> None:
        metadata = self.repository.get_metadata()
        decrypted_vault_id = legacy_encryption_service.decrypt(metadata.vault_id)
        encrypted_vault_id = new_encryption_service.encrypt(decrypted_vault_id)
        for entry in self.repository.list_all_entries():
            decrypted_password = legacy_encryption_service.decrypt(entry.password)
            reencrypted_password = new_encryption_service.encrypt(decrypted_password)
            self.repository.update_entry_password(entry.id, reencrypted_password)
            if entry.notes:
                self.repository.update_entry_notes(entry.id, new_encryption_service.encrypt(entry.notes))
        self.repository.update_metadata_security(
            version=SCHEMA_VERSION,
            vault_id=encrypted_vault_id,
            argon_parameters=metadata.argon_parameters,
            salt=metadata.salt,
        )

    def _uses_legacy_fernet(self, version: str) -> bool:
        try:
            major_version = int(version.split(".", 1)[0])
        except (ValueError, AttributeError):
            return True
        return major_version < 4

    def _needs_secure_notes_upgrade(self, version: str) -> bool:
        try:
            major_version = int(version.split(".", 1)[0])
        except (ValueError, AttributeError):
            return False
        return major_version < 5

    def _encrypt_existing_notes(self, encryption_service) -> None:
        for entry in self.repository.list_all_entries():
            if entry.notes:
                self.repository.update_entry_notes(entry.id, encryption_service.encrypt(entry.notes))
