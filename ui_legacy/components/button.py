from typing import Any, Callable, Literal
import customtkinter as ctk

from ui_legacy.design_system import typography, radius
from .base import BaseComponent, SizeVariant, StateVariant

ButtonVariant = Literal["primary", "secondary", "ghost", "danger"]

class Button(ctk.CTkButton, BaseComponent):
    def __init__(
        self,
        master: Any,
        text: str = "",
        variant: ButtonVariant = "primary",
        size: SizeVariant = "medium",
        icon: str | None = None,
        command: Callable[[], None] | None = None,
        state: StateVariant = "normal",
        shortcut: str | None = None,
        **kwargs
    ):
        BaseComponent.__init__(self, master, **kwargs)
        
        self.variant = variant
        self.size = size
        self.icon_name = icon
        self.shortcut = shortcut
        self._current_state = state

        # Determine dimensions and typography based on size
        if size == "small":
            height = 28
            font = typography.Body
            icon_size = 16
        elif size == "large":
            height = 44
            font = typography.Headline
            icon_size = 24
        else: # medium
            height = 36
            font = typography.BodyBold
            icon_size = 20

        # Load Icon
        ctk_image = self._load_icon(self.icon_name, size=icon_size)

        theme = self.get_theme()
        
        # Determine colors based on variant
        text_color = "white"
        fg_color = theme.accent
        hover_color = theme.accent_hover
        border_width = 0
        border_color = theme.accent # Cannot be "transparent"

        if variant == "secondary":
            fg_color = theme.input_bg
            hover_color = theme.border
            text_color = theme.text_primary
            border_width = 1
            border_color = theme.border
        elif variant == "ghost":
            fg_color = "transparent"
            hover_color = theme.surface_elevated
            text_color = theme.text_primary
            border_color = theme.surface # fallback valid color for 0 width
        elif variant == "danger":
            fg_color = theme.danger
            hover_color = "#DC2626" # darker red
            text_color = "white"
            border_color = theme.danger
        
        super().__init__(
            master=master,
            text=text,
            image=ctk_image,
            command=command,
            font=self._get_font(font),
            height=height,
            corner_radius=radius.MEDIUM,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=text_color,
            border_width=border_width,
            border_color=border_color,
            state="normal" if state == "normal" else "disabled" if state == "disabled" else "normal",
            **kwargs
        )
        
        self.update_state(state)

    def update_state(self, state: StateVariant) -> None:
        self._current_state = state
        if state == "disabled" or state == "loading":
            self.configure(state="disabled")
            # In a full implementation, we might change opacity or swap the icon to a spinner
        else:
            self.configure(state="normal")
