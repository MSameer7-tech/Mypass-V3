from typing import Any, Literal
import customtkinter as ctk

from ui_legacy.design_system import typography, radius, spacing
from .base import BaseComponent

BadgeVariant = Literal["weak", "strong", "favorite", "breached", "old", "compromised", "neutral"]

class Badge(ctk.CTkFrame, BaseComponent):
    def __init__(
        self,
        master: Any,
        text: str,
        variant: BadgeVariant = "neutral",
        **kwargs
    ):
        ctk.CTkFrame.__init__(self, master, fg_color="transparent")
        BaseComponent.__init__(self, master, **kwargs)
        
        theme = self.get_theme()
        
        # Determine colors based on variant
        if variant == "weak":
            bg_color = theme.warning
            text_color = "#FFFFFF"
        elif variant == "strong":
            bg_color = theme.success
            text_color = "#FFFFFF"
        elif variant == "favorite":
            bg_color = theme.accent
            text_color = "#FFFFFF"
        elif variant in ("breached", "compromised"):
            bg_color = theme.danger
            text_color = "#FFFFFF"
        elif variant == "old":
            bg_color = theme.surface_elevated
            text_color = theme.text_secondary
        else: # neutral
            bg_color = theme.border
            text_color = theme.text_primary
            
        self.container = ctk.CTkFrame(
            self,
            fg_color=bg_color,
            corner_radius=radius.SMALL
        )
        self.container.pack()
        
        self.label = ctk.CTkLabel(
            self.container,
            text=text.upper(),
            font=self._get_font(typography.Tiny),
            text_color=text_color
        )
        self.label.pack(padx=spacing.S, pady=2)

    def set_text(self, text: str) -> None:
        """Update the displayed badge text."""
        self.label.configure(text=text.upper())

    def set_variant(self, variant: str) -> None:
        """Update badge color style based on variant name."""
        theme = self.get_theme()
        if variant in ("weak", "warning"):
            bg_color = theme.warning
            text_color = "#FFFFFF"
        elif variant in ("strong", "success", "excellent"):
            bg_color = theme.success
            text_color = "#FFFFFF"
        elif variant in ("favorite", "primary"):
            bg_color = theme.accent
            text_color = "#FFFFFF"
        elif variant in ("breached", "compromised", "danger"):
            bg_color = theme.danger
            text_color = "#FFFFFF"
        elif variant in ("old", "secondary"):
            bg_color = theme.surface_elevated
            text_color = theme.text_secondary
        else:
            bg_color = theme.border
            text_color = theme.text_primary

        self.container.configure(fg_color=bg_color)
        self.label.configure(text_color=text_color)
