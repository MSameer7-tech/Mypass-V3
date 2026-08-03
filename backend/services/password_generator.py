import secrets
import string
from dataclasses import dataclass


@dataclass(frozen=True)
class PasswordStrength:
    label: str
    tone: str
    progress: float


@dataclass(frozen=True)
class PasswordGeneratorOptions:
    length: int = 16
    uppercase: bool = True
    lowercase: bool = True
    numbers: bool = True
    symbols: bool = True
    exclude_similar: bool = False
    avoid_ambiguous: bool = False


class PasswordGenerator:
    def __init__(self):
        self.uppercase = string.ascii_uppercase
        self.lowercase = string.ascii_lowercase
        self.numbers = string.digits
        self.symbols = "!#$%&()*+-=?@^_"
        self.similar_characters = "il1Lo0O"
        self.ambiguous_characters = "{}[]()/\\'\"`~,;:.<>"

    def generate(self, options: PasswordGeneratorOptions | None = None) -> str:
        options = options or PasswordGeneratorOptions()
        character_groups = self._character_groups(options)
        if not character_groups:
            raise ValueError("Select at least one character type.")
        if options.length < len(character_groups):
            raise ValueError("Password length is too short for the selected character types.")

        allowed_characters = "".join(character_groups)
        password_characters = [secrets.choice(group) for group in character_groups]
        password_characters.extend(
            secrets.choice(allowed_characters)
            for _ in range(options.length - len(password_characters))
        )
        secrets.SystemRandom().shuffle(password_characters)
        return "".join(password_characters)

    def _character_groups(self, options: PasswordGeneratorOptions) -> list[str]:
        groups = []
        for enabled, characters in (
            (options.uppercase, self.uppercase),
            (options.lowercase, self.lowercase),
            (options.numbers, self.numbers),
            (options.symbols, self.symbols),
        ):
            if not enabled:
                continue
            filtered = characters
            if options.exclude_similar:
                filtered = "".join(
                    character for character in filtered if character not in self.similar_characters
                )
            if options.avoid_ambiguous:
                filtered = "".join(
                    character for character in filtered if character not in self.ambiguous_characters
                )
            if filtered:
                groups.append(filtered)
        return groups

    def evaluate_strength(self, password: str) -> PasswordStrength:
        if not password:
            return PasswordStrength(label="", tone="empty", progress=0.0)

        score = 0
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if any(character.isupper() for character in password):
            score += 1
        if any(character.islower() for character in password):
            score += 1
        if any(character.isdigit() for character in password):
            score += 1
        if any(character in string.punctuation for character in password):
            score += 1

        progress = min(score / 6.0, 1.0)
        if progress < 0.4:
            return PasswordStrength("Weak Password", "weak", progress)
        if progress < 0.8:
            return PasswordStrength("Medium Password", "medium", progress)
        return PasswordStrength("Strong Password", "strong", progress)
