import platform

import customtkinter as ctk


BG_COLOR = "#1A1A1A"
CARD_COLOR = "#252525"
INPUT_COLOR = "#2A2A2A"
BORDER_COLOR = "#333333"
FOCUS_BORDER = "#4F8CFF"
ACCENT_COLOR = "#3B82F6"
MUTED_TEXT = "#8E8E93"
ERROR_COLOR = "#EF4444"
WARNING_COLOR = "#F59E0B"
SUCCESS_COLOR = "#10B981"
HOVER_ACCENT_COLOR = "#2563EB"


def get_app_font() -> str:
    os_name = platform.system()
    if os_name == "Darwin":
        return "SF Pro"
    if os_name == "Windows":
        return "Segoe UI"
    return "Arial"


APP_FONT = get_app_font()


def configure_ctk() -> None:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
