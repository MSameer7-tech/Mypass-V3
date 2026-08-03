import os
import tempfile
import unittest
import json

from database.database import DatabaseManager
from database.repository import VaultRepository
from services.master_password_service import InvalidMasterPasswordError, MasterPasswordService
from utils.constants import SCHEMA_VERSION


class FakeArgonParameters:
    def __init__(self, salt_length: int = 8):
        self.salt_length = salt_length


class FakeKeyDerivationService:
    def default_parameters(self):
        return FakeArgonParameters()

    def generate_salt(self, length: int) -> bytes:
        import os
        return os.urandom(length).hex()[:length].encode('utf-8')

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
        return json.dumps(
            {
                "key": self.key,
                "value": value,
                "tag": f"tag::{self.key}::{value}",
            }
        )

    def decrypt(self, value: str) -> str:
        payload = json.loads(value)
        expected_tag = f"tag::{self.key}::{payload['value']}"
        if payload["key"] != self.key or payload["tag"] != expected_tag:
            raise ValueError("invalid key")
        return payload["value"]

    @classmethod
    def from_key_file(cls, key_file: str):
        with open(key_file, "rb") as file_handle:
            return cls(file_handle.read())


class FakeLegacyEncryptionService(FakeEncryptionService):
    pass


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
        self.service.legacy_encryption_service_factory = FakeLegacyEncryptionService

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_master_password_stores_salt_and_not_plain_password(self):
        self.service.create_vault_service("MySecurePassword123")
        metadata = self.repository.get_metadata()

        self.assertTrue(metadata.salt)
        self.assertNotEqual(metadata.salt, "MySecurePassword123")
        self.assertIn("salt_length=", metadata.argon_parameters)
        self.assertEqual(metadata.version, SCHEMA_VERSION)

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
                "password": FakeLegacyEncryptionService(b"legacy").encrypt("Secret123!"),
                "notes": "",
                "category": "",
                "tags": "",
                "icon": "",
                "favorite": False,
                "created_at": "",
                "updated_at": "",
            })()
        )

        vault_service = self.service.create_vault_service("MySecurePassword123")
        migrated_entry = vault_service.find_credential("example.com")

        self.assertFalse(os.path.exists(self.legacy_key_file))
        self.assertEqual(migrated_entry.password, "Secret123!")

    def test_legacy_fernet_vault_is_upgraded_on_unlock(self):
        metadata = self.repository.get_metadata()
        self.repository.update_metadata_security(
            version="3.0",
            vault_id=FakeLegacyEncryptionService(b"MySecurePassword123:ssssssss").encrypt("vault-id"),
            argon_parameters="salt_length=8",
            salt="ssssssss",
        )
        self.repository.create_entry(
            type("Entry", (), {
                "id": None,
                "title": "example.com",
                "website": "example.com",
                "username": "user@example.com",
                "password": FakeLegacyEncryptionService(b"MySecurePassword123:ssssssss").encrypt("Secret123!"),
                "notes": "",
                "category": "",
                "tags": "",
                "icon": "",
                "favorite": False,
                "created_at": "",
                "updated_at": "",
            })()
        )

        vault_service = self.service.unlock_vault("MySecurePassword123")
        upgraded_metadata = self.repository.get_metadata()
        upgraded_entry = vault_service.find_credential("example.com")

        self.assertEqual(upgraded_metadata.version, SCHEMA_VERSION)
        self.assertEqual(upgraded_entry.password, "Secret123!")

    def test_tampered_ciphertext_is_rejected(self):
        vault_service = self.service.create_vault_service("MySecurePassword123")
        saved_entry = vault_service.save_entry(
            title="Personal Gmail",
            website="gmail.com",
            username="sameer@gmail.com",
            password="Secret123!",
        )
        stored_entry = self.repository.get_entry_by_id(saved_entry.id)
        tampered_password = stored_entry.password[:-1] + (
            "x" if stored_entry.password[-1] != "x" else "y"
        )
        self.repository.update_entry_password(saved_entry.id, tampered_password)

        with self.assertRaises(Exception):
            vault_service.find_credential("gmail.com")

    def test_existing_plaintext_notes_are_encrypted_on_unlock(self):
        self.repository.update_metadata_security(
            version="4.0",
            vault_id=FakeEncryptionService(b"MySecurePassword123:ssssssss").encrypt("vault-id"),
            argon_parameters="salt_length=8",
            salt="ssssssss",
        )
        self.repository.create_entry(
            type("Entry", (), {
                "id": None,
                "title": "WiFi",
                "website": "local-network",
                "username": "router",
                "password": FakeEncryptionService(b"MySecurePassword123:ssssssss").encrypt("Secret123!"),
                "notes": "Network key: secure-note",
                "category": "Personal",
                "tags": "wifi",
                "icon": "globe",
                "favorite": False,
                "created_at": "",
                "updated_at": "",
            })()
        )

        vault_service = self.service.unlock_vault("MySecurePassword123")
        stored_entry = self.repository.get_latest_entry_by_website("local-network")

        self.assertNotEqual(stored_entry.notes, "Network key: secure-note")
        self.assertEqual(vault_service.find_credential("local-network").notes, "Network key: secure-note")

    def test_change_master_password_success(self):
        vault_service = self.service.create_vault_service("MySecurePassword123")
        saved_entry = vault_service.save_entry(
            title="Personal Gmail",
            website="gmail.com",
            username="sameer@gmail.com",
            password="Secret123!",
            notes="Secure notes here"
        )
        old_metadata = self.repository.get_metadata()
        
        # Change password
        new_vault_service = self.service.change_master_password("MySecurePassword123", "NewPassword456")
        
        # Verify metadata was updated
        new_metadata = self.repository.get_metadata()
        self.assertNotEqual(old_metadata.salt, new_metadata.salt)
        self.assertIsNotNone(new_metadata.last_master_password_change)
        
        # Verify entry can be decrypted with new service
        entry = new_vault_service.find_credential("gmail.com")
        self.assertEqual(entry.password, "Secret123!")
        self.assertEqual(entry.notes, "Secure notes here")
        
        # Verify old password no longer works
        with self.assertRaises(InvalidMasterPasswordError):
            self.service.unlock_vault("MySecurePassword123")
            
        # Verify new password works
        self.assertIsNotNone(self.service.unlock_vault("NewPassword456"))

    def test_change_master_password_wrong_current(self):
        self.service.create_vault_service("MySecurePassword123")
        with self.assertRaises(InvalidMasterPasswordError):
            self.service.change_master_password("WrongPassword", "NewPassword456")

    def test_change_master_password_same_password(self):
        self.service.create_vault_service("MySecurePassword123")
        with self.assertRaises(ValueError):
            self.service.change_master_password("MySecurePassword123", "MySecurePassword123")

    def test_change_master_password_interrupted_reencryption(self):
        self.service.create_vault_service("MySecurePassword123")
        # To simulate interruption, we mock the update_vault_crypto_transaction to raise an exception
        with unittest.mock.patch.object(self.repository, "update_vault_crypto_transaction", side_effect=Exception("Database error")):
            with self.assertRaises(Exception):
                self.service.change_master_password("MySecurePassword123", "NewPassword456")
                
        # Verify old password still works (i.e. transaction rolled back or never committed)
        vault_service = self.service.unlock_vault("MySecurePassword123")
        self.assertIsNotNone(vault_service)


if __name__ == "__main__":
    unittest.main()
