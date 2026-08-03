from abc import ABC, abstractmethod


class PlatformCredentialProvider(ABC):
    """
    Abstract base class for platform-specific secure authentication 
    and credential storage (e.g., macOS Keychain, Windows Credential Manager, Linux Secret Service).
    """

    @abstractmethod
    def is_secure_storage_available(self) -> bool:
        """
        Returns True if the platform's secure storage backend is available and working.
        This should perform a non-destructive test (write/read/delete a temporary secret).
        """
        pass

    @abstractmethod
    def is_biometric_available(self) -> bool:
        """
        Returns True if the platform supports biometric authentication and hardware is present.
        """
        pass

    @abstractmethod
    def authenticate_user(self, prompt: str) -> bool:
        """
        Prompts the user to authenticate using biometrics.
        Returns True if authentication succeeded, False otherwise.
        """
        pass

    @abstractmethod
    def get_authentication_type(self) -> str:
        """
        Returns the type of biometric authentication available, e.g., 'Touch ID', 'Windows Hello', or 'None'.
        """
        pass

    @abstractmethod
    def store_secret(self, secret: bytes) -> bool:
        """
        Securely stores a secret (e.g. master vault key) in the OS credential store.
        Returns True if successful, False otherwise.
        """
        pass

    @abstractmethod
    def retrieve_secret(self) -> bytes | None:
        """
        Retrieves the securely stored secret.
        Returns the decrypted bytes if successful, or None if not found/error.
        """
        pass

    @abstractmethod
    def delete_secret(self) -> bool:
        """
        Removes the stored secret from the OS credential store.
        Returns True if successful or if the secret was already deleted.
        """
        pass

    @abstractmethod
    def get_platform_name(self) -> str:
        """Returns the human-readable name of the platform (e.g. 'macOS', 'Windows')."""
        pass
