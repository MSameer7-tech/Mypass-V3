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
        if not metadata.biometric_wrapped_key:
            return False
        return True

    def unlock_vault_with_biometrics(self, prompt: str) -> VaultService | None:
        if not self.is_biometric_enabled() or not self.is_biometric_available():
            return None

        metadata = self.repository.get_metadata()
        
        if not self._provider.authenticate_user(prompt):
            return None

        biometric_secret = self.retrieve_secret()
        if not biometric_secret:
            return None

        import json
        import base64
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        
        try:
            payload = json.loads(metadata.biometric_wrapped_key)
            nonce = base64.b64decode(payload["nonce"].encode())
            ciphertext = base64.b64decode(payload["ciphertext"].encode())
            
            aad = f"MyPass biometric master-key wrapper|{metadata.vault_id}".encode()
            
            master_key = AESGCM(biometric_secret).decrypt(nonce, ciphertext, aad)
        except Exception:
            return None

        encryption_service = AesGcmEncryptionService(master_key)
        try:
            encryption_service.decrypt(metadata.vault_id)
        except Exception:
            return None

        return VaultService(self.repository, encryption_service)

    def setup_biometrics(self, prompt: str, vault_service: VaultService) -> bool:
        if not self.is_biometric_available():
            return False

        if not self._provider.authenticate_user(prompt):
            return False

        import os
        import json
        import base64
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        biometric_secret = os.urandom(32)
        master_key = vault_service.encryption_service.key
        
        metadata = self.repository.get_metadata()
        aad = f"MyPass biometric master-key wrapper|{metadata.vault_id}".encode()
        
        nonce = os.urandom(12)
        ciphertext = AESGCM(biometric_secret).encrypt(nonce, master_key, aad)
        
        wrapped_key_payload = json.dumps({
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
        })

        if self.store_secret(biometric_secret):
            try:
                self.repository.update_biometric_metadata(
                    enabled=True,
                    platform=self.get_platform_name(),
                    enrolled_at=time.time(),
                    wrapped_key=wrapped_key_payload
                )
                return True
            except Exception:
                self.delete_secret()
                return False
                
        return False

    def disable_biometrics(self) -> None:
        self.delete_secret()
        self.repository.update_biometric_metadata(
            enabled=False,
            platform=None,
            enrolled_at=None,
            wrapped_key=None,
        )
