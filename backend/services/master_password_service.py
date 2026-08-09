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

    def change_master_password(self, current_password: str, new_password: str) -> VaultService:
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

        # Validate that the derived vault_id is correct (extra safety)
        try:
            uuid.UUID(decrypted_vault_id)
        except ValueError:
            raise InvalidMasterPasswordError("Vault ID decryption failed. Wrong current master password.")

        new_parameters = self.key_derivation_service.default_parameters()
        new_salt = self.key_derivation_service.generate_salt(new_parameters.salt_length)
        new_encryption_service = self._build_encryption_service(new_password, new_salt, new_parameters)

        encrypted_vault_id = new_encryption_service.encrypt(decrypted_vault_id)
        
        # Verify the new key works properly before committing
        verify_decrypted = new_encryption_service.decrypt(encrypted_vault_id)
        if verify_decrypted != decrypted_vault_id:
            raise RuntimeError("New encryption service failed validation. Aborting.")

        encrypted_entries_data = []
        entries = self.repository.list_all_entries()
        for entry in entries:
            dec_password = old_encryption_service.decrypt(entry.password)
            enc_password = new_encryption_service.encrypt(dec_password)
            
            enc_notes = ""
            if entry.notes:
                dec_notes = old_encryption_service.decrypt(entry.notes)
                enc_notes = new_encryption_service.encrypt(dec_notes)
                
            updated_at = self.repository._timestamp()
            encrypted_entries_data.append((entry.id, enc_password, enc_notes, updated_at))

        encrypted_history_data = []
        for entry in entries:
            history = self.repository.list_password_history(entry.id)
            for h in history:
                dec_h_password = old_encryption_service.decrypt(h.password)
                enc_h_password = new_encryption_service.encrypt(dec_h_password)
                encrypted_history_data.append((h.id, enc_h_password))

        self.repository.update_vault_crypto_transaction(
            version=SCHEMA_VERSION,
            vault_id=encrypted_vault_id,
            argon_parameters=self.key_derivation_service.serialize_parameters(new_parameters),
            salt=self.key_derivation_service.encode_salt(new_salt),
            encrypted_entries_data=encrypted_entries_data,
            encrypted_history_data=encrypted_history_data,
        )

        # Invalidate biometric credential if any, since it wraps the old key
        self.repository.update_biometric_metadata(
            enabled=False,
            platform=None,
            enrolled_at=None,
            wrapped_key=None,
        )

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
