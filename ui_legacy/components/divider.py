from typing import Any, Literal
import customtkinter as ctk

from ui_legacy.design_system import spacing
from .base import BaseComponent

Orientation = Literal["horizontal", "vertical"]

class Divider(ctk.CTkFrame, BaseComponent):
    def __init__(
        self,
        master: Any,
        orientation: Orientation = "horizontal",
        padding: int = spacing.M,
        **kwargs
    ):
        ctk.CTkFrame.__init__(self, master, fg_color="transparent")
        BaseComponent.__init__(self, master, **kwargs)
        
        theme = self.get_theme()
        
        self.line = ctk.CTkFrame(
            self,
            fg_color=theme.border,
        )
        
        if orientation == "horizontal":
            self.line.configure(height=1)
            self.line.pack(fill="x", expand=True, pady=padding)
        else:
            self.line.configure(width=1)
            self.line.pack(fill="y", expand=True, padx=padding)
