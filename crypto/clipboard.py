import pyperclip


class ClipboardService:
    def copy(self, value: str) -> None:
        pyperclip.copy(value)
