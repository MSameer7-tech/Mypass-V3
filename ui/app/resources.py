import os
from PySide6.QtGui import QIcon, QFont, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt

from ui.resources.styles.themes import ThemeManager

class Resources:
    """Unified API for loading all visual assets."""
    
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets"))
    ICONS_DIR = os.path.join(BASE_DIR, "icons")
    IMAGES_DIR = os.path.join(BASE_DIR, "images")

    @classmethod
    def _tint_svg(cls, icon_path: str, color_hex: str) -> QIcon:
        """Loads an SVG and tints it to the requested color."""
        if not os.path.exists(icon_path):
            return QIcon()
            
        # For Phase 1, we return the QIcon directly. 
        # Qt's QIcon doesn't easily tint SVGs natively without rendering to QPixmap.
        # Since we use Lucide SVGs with `currentColor`, we will need a custom SVG renderer 
        # or we render it to a pixmap here.
        # We'll render to a pixmap as a quick, robust tinting approach.
        
        # Load the SVG as a pixmap (we assume a reasonable default size like 64x64 for crispness)
        pixmap = QIcon(icon_path).pixmap(64, 64)
        if pixmap.isNull():
            return QIcon()
            
        # Create a new pixmap for the tinted version
        tinted = QPixmap(pixmap.size())
        tinted.fill(Qt.transparent)
        
        painter = QPainter(tinted)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Draw the original pixmap
        painter.drawPixmap(0, 0, pixmap)
        
        # Set composition mode to SourceIn to tint non-transparent pixels
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(tinted.rect(), QColor(color_hex))
        painter.end()
        
        return QIcon(tinted)

    @classmethod
    def icon(cls, icon_name: str, color_hex: str = None) -> QIcon:
        """Returns a QIcon from the assets/icons folder. Tints it if color_hex is provided."""
        filename = icon_name if icon_name.endswith(".svg") else f"{icon_name}.svg"
        path = os.path.join(cls.ICONS_DIR, filename)
        
        if color_hex:
            return cls._tint_svg(path, color_hex)
        return QIcon(path)

    @classmethod
    def font(cls, family: str, size: int, weight: str = "normal", italic: bool = False) -> QFont:
        """Constructs a QFont."""
        font = QFont(family, size)
        font.setItalic(italic)
        if weight.lower() == "bold":
            font.setBold(True)
        return font

    @classmethod
    def image(cls, image_name: str) -> QPixmap:
        """Returns a QPixmap from the assets/images folder."""
        path = os.path.join(cls.IMAGES_DIR, image_name)
        return QPixmap(path)

    @classmethod
    def illustration(cls, illustration_name: str) -> QPixmap:
        """Returns an illustration."""
        return cls.image(illustration_name)

    @classmethod
    def favicon(cls) -> QIcon:
        """Returns the main app favicon."""
        path = os.path.join(cls.IMAGES_DIR, "favicon.ico")
        if not os.path.exists(path):
            path = os.path.join(cls.ICONS_DIR, "shield.svg") # Fallback
        return QIcon(path)
