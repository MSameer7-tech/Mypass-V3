import os
import tempfile
import unittest
import base64

from database.database import DatabaseManager
from database.repository import VaultRepository
from services.backup_service import BackupService
from services.import_service import ImportService
from services.vault_service import VaultService


class FakeEncryptionService:
    def encrypt(self, value: str) -> str:
        return "encrypted::" + base64.b64encode(value.encode()).decode()

    def decrypt(self, value: str) -> str:
        if not value.startswith("encrypted::"):
            raise ValueError("invalid encrypted payload")
        return base64.b64decode(value.removeprefix("encrypted::")).decode()


class BackupAndImportTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.service = VaultService(
            VaultRepository(DatabaseManager(os.path.join(self.temp_dir.name, "vault.db"))),
            FakeEncryptionService(),
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_password_changes_are_kept_in_history_and_can_be_restored(self):
        entry = self.service.save_entry("Email", "mail.test", "user", "Original123!")
        updated = self.service.save_entry(
            "Email", "mail.test", "user", "Updated456!", entry_id=entry.id
        )
        history = self.service.get_password_history(entry.id)

        self.assertEqual([item.password for item in history], ["Original123!"])
        restored = self.service.restore_password_from_history(entry.id, history[0].id)
        self.assertEqual(restored.password, "Original123!")
        self.assertEqual(len(self.service.get_password_history(entry.id)), 2)
        self.assertEqual(updated.id, entry.id)

    def test_backup_is_encrypted_and_restores_entries_and_history(self):
        entry = self.service.save_entry("WiFi", "network", "router", "FirstPassword123!")
        self.service.save_entry("WiFi", "network", "router", "SecondPassword123!", entry_id=entry.id)
        backup_path = os.path.join(self.temp_dir.name, "vault.backup")

        BackupService().create_backup(self.service, backup_path)
        with open(backup_path, encoding="utf-8") as file_handle:
            self.assertNotIn("SecondPassword123!", file_handle.read())

        self.service.replace_vault_contents([], [])
        BackupService().restore_backup(self.service, backup_path)
        restored = self.service.search_entries("network")[0]
        self.assertEqual(restored.password, "SecondPassword123!")
        self.assertEqual(self.service.get_password_history(restored.id)[0].password, "FirstPassword123!")

    def test_chrome_and_bitwarden_csv_imports_are_mapped(self):
        chrome_path = os.path.join(self.temp_dir.name, "chrome.csv")
        with open(chrome_path, "w", encoding="utf-8") as file_handle:
            file_handle.write("name,url,username,password,note\nChrome,https://example.com,user,Secret123!,note\n")
        bitwarden_path = os.path.join(self.temp_dir.name, "bitwarden.csv")
        with open(bitwarden_path, "w", encoding="utf-8") as file_handle:
            file_handle.write(
                "folder,favorite,type,name,notes,login_uri,login_username,login_password\n"
                "Work,true,login,Bitwarden,private note,https://work.test,admin,Strong456!\n"
            )

        importer = ImportService()
        self.assertEqual(importer.import_csv(self.service, chrome_path, "Chrome"), 1)
        self.assertEqual(importer.import_csv(self.service, bitwarden_path, "Bitwarden"), 1)
        imported = self.service.search_entries("work.test")[0]
        self.assertEqual(imported.category, "Work")
        self.assertTrue(imported.favorite)
        self.assertEqual(imported.notes, "private note")


if __name__ == "__main__":
    unittest.main()
