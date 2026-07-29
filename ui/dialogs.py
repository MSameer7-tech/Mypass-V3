import customtkinter as ctk

from config import (
    ACCENT_COLOR,
    APP_FONT,
    BORDER_COLOR,
    CARD_COLOR,
    ERROR_COLOR,
    HOVER_ACCENT_COLOR,
    INPUT_COLOR,
    MUTED_TEXT,
    SUCCESS_COLOR,
)
from services.password_generator import PasswordGeneratorOptions


class ToastManager:
    def __init__(self, parent, font):
        self.toast_frame = ctk.CTkFrame(
            parent,
            fg_color=CARD_COLOR,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=16,
        )
        self.toast_label = ctk.CTkLabel(
            self.toast_frame,
            text="",
            font=(font, 13, "bold"),
            text_color="white",
        )
        self.toast_label.pack(padx=20, pady=8)

    def show(self, text: str, is_error: bool = False) -> None:
        color = ERROR_COLOR if is_error else SUCCESS_COLOR
        self.toast_label.configure(text=text, text_color=color)
        self.toast_frame.place(relx=0.5, rely=0.92, anchor="center")
        self.toast_frame.after(3000, self.toast_frame.place_forget)


def flash_entry_error(entry, error_color, default_color) -> None:
    original = entry.cget("border_color") or default_color
    entry.configure(border_color=error_color)
    entry.after(400, lambda: entry.configure(border_color=original))


class PasswordGeneratorDialog(ctk.CTkToplevel):
    def __init__(self, parent, on_generate):
        super().__init__(parent)
        self.on_generate = on_generate
        self.title("Password Generator")
        self.geometry("380x440")
        self.resizable(False, False)
        self.configure(fg_color=CARD_COLOR)
        self.transient(parent)
        self.grab_set()

        self.length_var = ctk.StringVar(value="16")
        self.uppercase_var = ctk.BooleanVar(value=True)
        self.lowercase_var = ctk.BooleanVar(value=True)
        self.numbers_var = ctk.BooleanVar(value=True)
        self.symbols_var = ctk.BooleanVar(value=True)
        self.similar_var = ctk.BooleanVar(value=False)
        self.ambiguous_var = ctk.BooleanVar(value=False)
        self.error_var = ctk.StringVar(value="")
        self._build_ui()

    def _build_ui(self) -> None:
        ctk.CTkLabel(
            self,
            text="Password Generator",
            font=(APP_FONT, 18, "bold"),
            text_color="white",
        ).pack(anchor="w", padx=24, pady=(24, 14))

        length_row = ctk.CTkFrame(self, fg_color="transparent")
        length_row.pack(fill="x", padx=24, pady=(0, 10))
        ctk.CTkLabel(
            length_row, text="Length", font=(APP_FONT, 13), text_color=MUTED_TEXT
        ).pack(side="left")
        ctk.CTkEntry(
            length_row,
            textvariable=self.length_var,
            width=80,
            height=34,
            fg_color=INPUT_COLOR,
            border_color=BORDER_COLOR,
        ).pack(side="right")

        for label, variable in (
            ("Uppercase", self.uppercase_var),
            ("Lowercase", self.lowercase_var),
            ("Numbers", self.numbers_var),
            ("Symbols", self.symbols_var),
            ("Exclude similar characters", self.similar_var),
            ("Avoid ambiguous characters", self.ambiguous_var),
        ):
            ctk.CTkCheckBox(
                self,
                text=label,
                variable=variable,
                font=(APP_FONT, 13),
                text_color="white",
                fg_color=ACCENT_COLOR,
                hover_color=HOVER_ACCENT_COLOR,
            ).pack(anchor="w", padx=24, pady=4)

        ctk.CTkLabel(
            self,
            textvariable=self.error_var,
            font=(APP_FONT, 12),
            text_color=ERROR_COLOR,
        ).pack(anchor="w", padx=24, pady=(4, 0))
        ctk.CTkButton(
            self,
            text="Generate Password",
            height=38,
            fg_color=ACCENT_COLOR,
            hover_color=HOVER_ACCENT_COLOR,
            command=self._submit,
        ).pack(fill="x", padx=24, pady=(10, 20))

    def _submit(self) -> None:
        try:
            options = PasswordGeneratorOptions(
                length=int(self.length_var.get()),
                uppercase=self.uppercase_var.get(),
                lowercase=self.lowercase_var.get(),
                numbers=self.numbers_var.get(),
                symbols=self.symbols_var.get(),
                exclude_similar=self.similar_var.get(),
                avoid_ambiguous=self.ambiguous_var.get(),
            )
            self.on_generate(options)
        except ValueError as error:
            self.error_var.set(str(error))
            return
        self.destroy()
