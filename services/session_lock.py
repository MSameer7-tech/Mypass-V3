import time


class SessionLockService:
    def __init__(self, timeout_seconds: int = 300, clock=time.monotonic):
        self.clock = clock
        self.timeout_seconds = timeout_seconds
        self._last_activity: float | None = None
        self._locked = True

    def unlock(self) -> None:
        self._locked = False
        self.record_activity()

    def lock(self) -> None:
        self._locked = True
        self._last_activity = None

    def record_activity(self) -> None:
        if not self._locked:
            self._last_activity = self.clock()

    def set_timeout(self, timeout_seconds: int) -> None:
        if timeout_seconds < 1:
            raise ValueError("Auto-lock timeout must be at least one second.")
        self.timeout_seconds = timeout_seconds
        self.record_activity()

    def should_lock(self) -> bool:
        if self._locked or self._last_activity is None:
            return False
        return self.clock() - self._last_activity >= self.timeout_seconds

    @property
    def is_locked(self) -> bool:
        return self._locked
