import unittest

from services.session_lock import SessionLockService


class SessionLockServiceTests(unittest.TestCase):
    def setUp(self):
        self.now = 100.0
        self.service = SessionLockService(timeout_seconds=300, clock=lambda: self.now)

    def test_session_locks_after_configured_inactivity(self):
        self.service.unlock()
        self.now += 299
        self.assertFalse(self.service.should_lock())
        self.now += 1
        self.assertTrue(self.service.should_lock())

    def test_manual_lock_and_timeout_change(self):
        self.service.unlock()
        self.service.set_timeout(60)
        self.now += 60
        self.assertTrue(self.service.should_lock())
        self.service.lock()
        self.assertTrue(self.service.is_locked)


if __name__ == "__main__":
    unittest.main()
