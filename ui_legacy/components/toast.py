from typing import Any
import customtkinter as ctk

from ui_legacy.design_system import typography, radius, spacing
from .base import BaseComponent
from .label import Label

class ToastManager(BaseComponent):
    def __init__(self, parent: Any, **kwargs):
        BaseComponent.__init__(self, parent, **kwargs)
        
        theme = self.get_theme()
        
        self.toast_frame = ctk.CTkFrame(
            parent,
            fg_color=theme.surface_elevated,
            border_width=1,
            border_color=theme.border,
            corner_radius=radius.LARGE,
        )
        self.toast_label = Label(
            self.toast_frame,
            text="",
            typography=typography.BodyBold
        )
        self.toast_label.pack(padx=spacing.XL, pady=spacing.S)

    def show(self, text: str, is_error: bool = False) -> None:
        theme = self.get_theme()
        self.toast_label.configure(text=text)
        
        if is_error:
            self.toast_label.configure(text_color=theme.danger)
        else:
            self.toast_label.configure(text_color=theme.success)
            
        self.toast_frame.place(relx=0.5, rely=0.92, anchor="center")
        self.toast_frame.after(3000, self.toast_frame.place_forget)
