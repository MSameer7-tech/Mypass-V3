from PySide6.QtGui import QIcon, QFont

class ResourceManager:
    """Centralized resource loading stubs for Phase 0."""
    
    @staticmethod
    def get_icon(name: str) -> QIcon:
        # Placeholder for Lucide SVG loading
        return QIcon()

    @staticmethod
    def get_font(family: str, size: int, weight: int = -1, italic: bool = False) -> QFont:
        return QFont(family, size, weight, italic)
