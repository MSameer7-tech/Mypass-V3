from typing import Any
import customtkinter as ctk

from ui_legacy.design_system import typography, spacing, radius
from .base import BaseComponent
from .label import Label
from .button import Button

class BaseDialog(ctk.CTkToplevel, BaseComponent):
    """
    Standard dialog base. Provides unified padding, title rendering, and standard 
    footer buttons if configured. Existing dialogs can inherit this to standardize
    their appearance.
    """
    def __init__(
        self,
        parent: Any,
        title: str,
        width: int = 400,
        height: int = 300,
        show_close: bool = True,
        **kwargs
    ):
        ctk.CTkToplevel.__init__(self, parent)
        BaseComponent.__init__(self, parent, **kwargs)
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        theme = self.get_theme()
        self.configure(fg_color=theme.background)
        
        # Main content area
        self.container = ctk.CTkFrame(
            self,
            fg_color=theme.surface,
            corner_radius=0
        )
        self.container.pack(fill="both", expand=True)
        
        # Header
        self.header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=spacing.XL, pady=(spacing.XL, spacing.L))
        
        self.title_label = Label(
            self.header_frame,
            text=title,
            typography=typography.Title,
            variant="primary"
        )
        self.title_label.pack(side="left")
        
        if show_close:
            self.close_btn = Button(
                self.header_frame,
                variant="ghost",
                size="small",
                icon="x",
                command=self.destroy
            )
            self.close_btn.pack(side="right")
            
        # Footer frame (optional, for standard ok/cancel buttons) — packed FIRST at bottom
        self.footer_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        
        # Body frame (scrollable, for subclasses to pack their content into)
        self.body_frame = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True, padx=spacing.XL, pady=(0, spacing.M))
        
    def add_standard_buttons(
        self,
        primary_text: str = "Confirm",
        primary_command: Any = None,
        primary_variant: str = "primary",
        secondary_text: str = "Cancel",
        secondary_command: Any = None
    ) -> None:
        """
        Helper to add standard dual-action buttons to the footer.
        """
        self.footer_frame.pack(fill="x", side="bottom", padx=spacing.XL, pady=(0, spacing.XL))
        
        if secondary_command:
            secondary_btn = Button(
                self.footer_frame,
                text=secondary_text,
                variant="secondary",
                command=secondary_command
            )
            secondary_btn.pack(side="left", fill="x", expand=True, padx=(0, spacing.S))
            
        if primary_command:
            primary_btn = Button(
                self.footer_frame,
                text=primary_text,
                variant=primary_variant, # type: ignore
                command=primary_command
            )
            primary_btn.pack(side="right", fill="x", expand=True, padx=(spacing.S, 0))
