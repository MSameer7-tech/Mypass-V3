import unittest
from unittest.mock import call, patch

from crypto.clipboard import ClipboardService


class FakeScheduler:
    def __init__(self):
        self.jobs = {}
        self.cancelled = []
        self.next_job = 0

    def after(self, _milliseconds, callback):
        self.next_job += 1
        job = f"job-{self.next_job}"
        self.jobs[job] = callback
        return job

    def after_cancel(self, job):
        self.cancelled.append(job)


class ClipboardServiceTests(unittest.TestCase):
    @patch("crypto.clipboard.pyperclip")
    def test_new_copy_cancels_old_timer_and_clears_latest_value(self, clipboard):
        scheduler = FakeScheduler()
        service = ClipboardService(clear_after_seconds=20)
        service.copy("first", scheduler=scheduler)
        service.copy("second", scheduler=scheduler)

        self.assertEqual(scheduler.cancelled, ["job-1"])
        clipboard.paste.return_value = "second"
        service.clear_if_unchanged()
        clipboard.copy.assert_any_call("")

    @patch("crypto.clipboard.pyperclip")
    def test_clipboard_is_not_cleared_after_user_replaces_it(self, clipboard):
        service = ClipboardService()
        service.copy("password")
        clipboard.paste.return_value = "different value"

        service.clear_if_unchanged()

        self.assertEqual(clipboard.copy.call_args_list, [call("password")])


if __name__ == "__main__":
    unittest.main()
