from enum import Enum, auto

class VaultActions(Enum):
    NEW_PASSWORD = auto()
    DELETE = auto()
    EDIT = auto()
    SYNC = auto()
    COPY_USERNAME = auto()
    COPY_PASSWORD = auto()
    GENERATE_PASSWORD = auto()
    COPY_TOTP = auto()
    TOGGLE_FAVORITE = auto()
