from typing import Any, Callable
import customtkinter as ctk

from ui_legacy.design_system import spacing, typography
from .base import BaseComponent
from .label import Label
from .button import Button

class EmptyState(ctk.CTkFrame, BaseComponent):
    def __init__(
        self,
        master: Any,
        icon: str = "search",
        title: str = "No items found",
        message: str | None = None,
        action_text: str | None = None,
        action_command: Callable[[], None] | None = None,
        **kwargs
    ):
        ctk.CTkFrame.__init__(self, master, fg_color="transparent")
        BaseComponent.__init__(self, master, **kwargs)
        
        self.icon_label = ctk.CTkLabel(
            self,
            text="",
            image=self._load_icon(icon, size=48)
        )
        self.icon_label.pack(pady=(0, spacing.M))
        
        self.title_label = Label(
            self,
            text=title,
            typography=typography.Headline,
            variant="primary"
        )
        self.title_label.pack(pady=(0, spacing.XS))
        
        if message:
            self.message_label = Label(
                self,
                text=message,
                typography=typography.Body,
                variant="muted"
            )
            self.message_label.pack(pady=(0, spacing.M))
            
        if action_text and action_command:
            self.action_btn = Button(
                self,
                text=action_text,
                variant="secondary",
                command=action_command
            )
            self.action_btn.pack(pady=(spacing.S, 0))
