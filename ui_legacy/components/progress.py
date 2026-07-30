from typing import Any
import customtkinter as ctk

from ui_legacy.design_system import spacing
from .base import BaseComponent
from .label import Label

class ProgressBar(ctk.CTkProgressBar, BaseComponent):
    def __init__(
        self,
        master: Any,
        progress: float = 0.0,
        **kwargs
    ):
        BaseComponent.__init__(self, master, **kwargs)
        
        theme = self.get_theme()
        
        ctk.CTkProgressBar.__init__(
            self,
            master=master,
            fg_color=theme.input_bg,
            progress_color=theme.accent,
            **kwargs
        )
        self.set(progress)

class PasswordStrengthIndicator(ctk.CTkFrame, BaseComponent):
    def __init__(
        self,
        master: Any,
        **kwargs
    ):
        ctk.CTkFrame.__init__(self, master, fg_color="transparent")
        BaseComponent.__init__(self, master, **kwargs)
        
        self.bar = ProgressBar(self)
        self.bar.pack(fill="x", expand=True)
        
        self.label = Label(self, text="Strength: Unknown", variant="muted")
        self.label.pack(anchor="w", pady=(spacing.XS, 0))
        
    def set_strength(self, score: int, label_text: str | None = None) -> None:
        """
        score: 0 to 4
        """
        theme = self.get_theme()
        
        if score == 0:
            color = theme.danger
            text = "Strength: Very Weak"
            val = 0.2
        elif score == 1:
            color = theme.danger
            text = "Strength: Weak"
            val = 0.4
        elif score == 2:
            color = theme.warning
            text = "Strength: Fair"
            val = 0.6
        elif score == 3:
            color = theme.success
            text = "Strength: Strong"
            val = 0.8
        else:
            color = theme.success
            text = "Strength: Very Strong"
            val = 1.0
            
        self.bar.set(val)
        self.bar.configure(progress_color=color)
        
        if label_text:
            text = label_text
            
        self.label.configure(text=text)
