from dataclasses import dataclass
import platform
from PySide6.QtGui import QFont

class FontWeight:
    REGULAR = QFont.Normal
    MEDIUM = QFont.Medium
    DEMIBOLD = QFont.DemiBold
    BOLD = QFont.Bold
    EXTRABOLD = QFont.ExtraBold

@dataclass(frozen=True)
class TypographyToken:
    family: str
    size: int
    weight: int
    line_height: int = 0
    letter_spacing: float = 0.0

def get_app_font() -> str:
    os_name = platform.system()
    if os_name == "Darwin":
        return "SF Pro"
    if os_name == "Windows":
        return "Segoe UI"
    return "Arial"

FONT_FAMILY = get_app_font()

class Typography:
    # Core Scale
    Display = TypographyToken(family=FONT_FAMILY, size=32, weight=FontWeight.EXTRABOLD, line_height=40, letter_spacing=0)
    Title = TypographyToken(family=FONT_FAMILY, size=24, weight=FontWeight.BOLD, line_height=32, letter_spacing=0)
    Headline = TypographyToken(family=FONT_FAMILY, size=16, weight=FontWeight.BOLD, line_height=24, letter_spacing=0)
    Body = TypographyToken(family=FONT_FAMILY, size=14, weight=FontWeight.REGULAR, line_height=20, letter_spacing=0)
    BodyMedium = TypographyToken(family=FONT_FAMILY, size=14, weight=FontWeight.MEDIUM, line_height=20, letter_spacing=0)
    Caption = TypographyToken(family=FONT_FAMILY, size=12, weight=FontWeight.REGULAR, line_height=16, letter_spacing=0.1)
    Overline = TypographyToken(family=FONT_FAMILY, size=11, weight=FontWeight.DEMIBOLD, line_height=16, letter_spacing=1.2)
    
    # Semantic Aliases
    ScreenTitle = Title
    SectionTitle = Headline
    CardTitle = Headline
    CardSubtitle = Caption
    Metadata = Caption
    SidebarItem = Body
    SidebarSection = Overline
    ButtonLabel = BodyMedium
