from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

class SessionState(Enum):
    BOOTING = auto()
    NO_VAULT = auto()
    LOCKED = auto()
    UNLOCKING = auto()
    UNLOCKED = auto()
    LOCKING = auto()
    ERROR = auto()

class LockReason(Enum):
    USER_REQUEST = auto()
    IDLE_TIMEOUT = auto()
    APP_BACKGROUND = auto()
    SYSTEM_SLEEP = auto()
    FAILED_AUTH = auto()
    NONE = auto() # Not locked

@dataclass
class SessionContext:
    """
    Immutable representation of the current application session.
    A new instance is emitted whenever the session state changes.
    """
    state: SessionState = SessionState.BOOTING
    vault_path: Optional[str] = None
    vault_id: Optional[str] = None
    last_activity: datetime = field(default_factory=datetime.now)
    lock_reason: LockReason = LockReason.NONE
    biometric_available: bool = False
    user_display_name: str = "User"
