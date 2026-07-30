from dataclasses import dataclass
import platform

@dataclass
class Typography:
    family: str
    size: int
    weight: str = "normal"
    
def get_app_font() -> str:
    os_name = platform.system()
    if os_name == "Darwin":
        return "SF Pro"
    if os_name == "Windows":
        return "Segoe UI"
    return "Arial"

font_family = get_app_font()

Display = Typography(family=font_family, size=32, weight="bold")
Title = Typography(family=font_family, size=24, weight="bold")
Headline = Typography(family=font_family, size=18, weight="bold")
Body = Typography(family=font_family, size=14, weight="normal")
BodyBold = Typography(family=font_family, size=14, weight="bold")
Caption = Typography(family=font_family, size=12, weight="normal")
Tiny = Typography(family=font_family, size=10, weight="normal")

def as_font(typography: Typography) -> tuple:
    return (typography.family, typography.size, typography.weight)
