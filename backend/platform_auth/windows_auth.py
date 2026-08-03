import base64
import keyring
from keyring.errors import KeyringError, PasswordDeleteError

import asyncio

try:
    from winrt.windows.security.credentials.ui import UserConsentVerifier, UserConsentVerifierAvailability, UserConsentVerificationResult
except ImportError:
    UserConsentVerifier = None

from platform_auth.base import PlatformCredentialProvider
from utils.constants import KEYRING_SERVICE, KEYRING_TEST_SERVICE, KEYRING_USERNAME


class WindowsCredentialProvider(PlatformCredentialProvider):
    def is_biometric_available(self) -> bool:
        if UserConsentVerifier is None:
            return False
        
        async def check_availability():
            availability = await UserConsentVerifier.check_availability_async()
            # 0 = Available
            return availability == UserConsentVerifierAvailability.AVAILABLE

        try:
            return asyncio.run(check_availability())
        except Exception:
            return False

    def authenticate_user(self, prompt: str) -> bool:
        if UserConsentVerifier is None:
            return False
            
        async def prompt_user():
            result = await UserConsentVerifier.request_verification_async(prompt)
            # 0 = VERIFIED
            return result == UserConsentVerificationResult.VERIFIED

        try:
            return asyncio.run(prompt_user())
        except Exception:
            return False

    def get_authentication_type(self) -> str:
        if self.is_biometric_available():
            return "Windows Hello"
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
        return "Windows"
