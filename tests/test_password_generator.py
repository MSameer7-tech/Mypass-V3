import unittest

from services.password_generator import PasswordGenerator, PasswordGeneratorOptions


class PasswordGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.generator = PasswordGenerator()

    def test_generate_password_contains_expected_character_types(self):
        password = self.generator.generate(
            PasswordGeneratorOptions(length=14, exclude_similar=True, avoid_ambiguous=True)
        )

        self.assertEqual(len(password), 14)
        self.assertTrue(any(character.isupper() for character in password))
        self.assertTrue(any(character.islower() for character in password))
        self.assertTrue(any(character.isdigit() for character in password))
        self.assertTrue(any(character in self.generator.symbols for character in password))
        self.assertFalse(any(character in self.generator.similar_characters for character in password))
        self.assertFalse(any(character in self.generator.ambiguous_characters for character in password))

    def test_generate_rejects_too_short_length_for_selected_groups(self):
        with self.assertRaises(ValueError):
            self.generator.generate(PasswordGeneratorOptions(length=3))

    def test_strength_evaluation_for_strong_password(self):
        strength = self.generator.evaluate_strength("Str0ng!Pass123")

        self.assertEqual(strength.label, "Strong Password")
        self.assertGreaterEqual(strength.progress, 0.8)


if __name__ == "__main__":
    unittest.main()
