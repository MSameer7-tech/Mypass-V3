import os
import uuid

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

        try:
            encryption_service.decrypt(metadata.vault_id)
        except Exception as error:
            raise InvalidMasterPasswordError("Wrong master password.") from error

        return VaultService(self.repository, encryption_service)

    def _build_encryption_service(self, master_password: str, salt: bytes, parameters):
        key = self.key_derivation_service.derive_key(master_password, salt, parameters)
        return self.encryption_service_factory(key)

    def _migrate_legacy_key_if_present(self, new_encryption_service) -> None:
        if not self.legacy_key_file or not os.path.exists(self.legacy_key_file):
            return

        legacy_encryption_service = self.encryption_service_factory.from_key_file(self.legacy_key_file)
        for entry in self.repository.list_all_entries():
            decrypted_password = legacy_encryption_service.decrypt(entry.password)
            reencrypted_password = new_encryption_service.encrypt(decrypted_password)
            self.repository.update_entry_password(entry.id, reencrypted_password)
        os.remove(self.legacy_key_file)

    def _default_encryption_factory(self):
        from crypto.encryption import FernetEncryptionService

        return FernetEncryptionService
