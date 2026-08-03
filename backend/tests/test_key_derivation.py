import unittest

from crypto.encryption import AesGcmEncryptionService
from crypto.key_derivation import Argon2KeyDerivationService


class KeyDerivationTests(unittest.TestCase):
    def test_argon2_key_is_aes_256_compatible(self):
        service = Argon2KeyDerivationService()
        parameters = service.default_parameters()
        key = service.derive_key("MySecurePassword123", b"s" * parameters.salt_length, parameters)

        self.assertEqual(len(key), 32)
        encrypted = AesGcmEncryptionService(key).encrypt("vault verifier")
        self.assertEqual(AesGcmEncryptionService(key).decrypt(encrypted), "vault verifier")

    def test_legacy_fernet_key_is_urlsafe_base64_encoded(self):
        service = Argon2KeyDerivationService()
        parameters = service.default_parameters()
        key = service.derive_legacy_fernet_key(
            "MySecurePassword123", b"s" * parameters.salt_length, parameters
        )

        self.assertEqual(len(key), 44)


if __name__ == "__main__":
    unittest.main()
