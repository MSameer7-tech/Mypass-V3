import customtkinter as ctk

from config import BORDER_COLOR, CARD_COLOR, ERROR_COLOR, SUCCESS_COLOR


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
