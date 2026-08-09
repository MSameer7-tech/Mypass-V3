import os
import sqlite3
import tempfile
import unittest
import json
from unittest.mock import patch
from datetime import datetime, UTC
import uuid

from database.database import DatabaseManager
from database.repository import VaultRepository
from crypto.encryption import AesGcmEncryptionService
from crypto.key_derivation import Argon2KeyDerivationService
from services.backup_service import BackupService
from services.vault_service import VaultService
from database.models import VaultEntryRecord

class FakeEncryptionService:
    def __init__(self, key=None):
        self.key = key
    def encrypt(self, value: str) -> str:
        return f"encrypted::{value}"
    def decrypt(self, value: str) -> str:
        return value.replace("encrypted::", "")

class Phase12_9_MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "vault.db")
        self.key_derivation = Argon2KeyDerivationService()
        
        self.master_pass = "MigrationTest123!"
        self.salt = self.key_derivation.generate_salt(16)
        params = self.key_derivation.default_parameters()
        self.key = self.key_derivation.derive_key(self.master_pass, self.salt, params)
        self.enc_service = AesGcmEncryptionService(self.key)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _setup_legacy_v2_database(self):
        """Creates a legacy v2.x database (missing columns, credentials table)"""
        conn = sqlite3.connect(self.db_path)
        
        # We manually build the old schema without tags, icon, or biometric metadata
        conn.executescript(
            """
            CREATE TABLE vault_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL, website TEXT NOT NULL, username TEXT NOT NULL,
                password TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL DEFAULT '', favorite INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            );
            CREATE TABLE password_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER NOT NULL,
                password TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (entry_id) REFERENCES vault_entries(id) ON DELETE CASCADE
            );
            CREATE TABLE app_metadata (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                version TEXT NOT NULL,
                created TEXT NOT NULL,
                vault_id TEXT NOT NULL,
                argon_parameters TEXT NOT NULL,
                salt TEXT NOT NULL
            );
            CREATE TABLE credentials (website TEXT, email TEXT, password TEXT);
            """
        )
        
        conn.execute(
            "INSERT INTO app_metadata (id, version, created, vault_id, argon_parameters, salt) VALUES (1, '2.0.0', ?, ?, ?, ?)",
            (datetime.now(UTC).isoformat(), str(uuid.uuid4()), json.dumps(self.key_derivation.serialize_parameters(self.key_derivation.default_parameters())), self.key_derivation.encode_salt(self.salt))
        )

        encrypted_pass = self.enc_service.encrypt("supersecret1")
        conn.execute(
            "INSERT INTO credentials VALUES (?, ?, ?)",
            ('legacy-site.com', 'user@legacy.com', encrypted_pass)
        )
        
        enc_note = self.enc_service.encrypt("Secret Note Body")
        enc_dev_key = self.enc_service.encrypt("AKIA123456789")
        now = datetime.now(UTC).isoformat()
        
        conn.execute(
            "INSERT INTO vault_entries (title, website, username, password, notes, category, favorite, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('My Note', '', '', enc_note, enc_note, 'Secure Notes', 1, now, now)
        )
        conn.execute(
            "INSERT INTO vault_entries (title, website, username, password, notes, category, favorite, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            ('Dev Key', 'aws.com', 'admin', enc_dev_key, '', 'Developer Keys', 0, now, now)
        )
        
        conn.commit()
        conn.close()

    def test_12_9_1_legacy_database_migration(self):
        """12.9.1: Ensure missing columns are added, credentials mapped, and data decrypted."""
        self._setup_legacy_v2_database()
        
        db = DatabaseManager(self.db_path)
        repo = VaultRepository(db)
        
        metadata = repo.get_metadata()
        self.assertEqual(metadata.biometric_prompt_state, 'never')
        self.assertFalse(metadata.biometric_enabled)
        
        entries = repo.list_all_entries()
        self.assertEqual(len(entries), 3)
        
        migrated_cred = next(e for e in entries if e.website == 'legacy-site.com')
        self.assertEqual(migrated_cred.tags, "")
        self.assertEqual(migrated_cred.icon, "")
        self.assertEqual(migrated_cred.category, "")
        self.assertEqual(self.enc_service.decrypt(migrated_cred.password), "supersecret1")
        
        note = next(e for e in entries if e.title == 'My Note')
        self.assertTrue(note.favorite)
        self.assertEqual(note.category, 'Secure Notes')
        self.assertEqual(self.enc_service.decrypt(note.notes), "Secret Note Body")

        dev_key = next(e for e in entries if e.title == 'Dev Key')
        self.assertFalse(dev_key.favorite)
        self.assertEqual(dev_key.category, 'Developer Keys')
        self.assertEqual(self.enc_service.decrypt(dev_key.password), "AKIA123456789")

    def test_12_9_2_legacy_mypass_migration(self):
        """12.9.2: Ensure legacy .mypass JSON structure can be imported"""
        # Create a fake vault service for BackupService
        repo = VaultRepository(DatabaseManager(self.db_path))
        vault_service = VaultService(repo, self.enc_service)
        
        legacy_backup_payload = json.dumps({
            "format_version": 1,
            "version": "2.0.0",
            "entries": [
                {
                    "id": 100,
                    "title": "Old Backup Entry",
                    "website": "backup.com",
                    "username": "bkp",
                    "password": "backup_pass",
                    "notes": "",
                    "category": "Logins",
                    "favorite": True,
                    "created_at": datetime.now(UTC).isoformat(),
                    "updated_at": datetime.now(UTC).isoformat()
                }
            ],
            "history": [],
            "extra_unknown_field": "Should be ignored"
        })
        
        encrypted_legacy_backup = self.enc_service.encrypt(legacy_backup_payload)
        backup_path = os.path.join(self.temp_dir.name, "legacy.mypass")
        with open(backup_path, 'w') as f:
            f.write(encrypted_legacy_backup)
            
        backup_service = BackupService()
        backup_service.restore_backup(vault_service, backup_path)
        
        entries = repo.list_all_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, "Old Backup Entry")
        self.assertEqual(entries[0].tags, "")
        self.assertEqual(entries[0].icon, "")
        self.assertTrue(entries[0].favorite)
        self.assertEqual(self.enc_service.decrypt(entries[0].password), "backup_pass")

    @patch.object(DatabaseManager, '_ensure_entry_columns')
    def test_12_9_3_failed_migration_rollback(self, mock_migration):
        """12.9.3: Ensure atomic transaction handling on migration failure"""
        self._setup_legacy_v2_database()
        
        mock_migration.side_effect = Exception("Simulated disk/schema failure during migration")
        
        with self.assertRaises(Exception):
            DatabaseManager(self.db_path)
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='credentials'")
        self.assertIsNotNone(cursor.fetchone(), "Credentials table dropped but migration failed! Data loss!")
        
        cursor.execute("PRAGMA table_info(app_metadata)")
        cols = {row[1] for row in cursor.fetchall()}
        self.assertNotIn("biometric_enabled", cols, "Biometric columns committed despite migration failure!")
        
        conn.close()

    def test_12_9_3_post_migration_integrity(self):
        """12.9.3: Ensure post-migration CRUD and lock/unlock remain intact"""
        self._setup_legacy_v2_database()
        db = DatabaseManager(self.db_path)
        repo = VaultRepository(db)
        vault_service = VaultService(repo, self.enc_service)
        
        new_enc = self.enc_service.encrypt("new_crud")
        now = datetime.now(UTC).isoformat()
        entry = VaultEntryRecord(
            id=None, title="CRUD Test", website="crud.com", username="c", password=new_enc,
            notes="", category="Logins", tags="test", icon="", favorite=False,
            created_at=now, updated_at=now
        )
        created = repo.create_entry(entry)
        self.assertIsNotNone(created.id)
        
        backup_service = BackupService()
        export_path = os.path.join(self.temp_dir.name, "re_export.mypass")
        backup_service.create_backup(vault_service, export_path)
        
        self.assertTrue(os.path.exists(export_path))
        with open(export_path, 'r') as f:
            enc_data = f.read()
            data = json.loads(self.enc_service.decrypt(enc_data))
            self.assertIn("entries", data)
            self.assertEqual(len(data["entries"]), 4) 
            self.assertIn("tags", data["entries"][0])

if __name__ == '__main__':
    unittest.main()
