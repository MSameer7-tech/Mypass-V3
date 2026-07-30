from typing import Any
import customtkinter as ctk

from ui_legacy.design_system import radius, spacing
from .base import BaseComponent

class Card(ctk.CTkFrame, BaseComponent):
    """
    A reusable card component that provides a standard surface elevation and corner radius.
    """
    def __init__(
        self,
        master: Any,
        padding: int = spacing.L,
        **kwargs
    ):
        ctk.CTkFrame.__init__(self, master, fg_color="transparent")
        BaseComponent.__init__(self, master, **kwargs)
        
        theme = self.get_theme()
        
        self.inner_frame = ctk.CTkFrame(
            self,
            fg_color=theme.surface,
            corner_radius=radius.LARGE,
            border_width=1,
            border_color=theme.border
        )
        self.inner_frame.pack(fill="both", expand=True, padx=padding, pady=padding)
        
    def get_container(self) -> ctk.CTkFrame:
        """
        Returns the inner frame so children can be packed into it directly with the appropriate background color.
        """
        return self.inner_frame
