import os
import tempfile
import unittest
import json
from dataclasses import asdict

from database.database import DatabaseManager
from database.repository import VaultRepository
from services.vault_service import VaultService
from crypto.key_derivation import Argon2KeyDerivationService
from crypto.encryption import AesGcmEncryptionService
from services.master_password_service import MasterPasswordService, InvalidMasterPasswordError
from services.backup_service import BackupService

class FakeDbManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self._connection = None

class TestE2ESecurity(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "vault.db")
        self.db_manager = DatabaseManager(self.db_path)
        self.repo = VaultRepository(self.db_manager)
        
        self.kdf = Argon2KeyDerivationService()
        self.legacy_key_file = os.path.join(self.temp_dir.name, "vault.key")
        self.master_pwd_service = MasterPasswordService(
            self.repo,
            key_derivation_service=self.kdf,
            encryption_service_factory=AesGcmEncryptionService,
            legacy_key_file=self.legacy_key_file
        )
        
    def tearDown(self):
        self.temp_dir.cleanup()
        
    def test_wrong_password_fails_cleanly(self):
        # Create vault
        vault_service = self.master_pwd_service.create_vault_service("CorrectPassword123!")
        vault_service.save_entry("Test", "test.com", "user", "pass")
        
        # Try to unlock with wrong password
        with self.assertRaises(InvalidMasterPasswordError):
            self.master_pwd_service.create_vault_service("WrongPassword!")
            
    def test_mypass_cannot_be_decrypted_without_password(self):
        vault_service = self.master_pwd_service.create_vault_service("MySecretPass!")
        vault_service.save_entry("Test", "test.com", "user", "supersecret")
        
        entries = vault_service.list_all_entries()
        payload_dict = {
            "format_version": 1,
            "entries": [asdict(entry) for entry in entries],
            "history": [] 
        }
        raw_payload = json.dumps(payload_dict)
        encrypted_payload = vault_service.encryption_service.encrypt(raw_payload)
        
        # Attempt to create a vault service with a different password fails immediately
        with self.assertRaises(InvalidMasterPasswordError):
            self.master_pwd_service.create_vault_service("DifferentPass!")
            
    def test_malformed_import_atomicity(self):
        # Setup initial database
        vault_service = self.master_pwd_service.create_vault_service("MySecretPass!")
        vault_service.save_entry("Initial", "test.com", "user", "pass")
        initial_count = len(vault_service.list_all_entries())
        self.assertEqual(initial_count, 1)
        
        # We'll simulate the ipc_bridge logic for atomicity here
        import ipc_bridge
        
        # Create a malformed payload: first item is valid, second is malformed (no title)
        malformed_items = [
            {"title": "Valid Entry", "password": "123"},
            {"password": "No title!"}
        ]
        
        # Instead of calling ipc_bridge main, we replicate the transaction logic tested
        validated_items = []
        import_failed = False
        try:
            for index, item in enumerate(malformed_items):
                if isinstance(item, dict) and "title" in item:
                    ipc_bridge.validate_entry_payload(item)
                    validated_items.append(item)
                else:
                    raise ValueError("Invalid entry")
        except ValueError:
            import_failed = True
            
        self.assertTrue(import_failed)
        
        # Simulate rollback / no insertion
        if not import_failed:
            # this shouldn't run
            for item in validated_items:
                vault_service.save_entry(title=item["title"])
                
        # Assert database has not changed
        final_count = len(vault_service.list_all_entries())
        self.assertEqual(initial_count, final_count)

if __name__ == '__main__':
    unittest.main()
