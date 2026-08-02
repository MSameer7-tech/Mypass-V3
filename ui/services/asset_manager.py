"""
Centralized AssetManager for MyPass.
Responsible for icon lookup, theme tinting, caching, and fallback behavior.
No UI component may reference SVG filenames, filesystem paths, or color values directly.
"""
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon, QPixmap

from ui.app.resources import Resources
from ui.services.icons.pipeline import IconPipeline, normalize_domain

class AssetManager(QObject):
    """
    Centralized manager for all icons, favicons, avatars, and visual assets.
    Exposes IconPipeline to UI views while maintaining complete backwards compatibility.
    """
    icon_loaded = Signal(int, str)  # (entry_id, icon_path_or_domain)
    _instance = None
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pipeline = IconPipeline(self)
        self.pipeline.icon_loaded.connect(self._on_pipeline_icon_loaded)
        AssetManager._instance = self

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
        
    @classmethod
    def icon(cls, identifier: str, color_hex: str = None) -> QIcon:
        """
        Returns a QIcon for a semantic Icons identifier.
        Automatically tints to theme text_primary if color_hex is None.
        """
        return Resources.icon(identifier, color_hex=color_hex)

    def _on_pipeline_icon_loaded(self, entry_id: int, disk_path: str):
        self.icon_loaded.emit(entry_id, disk_path)

    def request_website_icon(self, entry_id: int, url: str, fallback_title: str = "", size: int = 44) -> QPixmap:
        """Single entry point for requesting website favicons/monograms as QPixmap."""
        return self.pipeline.get_icon_pixmap(entry_id, url, fallback_title=fallback_title, size=size)

    def get_favicon(self, entry_id: int, url: str, fallback_title: str = "", size: int = 44, *args, **kwargs) -> QIcon:
        """Returns cached favicon if available in Memory or Disk; otherwise returns instant monogram."""
        return self.pipeline.get_icon(entry_id, url, fallback_title=fallback_title, size=size)

    def get_monogram_icon(self, letter: str, size: int = 24, color_hex: str = None) -> QIcon:
        """Generates a crisp monogram letter badge as a QIcon."""
        pixmap = self.pipeline.monogram_provider.fetch(domain="", size=size, letter_override=letter)
        return QIcon(pixmap or QPixmap())

    def get_icon(self, *args, **kwargs):
        """Backwards-compatible alias for get_favicon."""
        return self.get_favicon(*args, **kwargs)
