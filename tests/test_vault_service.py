import os
import tempfile
import unittest

from database.database import DatabaseManager
from database.repository import VaultRepository
from services.vault_service import VaultService
from utils.constants import SCHEMA_VERSION


class FakeEncryptionService:
    def encrypt(self, value: str) -> str:
        return f"encrypted::{value}"

    def decrypt(self, value: str) -> str:
        return value.removeprefix("encrypted::")


class VaultServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_file = os.path.join(self.temp_dir.name, "vault.db")
        self.service = VaultService(
            VaultRepository(DatabaseManager(self.db_file)),
            FakeEncryptionService(),
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_find_credential(self):
        action = self.service.save_credential("example.com", "user@example.com", "Secret123!")
        credential = self.service.find_credential("example.com")

        self.assertEqual(action, "created")
        self.assertIsNotNone(credential)
        self.assertEqual(credential.username, "user@example.com")
        self.assertEqual(credential.password, "Secret123!")
        self.assertEqual(credential.title, "example.com")
        self.assertEqual(credential.notes, "")
        self.assertEqual(credential.category, "")
        self.assertFalse(credential.favorite)

    def test_save_updates_existing_credential(self):
        self.service.save_credential("example.com", "user@example.com", "Secret123!")
        action = self.service.save_credential("example.com", "new@example.com", "Updated456!")
        credential = self.service.find_credential("example.com")

        self.assertEqual(action, "created")
        self.assertEqual(self.service.get_total_credentials(), 2)
        self.assertEqual(credential.username, "new@example.com")
        self.assertEqual(credential.password, "Updated456!")

    def test_save_updates_existing_website_and_username_pair(self):
        self.service.save_credential("example.com", "user@example.com", "Secret123!")

        action = self.service.save_credential("example.com", "user@example.com", "Updated456!")
        credential = self.service.find_credential("example.com")

        self.assertEqual(action, "updated")
        self.assertEqual(self.service.get_total_credentials(), 1)
        self.assertEqual(credential.password, "Updated456!")

    def test_save_entry_supports_notes_category_and_favorite(self):
        entry = self.service.save_entry(
            title="Personal Gmail",
            website="gmail.com",
            username="sameer@gmail.com",
            password="Secret123!",
            notes="Recovery codes stored offline",
            category="Personal",
            tags="email, recovery",
            icon="mail",
            favorite=True,
        )

        entries = self.service.list_entries_by_website("gmail.com")

        self.assertEqual(entry.title, "Personal Gmail")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].notes, "Recovery codes stored offline")
        self.assertEqual(entries[0].category, "Personal")
        self.assertEqual(entries[0].tags, "email, recovery")
        self.assertEqual(entries[0].icon, "mail")
        self.assertTrue(entries[0].favorite)

    def test_notes_are_encrypted_and_search_normalizes_websites(self):
        entry = self.service.save_entry(
            title="Amazon Shopping",
            website="https://amazon.com",
            username="user@example.com",
            password="StrongPassword123!",
            notes="Recovery code: 1234",
            category="Shopping",
            tags="retail, orders",
        )
        stored = self.service.repository.get_entry_by_id(entry.id)

        self.assertNotEqual(stored.notes, "Recovery code: 1234")
        self.assertEqual(self.service.search_entries("AMAZON")[0].id, entry.id)
        self.assertEqual(self.service.search_entries("amazon.com")[0].id, entry.id)
        self.assertEqual(self.service.search_entries("https://amazon.com")[0].id, entry.id)

    def test_metadata_is_initialized(self):
        metadata = self.service.get_metadata()

        self.assertEqual(metadata.version, SCHEMA_VERSION)
        self.assertTrue(metadata.created)
        self.assertTrue(metadata.vault_id)


if __name__ == "__main__":
    unittest.main()
