from dataclasses import dataclass

@dataclass(frozen=True)
class ColorPalette:
    background: str
    surface: str
    surface_elevated: str
    border: str
    text_primary: str
    text_secondary: str
    text_tertiary: str
    text_disabled: str
    divider: str
    accent: str
    accent_hover: str
    success: str
    warning: str
    danger: str
    input_bg: str

DarkColors = ColorPalette(
    background="#141518",
    surface="#1B1C21",
    surface_elevated="#16171A",
    border="#252730",
    text_primary="#FFFFFF",
    text_secondary="#9498A6",
    text_tertiary="#636674",
    text_disabled="#484A54",
    divider="#23252E",
    accent="#1F69FF",
    accent_hover="#3B82F6",
    success="#10B981",
    warning="#F59E0B",
    danger="#EF4444",
    input_bg="#22242B",
)

LightColors = ColorPalette(
    background="#F9FAFB",
    surface="#FFFFFF",
    surface_elevated="#FFFFFF",
    border="#E5E7EB",
    text_primary="#111827",
    text_secondary="#6B7280",
    text_tertiary="#9CA3AF",
    text_disabled="#D1D5DB",
    divider="#E5E7EB",
    accent="#3B82F6",
    accent_hover="#2563EB",
    success="#10B981",
    warning="#F59E0B",
    danger="#EF4444",
    input_bg="#F3F4F6",
)
