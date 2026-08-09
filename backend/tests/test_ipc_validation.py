import unittest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ipc_bridge import validate_entry_payload

class TestIPCValidation(unittest.TestCase):
    def test_valid_payload(self):
        payload = {
            "title": "My Bank",
            "username": "user",
            "password": "pwd",
            "website_url": "https://bank.com",
            "favorite": True
        }
        # Should not raise
        validate_entry_payload(payload)

    def test_title_too_long(self):
        payload = {"title": "A" * 101}
        with self.assertRaises(ValueError) as context:
            validate_entry_payload(payload)
        self.assertEqual(str(context.exception), "Invalid title")

    def test_empty_title(self):
        payload = {"title": ""}
        with self.assertRaises(ValueError):
            validate_entry_payload(payload)

    def test_invalid_title_type(self):
        payload = {"title": 123}
        with self.assertRaises(ValueError):
            validate_entry_payload(payload)

    def test_invalid_favorite_type(self):
        payload = {"title": "Valid", "favorite": "yes"}
        with self.assertRaises(ValueError):
            validate_entry_payload(payload)

    def test_notes_too_long(self):
        payload = {"title": "Valid", "notes": "A" * 5001}
        with self.assertRaises(ValueError):
            validate_entry_payload(payload)

if __name__ == '__main__':
    unittest.main()
