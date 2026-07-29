import os
import tempfile
import unittest

from database.database import DatabaseManager
from database.repository import VaultRepository
from services.master_password_service import InvalidMasterPasswordError, MasterPasswordService


class FakeArgonParameters:
    def __init__(self, salt_length: int = 8):
        self.salt_length = salt_length


class FakeKeyDerivationService:
    def default_parameters(self):
        return FakeArgonParameters()

    def generate_salt(self, length: int) -> bytes:
        return b"s" * length

    def derive_key(self, master_password: str, salt: bytes, parameters) -> bytes:
        return f"{master_password}:{salt.decode()}".encode()

    def serialize_parameters(self, parameters) -> str:
        return f"salt_length={parameters.salt_length}"

    def deserialize_parameters(self, raw_parameters: str):
        salt_length = int(raw_parameters.split("=")[1])
        return FakeArgonParameters(salt_length=salt_length)

    def encode_salt(self, salt: bytes) -> str:
        return salt.decode()

    def decode_salt(self, encoded_salt: str) -> bytes:
        return encoded_salt.encode()


class FakeEncryptionService:
    def __init__(self, key: bytes):
        self.key = key.decode()

    def encrypt(self, value: str) -> str:
        return f"{self.key}|{value}"

    def decrypt(self, value: str) -> str:
        prefix = f"{self.key}|"
        if not value.startswith(prefix):
            raise ValueError("invalid key")
        return value[len(prefix):]

    @classmethod
    def from_key_file(cls, key_file: str):
        with open(key_file, "rb") as file_handle:
            return cls(file_handle.read())


class MasterPasswordServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_file = os.path.join(self.temp_dir.name, "vault.db")
        self.legacy_key_file = os.path.join(self.temp_dir.name, "vault.key")
        self.repository = VaultRepository(DatabaseManager(self.db_file))
        self.service = MasterPasswordService(
            self.repository,
            key_derivation_service=FakeKeyDerivationService(),
            encryption_service_factory=FakeEncryptionService,
            legacy_key_file=self.legacy_key_file,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_master_password_stores_salt_and_not_plain_password(self):
        self.service.create_vault_service("MySecurePassword123")
        metadata = self.repository.get_metadata()

        self.assertTrue(metadata.salt)
        self.assertNotEqual(metadata.salt, "MySecurePassword123")
        self.assertIn("salt_length=", metadata.argon_parameters)

    def test_wrong_password_cannot_unlock_vault(self):
        self.service.create_vault_service("MySecurePassword123")

        with self.assertRaises(InvalidMasterPasswordError):
            self.service.unlock_vault("WrongPassword")

    def test_legacy_key_file_is_removed_after_migration(self):
        with open(self.legacy_key_file, "wb") as file_handle:
            file_handle.write(b"legacy")

        self.repository.create_entry(
            type("Entry", (), {
                "id": None,
                "title": "example.com",
                "website": "example.com",
                "username": "user@example.com",
                "password": "legacy|Secret123!",
                "notes": "",
                "category": "",
                "favorite": False,
                "created_at": "",
                "updated_at": "",
            })()
        )

        vault_service = self.service.create_vault_service("MySecurePassword123")
        migrated_entry = vault_service.find_credential("example.com")

        self.assertFalse(os.path.exists(self.legacy_key_file))
        self.assertEqual(migrated_entry.password, "Secret123!")


if __name__ == "__main__":
    unittest.main()
