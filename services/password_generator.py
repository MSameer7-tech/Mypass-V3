import secrets
import string
from dataclasses import dataclass


@dataclass(frozen=True)
class PasswordStrength:
    label: str
    tone: str
    progress: float


class PasswordGenerator:
    def __init__(self):
        self.letters = string.ascii_letters
        self.numbers = string.digits
        self.symbols = "!#$%&()*+"

    def generate(self) -> str:
        password_characters = (
            [secrets.choice(self.letters) for _ in range(8)]
            + [secrets.choice(self.numbers) for _ in range(3)]
            + [secrets.choice(self.symbols) for _ in range(3)]
        )
        secrets.SystemRandom().shuffle(password_characters)
        return "".join(password_characters)

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
