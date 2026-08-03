import base64
import keyring
from keyring.errors import KeyringError, PasswordDeleteError

import threading

try:
    import LocalAuthentication
except ImportError:
    LocalAuthentication = None

from platform_auth.base import PlatformCredentialProvider
from utils.constants import KEYRING_SERVICE, KEYRING_TEST_SERVICE, KEYRING_USERNAME


class MacCredentialProvider(PlatformCredentialProvider):
    def is_biometric_available(self) -> bool:
        if LocalAuthentication is None:
            return False
        context = LocalAuthentication.LAContext.alloc().init()
        # 1 = LAPolicyDeviceOwnerAuthenticationWithBiometrics
        success, _ = context.canEvaluatePolicy_error_(1, None)
        return bool(success)

    def authenticate_user(self, prompt: str) -> bool:
        if LocalAuthentication is None:
            return False
            
        context = LocalAuthentication.LAContext.alloc().init()
        success, _ = context.canEvaluatePolicy_error_(1, None)
        if not success:
            return False

        result = [False]
        event = threading.Event()
        
        def reply(auth_success, _):
            result[0] = bool(auth_success)
            event.set()
            
        context.evaluatePolicy_localizedReason_reply_(1, prompt, reply)
        event.wait()
        return result[0]

    def get_authentication_type(self) -> str:
        if LocalAuthentication is None:
            return "None"
        context = LocalAuthentication.LAContext.alloc().init()
        success, _ = context.canEvaluatePolicy_error_(1, None)
        if not success:
            return "None"
            
        if hasattr(context, "biometryType"):
            b_type = context.biometryType()
            if b_type == 1:
                return "Touch ID"
            elif b_type == 2:
                return "Face ID"
            elif b_type == 4:
                return "Optic ID"
        return "Biometrics"

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
        return "macOS"
