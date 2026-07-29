import os
import sqlite3
import tempfile
import unittest

from database.database import DatabaseManager
from database.repository import VaultRepository


class DatabaseMigrationTests(unittest.TestCase):
    def test_existing_vault_table_gains_tags_and_icon_columns_before_legacy_import(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_file = os.path.join(temp_dir, "vault.db")
            connection = sqlite3.connect(db_file)
            connection.executescript(
                """
                CREATE TABLE vault_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL, website TEXT NOT NULL, username TEXT NOT NULL,
                    password TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '',
                    category TEXT NOT NULL DEFAULT '', favorite INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE credentials (website TEXT, email TEXT, password TEXT);
                INSERT INTO credentials VALUES ('amazon.com', 'user@example.com', 'ciphertext');
                """
            )
            connection.commit()
            connection.close()

            repository = VaultRepository(DatabaseManager(db_file))
            migrated = repository.list_all_entries()

            self.assertEqual(len(migrated), 1)
            self.assertEqual(migrated[0].tags, "")
            self.assertEqual(migrated[0].icon, "")


if __name__ == "__main__":
    unittest.main()
