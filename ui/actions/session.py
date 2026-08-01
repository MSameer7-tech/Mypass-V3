from enum import Enum, auto

class SessionActions(Enum):
    LOCK = auto()
    UNLOCK = auto()
    LOGOUT = auto()
