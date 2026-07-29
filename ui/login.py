import customtkinter as ctk

from config import (
    ACCENT_COLOR,
    APP_FONT,
    BORDER_COLOR,
    CARD_COLOR,
    ERROR_COLOR,
    FOCUS_BORDER,
    HOVER_ACCENT_COLOR,
    INPUT_COLOR,
    MUTED_TEXT,
)

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, *, is_first_launch: bool, on_submit):
        super().__init__(parent, fg_color="transparent")
        self.is_first_launch = is_first_launch
        self.on_submit = on_submit
        self.error_var = ctk.StringVar(value="")
        self._build_ui()

    def _build_ui(self) -> None:
        card = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=16,
            border_width=1,
            border_color=BORDER_COLOR,
        )
        card.pack(expand=True, fill="both", padx=24, pady=24)

        title = "Create Master Password" if self.is_first_launch else "Unlock Vault"
        subtitle = (
            "Your master password is never stored. It unlocks the vault from your device."
            if self.is_first_launch
            else "Enter your master password to unlock the vault."
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=(APP_FONT, 24, "bold"),
            text_color="white",
        ).pack(anchor="w", padx=40, pady=(80, 8))
        ctk.CTkLabel(
            card,
            text=subtitle,
            font=(APP_FONT, 12),
            text_color=MUTED_TEXT,
            wraplength=520,
            justify="left",
        ).pack(anchor="w", padx=40, pady=(0, 24))

        self.password_entry = self._build_entry(card, "Master Password")
        self.password_entry.pack(fill="x", padx=40, pady=(0, 16))

        self.confirm_entry = None
        if self.is_first_launch:
            self.confirm_entry = self._build_entry(card, "Confirm Master Password")
            self.confirm_entry.pack(fill="x", padx=40, pady=(0, 16))

        self.error_label = ctk.CTkLabel(
            card,
            textvariable=self.error_var,
            font=(APP_FONT, 12),
            text_color=ERROR_COLOR,
        )
        self.error_label.pack(anchor="w", padx=40, pady=(0, 12))

        button_text = "Create Vault" if self.is_first_launch else "Unlock"
        ctk.CTkButton(
            card,
            text=button_text,
            height=44,
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_ACCENT_COLOR,
            text_color="white",
            corner_radius=8,
            cursor="hand2",
            font=(APP_FONT, 13, "bold"),
            command=self._submit,
        ).pack(fill="x", padx=40, pady=(8, 0))

        self.password_entry.bind("<Return>", lambda event: self._submit())
        if self.confirm_entry is not None:
            self.confirm_entry.bind("<Return>", lambda event: self._submit())

    def _build_entry(self, parent, placeholder: str):
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=44,
            fg_color=INPUT_COLOR,
            border_color=BORDER_COLOR,
            corner_radius=8,
            border_width=1,
            show="*",
        )
        entry.bind("<FocusIn>", lambda event: entry.configure(border_color=FOCUS_BORDER))
        entry.bind("<FocusOut>", lambda event: entry.configure(border_color=BORDER_COLOR))
        return entry

    def _submit(self) -> None:
        password = self.password_entry.get()
        confirm_password = self.confirm_entry.get() if self.confirm_entry is not None else ""

        if not password:
            self.error_var.set("Enter a master password.")
            return
        if self.confirm_entry is not None and password != confirm_password:
            self.error_var.set("Master passwords do not match.")
            return

        try:
            self.on_submit(password)
            self.error_var.set("")
        except Exception as error:
            self.error_var.set(str(error))
