from typing import Any, Literal

import customtkinter as ctk

from ui_legacy.design_system.themes import get_theme, ThemeManager
from ui_legacy.design_system.icons import IconLoader
from ui_legacy.design_system.typography import as_font, Typography

SizeVariant = Literal["small", "medium", "large"]
StateVariant = Literal["normal", "hover", "pressed", "disabled", "focused", "error", "success", "loading"]

class BaseComponent:
    """
    Base class for all design system components.
    Provides standard theme, sizing, and icon loading capabilities.
    """
    def __init__(self, master: Any, variant: str = "primary", size: str = "medium", **kwargs):
        self.master = master
        self._theme = get_theme()
        
        self.component_name = self.__class__.__name__
        self.variant = variant
        self.size = size
        
        ThemeManager.register(self)

    def get_theme(self):
        return self._theme
        
    def _load_icon(self, icon_name: str | None, size: int = 24) -> ctk.CTkImage | None:
        if not icon_name:
            return None
        return IconLoader.load(icon_name, size)
    
    def _get_font(self, typography: Typography) -> tuple:
        return as_font(typography)

    def update_state(self, state: StateVariant) -> None:
        """
        Subclasses should override this to handle state changes (e.g., error borders, disabled opacity).
        """
        pass
        
    def apply_theme(self) -> None:
        """
        Subclasses should override this to re-configure their colors when the active theme changes.
        """
        self._theme = get_theme()
