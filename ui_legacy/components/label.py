from typing import Any, Literal
import customtkinter as ctk

from ui_legacy.design_system import typography
from ui_legacy.design_system.themes import get_theme
from .base import BaseComponent

VariantType = Literal["primary", "secondary", "muted", "danger", "success", "warning"]

class Label(ctk.CTkLabel, BaseComponent):
    def __init__(
        self,
        master: Any,
        text: str = "",
        variant: VariantType = "primary",
        typography: typography.Typography = typography.Body,
        **kwargs
    ):
        BaseComponent.__init__(self, master, **kwargs)
        
        self.variant = variant
        self.text = text
        self.typography = typography

        theme = self.get_theme()
        text_color = theme.text_primary
        if variant == "secondary" or variant == "muted":
            text_color = theme.text_secondary
        elif variant == "danger":
            text_color = theme.danger
        elif variant == "success":
            text_color = theme.success
        elif variant == "warning":
            text_color = theme.warning

        super().__init__(
            master=master,
            text=text,
            font=self._get_font(typography),
            text_color=text_color,
            **kwargs
        )
