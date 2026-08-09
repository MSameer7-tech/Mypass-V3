import unittest
import sqlite3
import os
import shutil
from utils.helpers import build_data_path

# Add backend to path
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import DatabaseManager
from database.repository import VaultRepository
from services.master_password_service import MasterPasswordService
from services.vault_service import VaultService

class TestSqliteEncryption(unittest.TestCase):
    def setUp(self):
        self.db_dir = build_data_path(".mypass_test_data")
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_file = os.path.join(self.db_dir, "mypass.db")
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

        self.db_manager = DatabaseManager(self.db_file)
        self.repo = VaultRepository(self.db_manager)
        self.master_pwd_service = MasterPasswordService(self.repo)
        
    def tearDown(self):
        if os.path.exists(self.db_dir):
            shutil.rmtree(self.db_dir)

    def test_raw_sqlite_does_not_contain_plaintext(self):
        # 1. Create vault with known password
        vault_service = self.master_pwd_service.create_vault_service("MyTestMasterPwd")
        
        # 2. Add an entry with a deliberately recognizable test password
        secret_password = "SUPER_SECRET_PLAINTEXT_12345"
        secret_notes = "THESE_ARE_MY_SECRET_NOTES"
        
        vault_service.save_entry(
            title="My Bank",
            website="https://bank.com",
            username="user",
            password=secret_password,
            notes=secret_notes,
            category="Passwords",
            favorite=False
        )
        
        # 3. Open the SQLite database as raw bytes/text
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password, notes FROM vault_entries LIMIT 1")
            row = cursor.fetchone()
            
            raw_password, raw_notes = row
            
            # 4. Assert that the known plaintext password is not present
            self.assertNotIn(secret_password, raw_password)
            self.assertNotEqual(secret_password, raw_password)
            
            self.assertNotIn(secret_notes, raw_notes)
            self.assertNotEqual(secret_notes, raw_notes)

        # 5. Verify the original password can still be decrypted correctly
        unlocked_vault_service = self.master_pwd_service.unlock_vault("MyTestMasterPwd")
        entries = unlocked_vault_service.list_all_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].password, secret_password)
        self.assertEqual(entries[0].notes, secret_notes)

        # 6. Verify incorrect master passwords cannot decrypt it
        with self.assertRaises(Exception):
            self.master_pwd_service.unlock_vault("WrongPassword")

if __name__ == '__main__':
    unittest.main()
