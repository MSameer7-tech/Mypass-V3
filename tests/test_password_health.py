import unittest
from datetime import UTC, datetime, timedelta

from database.models import VaultEntryRecord
from services.password_health import PasswordHealthService


class PasswordHealthServiceTests(unittest.TestCase):
    def entry(self, password: str, updated_at: str) -> VaultEntryRecord:
        return VaultEntryRecord(
            id=1,
            title="Example",
            website="example.com",
            username="user",
            password=password,
            notes="",
            category="Work",
            tags="",
            icon="",
            favorite=False,
            created_at=updated_at,
            updated_at=updated_at,
        )

    def test_health_counts_weak_duplicate_and_old_passwords(self):
        old_date = (datetime.now(UTC) - timedelta(days=91)).isoformat()
        recent_date = datetime.now(UTC).isoformat()
        report = PasswordHealthService().analyze(
            [
                self.entry("weak", old_date),
                self.entry("weak", recent_date),
                self.entry("StrongPassword123!", recent_date),
            ]
        )

        self.assertEqual(report.weak_passwords, 2)
        self.assertEqual(report.duplicate_passwords, 1)
        self.assertEqual(report.reused_passwords, 1)
        self.assertEqual(report.old_passwords, 1)
        self.assertLess(report.score, 100)


if __name__ == "__main__":
    unittest.main()
