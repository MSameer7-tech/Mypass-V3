import time
from platform_auth.factory import PlatformFactory
from database.repository import VaultRepository
from crypto.encryption import AesGcmEncryptionService
from services.vault_service import VaultService


class AuthenticationService:
    """
    Facade for platform-specific authentication and secure credential storage.
    Delegates calls to the appropriate PlatformCredentialProvider and owns
    the biometric unlock flow.
    """

    def __init__(self, repository: VaultRepository):
        self.repository = repository
        self._provider = PlatformFactory.get_provider()

    def is_secure_storage_available(self) -> bool:
        return self._provider.is_secure_storage_available()

    def store_secret(self, secret: bytes) -> bool:
        return self._provider.store_secret(secret)

    def retrieve_secret(self) -> bytes | None:
        return self._provider.retrieve_secret()

    def delete_secret(self) -> bool:
        return self._provider.delete_secret()

    def get_platform_name(self) -> str:
        return self._provider.get_platform_name()

    def is_biometric_available(self) -> bool:
        return self._provider.is_biometric_available()

    def get_authentication_type(self) -> str:
        return self._provider.get_authentication_type()

    def is_biometric_enabled(self) -> bool:
        metadata = self.repository.get_metadata()
        if not metadata.biometric_enabled:
            return False
        if metadata.biometric_platform and metadata.biometric_platform != self.get_platform_name():
            return False
        return True

    def unlock_vault_with_biometrics(self, prompt: str) -> VaultService | None:
        if not self.is_biometric_enabled() or not self.is_biometric_available():
            return None

        if not self._provider.authenticate_user(prompt):
            return None

        secret = self.retrieve_secret()
        if not secret:
            return None

        encryption_service = AesGcmEncryptionService(secret)
        metadata = self.repository.get_metadata()
        try:
            encryption_service.decrypt(metadata.vault_id)
        except Exception:
            return None

        return VaultService(self.repository, encryption_service)

    def enable_biometrics(self, prompt: str) -> bool:
        if self._provider.authenticate_user(prompt):
            self.repository.update_biometric_metadata(
                enabled=True,
                platform=self.get_platform_name(),
                enrolled_at=time.time(),
            )
            return True
        return False

    def disable_biometrics(self) -> None:
        self.repository.update_biometric_metadata(
            enabled=False,
            platform=None,
            enrolled_at=None,
        )
