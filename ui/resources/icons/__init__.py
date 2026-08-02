"""
Semantic Icon Registry for MyPass.
No UI component may use string literals or SVG filenames directly.
Always reference icons via Icons.<IDENTIFIER>.
"""

class Icons:
    # Actions
    COPY = "actions/copy.svg"
    EYE = "actions/eye.svg"
    EYE_OFF = "actions/eye-off.svg"
    NEW = "actions/plus.svg"
    EDIT = "actions/edit.svg"
    STAR = "navigation/star.svg"
    STAR_FILLED = "actions/star-filled.svg"
    ZAP = "actions/zap.svg"
    
    # Navigation
    KEY = "navigation/key.svg"
    CLOCK = "navigation/clock.svg"
    HOME = "navigation/home.svg"
    BRIEFCASE = "navigation/briefcase.svg"
    CREDIT_CARD = "navigation/credit-card.svg"
    CHEVRON_DOWN = "navigation/chevron-down.svg"
    VAULT = "navigation/vault.svg"
    FOLDER = "navigation/folder.svg"
    SETTINGS = "navigation/settings.svg"
    USER = "navigation/user.svg"
    SEARCH = "navigation/search.svg"
    
    # Status
    SUCCESS = "status/success.svg"
    WARNING = "status/warning.svg"
    ERROR = "status/error.svg"
    INFO = "status/info.svg"
    LOADER = "status/loader.svg"
    
    # Security
    SHIELD = "security/shield.svg"
    SHIELD_CHECK = "security/shield-check.svg"
    LOCK = "security/lock.svg"
