from typing import Any
import customtkinter as ctk

from ui_legacy.design_system import typography, radius
from .base import BaseComponent

class Checkbox(ctk.CTkCheckBox, BaseComponent):
    def __init__(
        self,
        master: Any,
        text: str = "",
        variable: Any = None,
        command: Any = None,
        **kwargs
    ):
        BaseComponent.__init__(self, master, **kwargs)
        
        theme = self.get_theme()
        
        super().__init__(
            master=master,
            text=text,
            variable=variable,
            command=command,
            font=self._get_font(typography.Body),
            text_color=theme.text_primary,
            fg_color=theme.accent,
            hover_color=theme.accent_hover,
            border_color=theme.border,
            corner_radius=radius.SMALL,
            **kwargs
        )
