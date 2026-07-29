from cryptography.fernet import Fernet

class FernetEncryptionService:
    def __init__(self, key: bytes):
        self._fernet = Fernet(key)

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        return self._fernet.decrypt(value.encode()).decode()

    @classmethod
    def from_key_file(cls, key_file: str):
        with open(key_file, "rb") as file_handle:
            return cls(file_handle.read())
