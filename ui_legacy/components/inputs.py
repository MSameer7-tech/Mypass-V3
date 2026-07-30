from typing import Any, Callable
import customtkinter as ctk

from ui_legacy.design_system import typography, radius, spacing
from .base import BaseComponent, SizeVariant, StateVariant
from .label import Label
from .button import Button

class _BaseInput(ctk.CTkFrame, BaseComponent):
    """
    Internal base frame that groups a label (optional), the input field itself,
    and an error message (optional).
    """
    def __init__(
        self,
        master: Any,
        label: str | None = None,
        required: bool = False,
        error_message: str | None = None,
        **kwargs
    ):
        ctk.CTkFrame.__init__(self, master, fg_color="transparent")
        BaseComponent.__init__(self, master, **kwargs)

        self._label_text = label
        self._required = required
        
        if label:
            label_text = f"{label} *" if required else label
            self.label_widget = Label(self, text=label_text, typography=typography.BodyBold)
            self.label_widget.pack(anchor="w", pady=(0, spacing.XS))
            
        self.input_container = ctk.CTkFrame(self, fg_color="transparent")
        self.input_container.pack(fill="x", expand=True)
        
        self.error_label = Label(self, text=error_message or "", variant="danger", typography=typography.Caption)
        if error_message:
            self.error_label.pack(anchor="w", pady=(spacing.XS, 0))

    def set_error(self, message: str | None) -> None:
        if message:
            self.error_label.configure(text=message)
            self.error_label.pack(anchor="w", pady=(spacing.XS, 0))
            self.update_state("error")
        else:
            self.error_label.pack_forget()
            self.update_state("normal")

    def update_state(self, state: StateVariant) -> None:
        pass # To be overridden by specific input fields

class TextField(_BaseInput):
    def __init__(
        self,
        master: Any,
        label: str | None = None,
        placeholder: str = "",
        state: StateVariant = "normal",
        size: SizeVariant = "medium",
        required: bool = False,
        error_message: str | None = None,
        textvariable: ctk.StringVar | None = None,
        **kwargs
    ):
        super().__init__(master, label=label, required=required, error_message=error_message, **kwargs)
        
        self._current_state = state
        self.size = size
        
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
        
        self.entry = ctk.CTkEntry(
            self.input_container,
            placeholder_text=placeholder,
            textvariable=textvariable,
            height=height,
            font=self._get_font(font),
            fg_color=theme.input_bg,
            border_color=theme.border,
            border_width=1,
            text_color=theme.text_primary,
            placeholder_text_color=theme.text_secondary,
            corner_radius=radius.MEDIUM
        )
        self.entry.pack(fill="x", expand=True)
        self.update_state(state)
        
        # Bind focus events for active styling
        self.entry.bind("<FocusIn>", lambda e: self.update_state("focused"))
        self.entry.bind("<FocusOut>", lambda e: self.update_state("normal") if self._current_state != "error" else None)
        
    def update_state(self, state: StateVariant) -> None:
        self._current_state = state
        theme = self.get_theme()
        
        if state == "disabled":
            self.entry.configure(state="disabled", border_color=theme.border, fg_color=theme.surface_elevated)
        elif state == "error":
            self.entry.configure(state="normal", border_color=theme.danger, border_width=1)
        elif state == "focused":
            self.entry.configure(state="normal", border_color=theme.accent, border_width=2)
        elif state == "success":
            self.entry.configure(state="normal", border_color=theme.success, border_width=1)
        else: # normal
            self.entry.configure(state="normal", border_color=theme.border, border_width=1, fg_color=theme.input_bg)
            
    def get(self) -> str:
        return self.entry.get()

class PasswordField(_BaseInput):
    def __init__(
        self,
        master: Any,
        label: str | None = None,
        placeholder: str = "",
        state: StateVariant = "normal",
        size: SizeVariant = "medium",
        required: bool = False,
        error_message: str | None = None,
        textvariable: ctk.StringVar | None = None,
        allow_copy: bool = False,
        allow_visibility_toggle: bool = True,
        on_copy: Callable[[], None] | None = None,
        **kwargs
    ):
        super().__init__(master, label=label, required=required, error_message=error_message, **kwargs)
        
        self.is_visible = False
        
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
        
        self.entry = ctk.CTkEntry(
            self.input_container,
            placeholder_text=placeholder,
            textvariable=textvariable,
            height=height,
            font=self._get_font(font),
            fg_color=theme.input_bg,
            border_color=theme.border,
            border_width=1,
            text_color=theme.text_primary,
            placeholder_text_color=theme.text_secondary,
            corner_radius=radius.MEDIUM,
            show="*"
        )
        self.entry.pack(side="left", fill="x", expand=True)
        
        if allow_visibility_toggle:
            self.toggle_btn = Button(
                self.input_container, 
                variant="ghost", 
                size=size,
                icon="eye", 
                command=self._toggle_visibility
            )
            self.toggle_btn.pack(side="left", padx=(spacing.XS, 0))
            
        if allow_copy:
            self.copy_btn = Button(
                self.input_container,
                variant="ghost",
                size=size,
                icon="copy",
                command=on_copy
            )
            self.copy_btn.pack(side="left", padx=(spacing.XS, 0))
            
        self.update_state(state)
        
    def _toggle_visibility(self):
        self.is_visible = not self.is_visible
        if self.is_visible:
            self.entry.configure(show="")
            self.toggle_btn.configure(image=self._load_icon("eye-off", size=20))
        else:
            self.entry.configure(show="*")
            self.toggle_btn.configure(image=self._load_icon("eye", size=20))
            
    def update_state(self, state: StateVariant) -> None:
        self._current_state = state
        theme = self.get_theme()
        
        if state == "disabled":
            self.entry.configure(state="disabled", border_color=theme.border, fg_color=theme.surface_elevated)
        elif state == "error":
            self.entry.configure(state="normal", border_color=theme.danger, border_width=1)
        elif state == "focused":
            self.entry.configure(state="normal", border_color=theme.accent, border_width=2)
        else:
            self.entry.configure(state="normal", border_color=theme.border, border_width=1, fg_color=theme.input_bg)
            
    def get(self) -> str:
        return self.entry.get()

class SearchField(ctk.CTkFrame, BaseComponent):
    def __init__(
        self,
        master: Any,
        placeholder: str = "Search...",
        size: SizeVariant = "medium",
        command: Callable[[str], None] | None = None,
        **kwargs
    ):
        ctk.CTkFrame.__init__(self, master, fg_color="transparent")
        BaseComponent.__init__(self, master, **kwargs)
        
        self.command = command
        theme = self.get_theme()
        
        if size == "small":
            height = 28
            font = typography.Body
        elif size == "large":
            height = 44
            font = typography.Headline
        else:
            height = 36
            font = typography.Body
            
        # Inner container mimicking the input styling
        self.container = ctk.CTkFrame(
            self, 
            fg_color=theme.input_bg, 
            corner_radius=radius.MEDIUM,
            border_width=1,
            border_color=theme.border
        )
        self.container.pack(fill="x", expand=True)
        
        self.search_icon = ctk.CTkLabel(self.container, text="", image=self._load_icon("search", size=16))
        self.search_icon.pack(side="left", padx=(spacing.S, 0))
        
        self.entry = ctk.CTkEntry(
            self.container,
            placeholder_text=placeholder,
            height=height,
            font=self._get_font(font),
            fg_color="transparent",
            border_width=0,
            text_color=theme.text_primary,
            placeholder_text_color=theme.text_secondary,
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=spacing.XS)
        
        self.clear_btn = Button(
            self.container,
            variant="ghost",
            size="small",
            icon="delete",
            command=self._clear
        )
        
        self.entry.bind("<KeyRelease>", self._on_change)
        self.entry.bind("<FocusIn>", lambda e: self.container.configure(border_color=theme.accent, border_width=2))
        self.entry.bind("<FocusOut>", lambda e: self.container.configure(border_color=theme.border, border_width=1))
        
    def _on_change(self, event):
        val = self.entry.get()
        if val:
            self.clear_btn.pack(side="right", padx=(0, spacing.XS))
        else:
            self.clear_btn.pack_forget()
            
        if self.command:
            self.command(val)
            
    def _clear(self):
        self.entry.delete(0, 'end')
        self.clear_btn.pack_forget()
        if self.command:
            self.command("")

class TextArea(_BaseInput):
    def __init__(
        self,
        master: Any,
        label: str | None = None,
        state: StateVariant = "normal",
        height: int = 100,
        **kwargs
    ):
        super().__init__(master, label=label, **kwargs)
        
        theme = self.get_theme()
        
        self.textbox = ctk.CTkTextbox(
            self.input_container,
            height=height,
            font=self._get_font(typography.Body),
            fg_color=theme.input_bg,
            border_color=theme.border,
            border_width=1,
            text_color=theme.text_primary,
            corner_radius=radius.MEDIUM
        )
        self.textbox.pack(fill="x", expand=True)
        self.update_state(state)
        
        self.textbox.bind("<FocusIn>", lambda e: self.update_state("focused"))
        self.textbox.bind("<FocusOut>", lambda e: self.update_state("normal"))

    def update_state(self, state: StateVariant) -> None:
        self._current_state = state
        theme = self.get_theme()
        
        if state == "disabled":
            self.textbox.configure(state="disabled", border_color=theme.border, fg_color=theme.surface_elevated)
        elif state == "error":
            self.textbox.configure(state="normal", border_color=theme.danger, border_width=1)
        elif state == "focused":
            self.textbox.configure(state="normal", border_color=theme.accent, border_width=2)
        else:
            self.textbox.configure(state="normal", border_color=theme.border, border_width=1, fg_color=theme.input_bg)

    def get(self) -> str:
        return self.textbox.get("1.0", "end-1c")

class Radio(ctk.CTkRadioButton, BaseComponent):
    """
    Radio button component aligned with the design system.
    """
    def __init__(
        self,
        master: Any,
        text: str = "",
        variable: Any = None,
        value: Any = None,
        command: Any = None,
        **kwargs
    ):
        ctk.CTkRadioButton.__init__(
            self,
            master=master,
            text=text,
            variable=variable,
            value=value,
            command=command,
            **kwargs
        )
        BaseComponent.__init__(self, master, **kwargs)
        
        self.configure(
            font=self._get_font(typography.Body),
            corner_radius=999,
        )
        self.apply_theme()
        
    def apply_theme(self) -> None:
        super().apply_theme()
        self.configure(
            text_color=self._theme.text_primary,
            fg_color=self._theme.accent,
            hover_color=self._theme.accent_hover,
            border_color=self._theme.border
        )
