from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from database.models import VaultEntryRecord
from utils.constants import PASSWORD_AGE_DAYS


@dataclass(frozen=True)
class PasswordHealthReport:
    score: int
    weak_passwords: int
    duplicate_passwords: int
    old_passwords: int
    reused_passwords: int


class PasswordHealthService:
    def analyze(self, entries: list[VaultEntryRecord]) -> PasswordHealthReport:
        password_counts = Counter(entry.password for entry in entries if entry.password)
        duplicate_passwords = sum(count - 1 for count in password_counts.values() if count > 1)
        weak_passwords = sum(self._is_weak(entry.password) for entry in entries)
        old_passwords = sum(self._is_old(entry.updated_at) for entry in entries)
        score = max(0, 100 - weak_passwords * 12 - duplicate_passwords * 15 - old_passwords * 3)
        return PasswordHealthReport(
            score=score,
            weak_passwords=weak_passwords,
            duplicate_passwords=duplicate_passwords,
            old_passwords=old_passwords,
            reused_passwords=duplicate_passwords,
        )

    def _is_weak(self, password: str) -> bool:
        return (
            len(password) < 12
            or not any(character.isupper() for character in password)
            or not any(character.islower() for character in password)
            or not any(character.isdigit() for character in password)
            or not any(not character.isalnum() for character in password)
        )

    def _is_old(self, updated_at: str) -> bool:
        try:
            updated = datetime.fromisoformat(updated_at).astimezone(UTC)
        except (TypeError, ValueError):
            return False
        return updated < datetime.now(UTC) - timedelta(days=PASSWORD_AGE_DAYS)
