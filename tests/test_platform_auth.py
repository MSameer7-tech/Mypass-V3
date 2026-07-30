import base64
from unittest.mock import patch, Mock
import pytest

import keyring
from keyring.errors import KeyringError, PasswordDeleteError

from platform_auth.base import PlatformCredentialProvider
from platform_auth.factory import PlatformFactory
from platform_auth.linux_auth import LinuxCredentialProvider
from platform_auth.mac_auth import MacCredentialProvider
from platform_auth.windows_auth import WindowsCredentialProvider
from services.authentication_service import AuthenticationService
from utils.constants import KEYRING_SERVICE, KEYRING_TEST_SERVICE, KEYRING_USERNAME


class TestPlatformFactory:
    @patch("platform.system", return_value="Windows")
    def test_factory_returns_windows(self, mock_system):
        provider = PlatformFactory.get_provider()
        assert isinstance(provider, WindowsCredentialProvider)
        assert provider.get_platform_name() == "Windows"

    @patch("platform.system", return_value="Darwin")
    def test_factory_returns_mac(self, mock_system):
        provider = PlatformFactory.get_provider()
        assert isinstance(provider, MacCredentialProvider)
        assert provider.get_platform_name() == "macOS"

    @patch("platform.system", return_value="Linux")
    def test_factory_returns_linux(self, mock_system):
        provider = PlatformFactory.get_provider()
        assert isinstance(provider, LinuxCredentialProvider)
        assert provider.get_platform_name() == "Linux"


class TestAuthenticationServiceWithKeyring:
    @patch("platform_auth.mac_auth.keyring")
    @patch("platform.system", return_value="Darwin")
    def test_service_delegates_to_provider(self, mock_system, mock_keyring):
        mock_repo = Mock()
        service = AuthenticationService(mock_repo)
        
        # Test store_secret
        secret = b"my_secret_key"
        encoded = base64.b64encode(secret).decode("utf-8")
        assert service.store_secret(secret) is True
        mock_keyring.set_password.assert_called_with(KEYRING_SERVICE, KEYRING_USERNAME, encoded)
        
        # Test retrieve_secret
        mock_keyring.get_password.return_value = encoded
        assert service.retrieve_secret() == secret
        mock_keyring.get_password.assert_called_with(KEYRING_SERVICE, KEYRING_USERNAME)
        
        # Test delete_secret
        assert service.delete_secret() is True
        mock_keyring.delete_password.assert_called_with(KEYRING_SERVICE, KEYRING_USERNAME)
        
        assert service.get_platform_name() == "macOS"

    @patch("platform_auth.mac_auth.keyring")
    @patch("platform.system", return_value="Darwin")
    def test_is_secure_storage_available(self, mock_system, mock_keyring):
        mock_repo = Mock()
        service = AuthenticationService(mock_repo)
        
        # Mock retrieve to return the same secret
        mock_keyring.get_password.return_value = "test_probe_secret"
        assert service.is_secure_storage_available() is True
        
        # Test failure case
        mock_keyring.get_password.side_effect = KeyringError("Backend error")
        assert service.is_secure_storage_available() is False

    @patch("platform_auth.mac_auth.keyring")
    @patch("platform.system", return_value="Darwin")
    def test_invalid_base64_retrieval(self, mock_system, mock_keyring):
        mock_repo = Mock()
        service = AuthenticationService(mock_repo)
        mock_keyring.get_password.return_value = "invalid_base64_!@#"
        assert service.retrieve_secret() is None

    @patch("platform_auth.mac_auth.keyring")
    @patch("platform.system", return_value="Darwin")
    def test_delete_missing_secret(self, mock_system, mock_keyring):
        mock_repo = Mock()
        service = AuthenticationService(mock_repo)
        # Ensure password delete error still returns True (success since it's gone)
        mock_keyring.delete_password.side_effect = PasswordDeleteError("Not found")
        assert service.delete_secret() is True

    @patch("platform_auth.mac_auth.keyring")
    @patch("platform.system", return_value="Darwin")
    def test_biometric_success(self, mock_system, mock_keyring):
        mock_repo = Mock()
        mock_metadata = Mock()
        mock_metadata.biometric_enabled = True
        mock_metadata.biometric_platform = "macOS"
        mock_metadata.vault_id = "test-vault-id"
        mock_repo.get_metadata.return_value = mock_metadata

        service = AuthenticationService(mock_repo)
        service._provider = Mock()
        service._provider.is_biometric_available.return_value = True
        service._provider.authenticate_user.return_value = True
        service._provider.get_platform_name.return_value = "macOS"
        service.retrieve_secret = Mock(return_value=b"32bytekey" + b"0" * 23)

        with patch("services.authentication_service.AesGcmEncryptionService") as mock_aes:
            # Mock the decrypt to not raise an error
            mock_aes.return_value.decrypt.return_value = "decrypted"
            vault_service = service.unlock_vault_with_biometrics("Prompt")
            
            assert vault_service is not None
            mock_aes.return_value.decrypt.assert_called_with("test-vault-id")
            
    @patch("platform_auth.mac_auth.keyring")
    @patch("platform.system", return_value="Darwin")
    def test_biometric_cancellation_or_failure(self, mock_system, mock_keyring):
        mock_repo = Mock()
        mock_metadata = Mock()
        mock_metadata.biometric_enabled = True
        mock_metadata.biometric_platform = "macOS"
        mock_repo.get_metadata.return_value = mock_metadata

        service = AuthenticationService(mock_repo)
        service._provider = Mock()
        service._provider.is_biometric_available.return_value = True
        service._provider.authenticate_user.return_value = False
        service._provider.get_platform_name.return_value = "macOS"

        vault_service = service.unlock_vault_with_biometrics("Prompt")
        assert vault_service is None
        
    @patch("platform_auth.mac_auth.keyring")
    @patch("platform.system", return_value="Darwin")
    def test_biometric_sensor_unavailable(self, mock_system, mock_keyring):
        mock_repo = Mock()
        mock_metadata = Mock()
        mock_metadata.biometric_enabled = True
        mock_metadata.biometric_platform = "macOS"
        mock_repo.get_metadata.return_value = mock_metadata

        service = AuthenticationService(mock_repo)
        service._provider = Mock()
        service._provider.is_biometric_available.return_value = False
        service._provider.get_platform_name.return_value = "macOS"

        vault_service = service.unlock_vault_with_biometrics("Prompt")
        assert vault_service is None
        service._provider.authenticate_user.assert_not_called()

    @patch("platform_auth.mac_auth.keyring")
    @patch("platform.system", return_value="Darwin")
    def test_biometric_disabled(self, mock_system, mock_keyring):
        mock_repo = Mock()
        mock_metadata = Mock()
        mock_metadata.biometric_enabled = False
        mock_repo.get_metadata.return_value = mock_metadata

        service = AuthenticationService(mock_repo)
        service._provider = Mock()
        
        vault_service = service.unlock_vault_with_biometrics("Prompt")
        assert vault_service is None
        service._provider.authenticate_user.assert_not_called()
