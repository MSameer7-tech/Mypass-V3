from enum import Enum, auto

class ThemeMode(Enum):
    LIGHT = auto()
    DARK = auto()

class ButtonState(Enum):
    NORMAL = auto()
    HOVER = auto()
    PRESSED = auto()
    DISABLED = auto()

class InputState(Enum):
    NORMAL = auto()
    HOVER = auto()
    FOCUS = auto()
    DISABLED = auto()
    ERROR = auto()

class BadgeVariant(Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    PRIMARY = "primary"
    NEUTRAL = "neutral"
