import base64
import keyring
from keyring.errors import KeyringError, PasswordDeleteError

from platform_auth.base import PlatformCredentialProvider
from utils.constants import KEYRING_SERVICE, KEYRING_TEST_SERVICE, KEYRING_USERNAME


class LinuxCredentialProvider(PlatformCredentialProvider):
    def is_biometric_available(self) -> bool:
        return False

    def authenticate_user(self, prompt: str) -> bool:
        return False

    def get_authentication_type(self) -> str:
        return "None"

    def is_secure_storage_available(self) -> bool:
        test_secret = "test_probe_secret"
        try:
            keyring.set_password(KEYRING_TEST_SERVICE, KEYRING_USERNAME, test_secret)
            retrieved = keyring.get_password(KEYRING_TEST_SERVICE, KEYRING_USERNAME)
            keyring.delete_password(KEYRING_TEST_SERVICE, KEYRING_USERNAME)
            return retrieved == test_secret
        except KeyringError:
            return False

    def store_secret(self, secret: bytes) -> bool:
        try:
            encoded = base64.b64encode(secret).decode("utf-8")
            keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, encoded)
            return True
        except KeyringError:
            return False

    def retrieve_secret(self) -> bytes | None:
        try:
            encoded = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
            if not encoded:
                return None
            return base64.b64decode(encoded.encode("utf-8"))
        except (KeyringError, base64.binascii.Error):
            return None

    def delete_secret(self) -> bool:
        try:
            keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
            return True
        except PasswordDeleteError:
            # Treated as success if it doesn't exist
            return True
        except KeyringError:
            return False

    def get_platform_name(self) -> str:
        return "Linux"
