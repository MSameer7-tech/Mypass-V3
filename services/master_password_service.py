import os
import uuid

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

    def is_configured(self) -> bool:
        metadata = self.repository.get_metadata()
        return bool(metadata.salt)

    def create_vault_service(self, master_password: str) -> VaultService:
        if self.is_configured():
            return self.unlock_vault(master_password)

        parameters = self.key_derivation_service.default_parameters()
        salt = self.key_derivation_service.generate_salt(parameters.salt_length)
        encryption_service = self._build_encryption_service(master_password, salt, parameters)
        vault_id = encryption_service.encrypt(str(uuid.uuid4()))
        self.repository.update_metadata_security(
            version=SCHEMA_VERSION,
            vault_id=vault_id,
            argon_parameters=self.key_derivation_service.serialize_parameters(parameters),
            salt=self.key_derivation_service.encode_salt(salt),
        )
        self._migrate_legacy_key_if_present(encryption_service)
        return VaultService(self.repository, encryption_service)

    def unlock_vault(self, master_password: str) -> VaultService:
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
        except Exception as error:
            raise InvalidMasterPasswordError("Wrong master password.") from error

        if not upgraded_legacy_vault and self._needs_secure_notes_upgrade(metadata.version):
            self._encrypt_existing_notes(encryption_service)
            self.repository.update_metadata_security(
                version=SCHEMA_VERSION,
                vault_id=metadata.vault_id,
                argon_parameters=metadata.argon_parameters,
                salt=metadata.salt,
            )
        return VaultService(self.repository, encryption_service)

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
