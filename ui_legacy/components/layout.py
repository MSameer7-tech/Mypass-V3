from typing import Any
import customtkinter as ctk

from .base import BaseComponent

class Sidebar(ctk.CTkFrame, BaseComponent):
    def __init__(self, master: Any, **kwargs):
        ctk.CTkFrame.__init__(self, master, fg_color="transparent")
        BaseComponent.__init__(self, master, **kwargs)
        
        theme = self.get_theme()
        self.configure(fg_color=theme.surface, width=250)

class Toolbar(ctk.CTkFrame, BaseComponent):
    def __init__(self, master: Any, **kwargs):
        ctk.CTkFrame.__init__(self, master, fg_color="transparent")
        BaseComponent.__init__(self, master, **kwargs)
        
        theme = self.get_theme()
        self.configure(fg_color=theme.surface, height=50)

class Container(ctk.CTkFrame, BaseComponent):
    """
    A layout wrapper around CTkFrame. Use variants for styling context.
    Variants: "transparent" (default), "surface", "elevated"
    """
    def __init__(self, master: Any, variant: str = "transparent", **kwargs):
        ctk.CTkFrame.__init__(self, master, fg_color="transparent")
        BaseComponent.__init__(self, master, variant=variant, **kwargs)
        
        self.apply_theme()
        
    def apply_theme(self) -> None:
        super().apply_theme()
        if self.variant == "surface":
            self.configure(fg_color=self._theme.surface)
        elif self.variant == "elevated":
            self.configure(fg_color=self._theme.surface_elevated)
        else:
            self.configure(fg_color="transparent")
