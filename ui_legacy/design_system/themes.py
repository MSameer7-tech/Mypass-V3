from dataclasses import dataclass

@dataclass
class Theme:
    background: str
    surface: str
    surface_elevated: str
    border: str
    text_primary: str
    text_secondary: str
    accent: str
    accent_hover: str
    success: str
    warning: str
    danger: str
    input_bg: str

DarkTheme = Theme(
    background="#141414",
    surface="#1E1E1E",
    surface_elevated="#252525",
    border="#333333",
    text_primary="#FFFFFF",
    text_secondary="#8E8E93",
    accent="#3B82F6",
    accent_hover="#2563EB",
    success="#10B981",
    warning="#F59E0B",
    danger="#EF4444",
    input_bg="#2A2A2A",
)

LightTheme = Theme(
    background="#F9FAFB",
    surface="#FFFFFF",
    surface_elevated="#FFFFFF",
    border="#E5E7EB",
    text_primary="#111827",
    text_secondary="#6B7280",
    accent="#3B82F6",
    accent_hover="#2563EB",
    success="#10B981",
    warning="#F59E0B",
    danger="#EF4444",
    input_bg="#F3F4F6",
)

import weakref

# Active Theme
active_theme = DarkTheme

class ThemeManager:
    _listeners = weakref.WeakSet()
    
    @classmethod
    def register(cls, component):
        cls._listeners.add(component)
        
    @classmethod
    def set_theme(cls, theme: Theme):
        global active_theme
        active_theme = theme
        cls.notify_theme_changed()
        
    @classmethod
    def notify_theme_changed(cls):
        for component in cls._listeners:
            if hasattr(component, 'apply_theme'):
                try:
                    component.apply_theme()
                except Exception:
                    pass

def get_theme() -> Theme:
    return active_theme
