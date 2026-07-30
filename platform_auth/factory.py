import platform

from platform_auth.base import PlatformCredentialProvider
from platform_auth.linux_auth import LinuxCredentialProvider
from platform_auth.mac_auth import MacCredentialProvider
from platform_auth.windows_auth import WindowsCredentialProvider


class PlatformFactory:
    @staticmethod
    def get_provider() -> PlatformCredentialProvider:
        system = platform.system()
        if system == "Windows":
            return WindowsCredentialProvider()
        elif system == "Darwin":
            return MacCredentialProvider()
        else:
            return LinuxCredentialProvider()
