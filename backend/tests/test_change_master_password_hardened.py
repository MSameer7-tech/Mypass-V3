import os
import unittest
import uuid
import tempfile
import json
import sqlite3
from unittest.mock import MagicMock, patch

from database.database import DatabaseManager
from database.repository import VaultRepository
from services.master_password_service import MasterPasswordService, InvalidMasterPasswordError
from services.vault_service import VaultService
from services.authentication_service import AuthenticationService


class TestChangeMasterPasswordHardened(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.test_dir.name, "test_vault.db")
        self.db_manager = DatabaseManager(self.db_path)
        self.repository = VaultRepository(self.db_manager)
        self.master_pwd_service = MasterPasswordService(self.repository)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_happy_path_rotation_with_diverse_data(self):
        # 1. Initialize vault
        pwd_a = "OriginalPassword123!"
        pwd_b = "NewSecurePassword456$"
        vs = self.master_pwd_service.create_vault_service(pwd_a)

        # 2. Add diverse entries
        e1 = vs.save_entry(
            title="Personal Email",
            website="https://mail.google.com",
            username="sameer@example.com",
            password="InitialEmailPassword1!",
            notes="Secret notes with unicode: 🚀 🔐 and symbols: @#$%^&*()",
            category="Email",
            favorite=True,
        )
        # Update password to create password history
        vs.save_entry(
            entry_id=e1.id,
            title="Personal Email",
            website="https://mail.google.com",
            username="sameer@example.com",
            password="SecondEmailPassword2@",
            notes="Updated secret notes",
            category="Email",
            favorite=True,
        )

        e2 = vs.save_entry(
            title="Zero Notes Account",
            website="https://example.org",
            username="testuser",
            password="ComplexPassword99#",
            notes="",
            category="Work",
            favorite=False,
        )

        # 3. Rotate Master Password
        new_vs = self.master_pwd_service.change_master_password(pwd_a, pwd_b)
        self.assertIsInstance(new_vs, VaultService)

        # 4. Verify old master password no longer works
        with self.assertRaises(InvalidMasterPasswordError):
            self.master_pwd_service.unlock_vault(pwd_a)

        # 5. Verify new master password unlocks cleanly
        unlocked_vs = self.master_pwd_service.unlock_vault(pwd_b)
        self.assertIsNotNone(unlocked_vs)

        # 6. Verify full data integrity of entries and history
        entries = unlocked_vs.list_all_entries()
        self.assertEqual(len(entries), 2)

        entry1_unlocked = unlocked_vs.get_entry(e1.id)
        self.assertEqual(entry1_unlocked.title, "Personal Email")
        self.assertEqual(entry1_unlocked.username, "sameer@example.com")
        self.assertEqual(entry1_unlocked.password, "SecondEmailPassword2@")
        self.assertEqual(entry1_unlocked.notes, "Updated secret notes")
        self.assertEqual(entry1_unlocked.category, "Email")
        self.assertTrue(entry1_unlocked.favorite)

        # Verify history decrypted with new key
        history = unlocked_vs.get_password_history(e1.id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].password, "InitialEmailPassword1!")

        entry2_unlocked = unlocked_vs.get_entry(e2.id)
        self.assertEqual(entry2_unlocked.title, "Zero Notes Account")
        self.assertEqual(entry2_unlocked.password, "ComplexPassword99#")
        self.assertEqual(entry2_unlocked.notes, "")

    def test_zero_entries_vault_rotation(self):
        pwd_a = "InitialPassword123!"
        pwd_b = "RotatedPassword456!"
        self.master_pwd_service.create_vault_service(pwd_a)

        # Empty vault rotation
        self.master_pwd_service.change_master_password(pwd_a, pwd_b)

        with self.assertRaises(InvalidMasterPasswordError):
            self.master_pwd_service.unlock_vault(pwd_a)

        unlocked = self.master_pwd_service.unlock_vault(pwd_b)
        self.assertEqual(len(unlocked.list_all_entries()), 0)

    def test_validation_rules(self):
        pwd_a = "InitialPassword123!"
        self.master_pwd_service.create_vault_service(pwd_a)

        # Same password
        with self.assertRaises(ValueError) as ctx:
            self.master_pwd_service.change_master_password(pwd_a, pwd_a)
        self.assertIn("different", str(ctx.exception))

        # Short new password
        with self.assertRaises(ValueError) as ctx:
            self.master_pwd_service.change_master_password(pwd_a, "short")
        self.assertIn("at least 8 characters", str(ctx.exception))

        # Wrong current password
        with self.assertRaises(InvalidMasterPasswordError):
            self.master_pwd_service.change_master_password("WrongCurrentPwd123!", "ValidNewPassword456!")

    def test_biometric_reset_and_os_cleanup(self):
        pwd_a = "InitialPassword123!"
        pwd_b = "RotatedPassword456!"
        vs = self.master_pwd_service.create_vault_service(pwd_a)

        # Simulate biometric enrollment
        mock_auth_service = MagicMock()
        self.repository.update_biometric_metadata(
            enabled=True,
            platform="TestPlatform",
            enrolled_at=1234567.0,
            wrapped_key=json.dumps({"nonce": "abc", "ciphertext": "xyz"}),
        )

        meta_before = self.repository.get_metadata()
        self.assertTrue(meta_before.biometric_enabled)
        self.assertIsNotNone(meta_before.biometric_wrapped_key)

        # Rotate password with auth_service attached
        self.master_pwd_service.change_master_password(pwd_a, pwd_b, auth_service=mock_auth_service)

        # Verify biometric metadata reset in DB
        meta_after = self.repository.get_metadata()
        self.assertFalse(meta_after.biometric_enabled)
        self.assertIsNone(meta_after.biometric_wrapped_key)
        self.assertIsNone(meta_after.biometric_platform)

        # Verify OS secret deletion was called
        mock_auth_service.delete_secret.assert_called_once()

    def test_pre_validation_guarantees_zero_writes_on_corruption(self):
        pwd_a = "InitialPassword123!"
        pwd_b = "RotatedPassword456!"
        vs = self.master_pwd_service.create_vault_service(pwd_a)

        e = vs.save_entry(
            title="Corrupted Entry Test",
            website="https://test.com",
            username="user",
            password="Password123!",
            notes="Notes",
        )

        meta_before = self.repository.get_metadata()

        # Manually corrupt the encrypted password field in the database
        with self.db_manager.connect() as conn:
            conn.execute("UPDATE vault_entries SET password = '{\"nonce\":\"bad\",\"ciphertext\":\"bad\"}' WHERE id = ?", (e.id,))

        # Attempt rotation -> must fail during pre-validation before any new metadata is written
        with self.assertRaises(Exception):
            self.master_pwd_service.change_master_password(pwd_a, pwd_b)

        meta_after = self.repository.get_metadata()
        # Verify metadata (salt, argon parameters, vault_id) was NEVER modified
        self.assertEqual(meta_before.salt, meta_after.salt)
        self.assertEqual(meta_before.vault_id, meta_after.vault_id)

    def test_transaction_rollback_on_database_failure(self):
        pwd_a = "InitialPassword123!"
        pwd_b = "RotatedPassword456!"
        vs = self.master_pwd_service.create_vault_service(pwd_a)

        vs.save_entry(
            title="Rollback Test",
            website="https://test.com",
            username="user",
            password="SecretPassword123!",
            notes="Pre-rollback notes",
        )

        meta_before = self.repository.get_metadata()

        # Patch update_vault_crypto_transaction to raise an exception mid-transaction
        with patch.object(self.repository, "update_vault_crypto_transaction", side_effect=sqlite3.OperationalError("Simulated DB Disk Full")):
            with self.assertRaises(sqlite3.OperationalError):
                self.master_pwd_service.change_master_password(pwd_a, pwd_b)

        # Verify old password still works and metadata is unchanged
        meta_after = self.repository.get_metadata()
        self.assertEqual(meta_before.salt, meta_after.salt)
        self.assertEqual(meta_before.vault_id, meta_after.vault_id)

        unlocked = self.master_pwd_service.unlock_vault(pwd_a)
        self.assertIsNotNone(unlocked)
        self.assertEqual(len(unlocked.list_all_entries()), 1)
        self.assertEqual(unlocked.list_all_entries()[0].password, "SecretPassword123!")


if __name__ == "__main__":
    unittest.main()
