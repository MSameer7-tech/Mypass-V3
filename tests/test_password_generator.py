import unittest

from services.password_generator import PasswordGenerator


class PasswordGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.generator = PasswordGenerator()

    def test_generate_password_contains_expected_character_types(self):
        password = self.generator.generate()

        self.assertEqual(len(password), 14)
        self.assertTrue(any(character.isalpha() for character in password))
        self.assertTrue(any(character.isdigit() for character in password))
        self.assertTrue(any(character in self.generator.symbols for character in password))

    def test_strength_evaluation_for_strong_password(self):
        strength = self.generator.evaluate_strength("Str0ng!Pass123")

        self.assertEqual(strength.label, "Strong Password")
        self.assertGreaterEqual(strength.progress, 0.8)


if __name__ == "__main__":
    unittest.main()
