import unittest
import time
from unittest.mock import MagicMock, patch

from services.master_password_service import MasterPasswordService, InvalidMasterPasswordError

class TestAuthSecurity(unittest.TestCase):
    def setUp(self):
        self.mock_repo = MagicMock()
        self.mock_key_derivation = MagicMock()
        self.mock_encryption = MagicMock()
        
        # Setup mock metadata
        self.mock_metadata = MagicMock()
        self.mock_metadata.salt = b"test_salt"
        self.mock_metadata.argon_parameters = "test_params"
        self.mock_metadata.vault_id = "encrypted_vault_id"
        self.mock_metadata.version = "5.0"
        self.mock_repo.get_metadata.return_value = self.mock_metadata
        
        # Ensure it always raises exception to simulate wrong password
        self.mock_encryption_instance = MagicMock()
        self.mock_encryption_instance.decrypt.side_effect = Exception("Decryption failed")
        self.mock_encryption_factory = MagicMock(return_value=self.mock_encryption_instance)
        
        self.service = MasterPasswordService(
            repository=self.mock_repo,
            key_derivation_service=self.mock_key_derivation,
            encryption_service_factory=self.mock_encryption_factory
        )

    def test_rate_limiting_exponential_backoff(self):
        # We need to measure the time taken for each call
        
        # Attempt 1: No delay (fails)
        start_time = time.time()
        with self.assertRaises(InvalidMasterPasswordError):
            self.service.unlock_vault("Wrong1")
        duration_1 = time.time() - start_time
        self.assertLess(duration_1, 0.5) # Should be instant
        self.assertEqual(self.service._failed_attempts, 1)

        # Attempt 2: 1s delay
        start_time = time.time()
        with self.assertRaises(InvalidMasterPasswordError):
            self.service.unlock_vault("Wrong2")
        duration_2 = time.time() - start_time
        self.assertGreaterEqual(duration_2, 1.0)
        self.assertLess(duration_2, 1.5)
        self.assertEqual(self.service._failed_attempts, 2)

        # Attempt 3: 2s delay
        start_time = time.time()
        with self.assertRaises(InvalidMasterPasswordError):
            self.service.unlock_vault("Wrong3")
        duration_3 = time.time() - start_time
        self.assertGreaterEqual(duration_3, 2.0)
        self.assertLess(duration_3, 2.5)
        self.assertEqual(self.service._failed_attempts, 3)

        # Attempt 4: 4s delay
        start_time = time.time()
        with self.assertRaises(InvalidMasterPasswordError):
            self.service.unlock_vault("Wrong4")
        duration_4 = time.time() - start_time
        self.assertGreaterEqual(duration_4, 4.0)
        self.assertLess(duration_4, 4.5)
        self.assertEqual(self.service._failed_attempts, 4)
        
    def test_successful_auth_resets_counter(self):
        # Fail first to bump counter
        with self.assertRaises(InvalidMasterPasswordError):
            self.service.unlock_vault("Wrong1")
        self.assertEqual(self.service._failed_attempts, 1)
        
        # Next attempt will sleep 1 second. Let's mock time.sleep so we don't actually wait
        with patch('time.sleep') as mock_sleep:
            # Now simulate a correct password
            self.mock_encryption_instance.decrypt.side_effect = None
            self.mock_encryption_instance.decrypt.return_value = "decrypted_id"
            self.service.unlock_vault("CorrectPassword")
            
            # Counter should be reset
            self.assertEqual(self.service._failed_attempts, 0)
            mock_sleep.assert_called_once_with(1)

    def test_rate_limiting_cap(self):
        self.service._failed_attempts = 15
        with patch('time.sleep') as mock_sleep:
            with self.assertRaises(InvalidMasterPasswordError):
                self.service.unlock_vault("Wrong16")
            
            # Should be capped at 10 seconds
            mock_sleep.assert_called_once_with(10)
            self.assertEqual(self.service._failed_attempts, 16)

if __name__ == '__main__':
    unittest.main()
