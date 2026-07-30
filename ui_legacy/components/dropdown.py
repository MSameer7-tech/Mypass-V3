from typing import Any, Callable
import customtkinter as ctk

from ui_legacy.design_system import typography, radius
from .base import BaseComponent, SizeVariant

class Dropdown(ctk.CTkOptionMenu, BaseComponent):
    def __init__(
        self,
        master: Any,
        values: list[str],
        size: SizeVariant = "medium",
        command: Callable[[str], None] | None = None,
        variable: ctk.StringVar | None = None,
        **kwargs
    ):
        BaseComponent.__init__(self, master, **kwargs)
        
        if size == "small":
            height = 28
            font = typography.Body
        elif size == "large":
            height = 44
            font = typography.Headline
        else:
            height = 36
            font = typography.Body
            
        theme = self.get_theme()
        
        super().__init__(
            master=master,
            values=values,
            command=command,
            variable=variable,
            height=height,
            font=self._get_font(font),
            dropdown_font=self._get_font(font),
            fg_color=theme.input_bg,
            button_color=theme.input_bg,
            button_hover_color=theme.surface_elevated,
            text_color=theme.text_primary,
            dropdown_fg_color=theme.surface,
            dropdown_hover_color=theme.surface_elevated,
            dropdown_text_color=theme.text_primary,
            corner_radius=radius.MEDIUM,
            **kwargs
        )
