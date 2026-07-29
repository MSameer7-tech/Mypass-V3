import base64
import json
import os


class AesGcmEncryptionService:
    def __init__(self, key: bytes):
        self.key = key

    def encrypt(self, value: str) -> str:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        nonce = os.urandom(12)
        ciphertext = AESGCM(self.key).encrypt(nonce, value.encode(), None)
        payload = {
            "nonce": base64.b64encode(nonce).decode(),
            "ciphertext": base64.b64encode(ciphertext).decode(),
        }
        return json.dumps(payload)

    def decrypt(self, value: str) -> str:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        payload = json.loads(value)
        nonce = base64.b64decode(payload["nonce"].encode())
        ciphertext = base64.b64decode(payload["ciphertext"].encode())
        plaintext = AESGCM(self.key).decrypt(nonce, ciphertext, None)
        return plaintext.decode()

    @classmethod
    def from_key_file(cls, key_file: str):
        with open(key_file, "rb") as file_handle:
            return cls(file_handle.read())


class FernetEncryptionService:
    def __init__(self, key: bytes):
        from cryptography.fernet import Fernet

        self._fernet = Fernet(key)

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        return self._fernet.decrypt(value.encode()).decode()

    @classmethod
    def from_key_file(cls, key_file: str):
        with open(key_file, "rb") as file_handle:
            return cls(file_handle.read())
