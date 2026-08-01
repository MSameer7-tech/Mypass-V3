import os
from PySide6.QtGui import QIcon, QFont, QPixmap, QPainter, QColor, QImage
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import Qt, QByteArray

from ui.resources.styles.themes import ThemeManager

# Render size for crisp icons on Retina/HiDPI — icons are scaled down from this
_SVG_RENDER_SIZE = 128


class Resources:
    """Unified API for loading all visual assets."""
    
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets"))
    ICONS_DIR = os.path.join(BASE_DIR, "icons")
    IMAGES_DIR = os.path.join(BASE_DIR, "images")

    # In-memory cache: (path, color_hex) -> QIcon
    _icon_cache: dict[tuple[str, str | None], QIcon] = {}

    @classmethod
    def _render_svg(cls, icon_path: str, color_hex: str | None = None) -> QIcon:
        """
        Renders an SVG to a QIcon with proper alpha transparency.
        
        Lucide/Phosphor SVGs use stroke="currentColor" which Qt resolves to
        black by default.  We replace currentColor in the XML with the desired
        colour *before* handing it to QSvgRenderer, producing crisp,
        correctly-tinted, alpha-transparent icons.
        """
        if not os.path.exists(icon_path):
            return QIcon()

        try:
            with open(icon_path, "r", encoding="utf-8") as f:
                svg_xml = f.read()
        except Exception:
            return QIcon()

        # Determine target colour
        if color_hex:
            target_color = color_hex
        else:
            # Default to theme text_primary so icons are visible on dark backgrounds
            try:
                target_color = ThemeManager.colors().text_primary
            except Exception:
                target_color = "#E2E8F0"   # safe light-gray fallback

        # Replace currentColor with actual colour
        svg_xml = svg_xml.replace("currentColor", target_color)

        renderer = QSvgRenderer(QByteArray(svg_xml.encode("utf-8")))
        if not renderer.isValid():
            return QIcon()

        # Render onto an alpha-transparent QImage
        image = QImage(_SVG_RENDER_SIZE, _SVG_RENDER_SIZE, QImage.Format_ARGB32)
        image.fill(QColor(0, 0, 0, 0))

        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        renderer.render(painter)
        painter.end()

        return QIcon(QPixmap.fromImage(image))

    @classmethod
    def icon(cls, icon_name: str, color_hex: str = None) -> QIcon:
        """Returns a QIcon from the assets/icons folder, tinted to color_hex (or theme default)."""
        filename = icon_name if icon_name.endswith(".svg") else f"{icon_name}.svg"
        path = os.path.join(cls.ICONS_DIR, filename)

        cache_key = (path, color_hex)
        cached = cls._icon_cache.get(cache_key)
        if cached is not None:
            return cached

        result = cls._render_svg(path, color_hex)
        cls._icon_cache[cache_key] = result
        return result

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
            path = os.path.join(cls.ICONS_DIR, "security", "shield.svg")
        return QIcon(path)
