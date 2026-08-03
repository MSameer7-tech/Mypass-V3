try:
    import pyperclip
except ModuleNotFoundError:  # Allows the non-UI test suite to run before dependencies are installed.
    pyperclip = None


class ClipboardService:
    def __init__(self, clear_after_seconds: int = 20):
        self.clear_after_seconds = clear_after_seconds
        self._clear_job = None
        self._scheduler = None
        self._copied_value: str | None = None

    def copy(self, value: str, *, scheduler=None) -> None:
        self._require_pyperclip()
        self._cancel_pending_clear()
        pyperclip.copy(value)
        self._copied_value = value
        self._scheduler = scheduler
        if scheduler is not None:
            self._clear_job = scheduler.after(
                self.clear_after_seconds * 1000,
                self.clear_if_unchanged,
            )

    def clear_if_unchanged(self) -> None:
        self._clear_job = None
        if self._copied_value is None:
            return
        self._require_pyperclip()
        try:
            if pyperclip.paste() == self._copied_value:
                pyperclip.copy("")
        finally:
            self._copied_value = None

    def clear_now(self) -> None:
        self._cancel_pending_clear()
        self.clear_if_unchanged()

    def _cancel_pending_clear(self) -> None:
        if self._clear_job is not None and self._scheduler is not None:
            self._scheduler.after_cancel(self._clear_job)
        self._clear_job = None

    @staticmethod
    def _require_pyperclip() -> None:
        if pyperclip is None:
            raise RuntimeError("Clipboard support requires the pyperclip package.")
