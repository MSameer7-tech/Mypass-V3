"""
Centralized AssetManager for MyPass.
Responsible for icon lookup, theme tinting, caching, and fallback behavior.
No UI component may reference SVG filenames, filesystem paths, or color values directly.
"""
import os
import urllib.request
import urllib.parse
from urllib.error import URLError, HTTPError
from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool, Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont

from ui.app.resources import Resources
from ui.resources.styles.themes import ThemeManager
from utils.helpers import build_data_path
from utils.constants import DATA_DIR_NAME

class FaviconFetchTask(QRunnable):
    def __init__(self, domain: str, entry_id: int, cache_dir: str, callback):
        super().__init__()
        self.domain = domain
        self.entry_id = entry_id
        self.cache_dir = cache_dir
        self.callback = callback
        
    def run(self):
        # Ensure disk cache dir exists
        os.makedirs(self.cache_dir, exist_ok=True)
        disk_path = os.path.join(self.cache_dir, f"{self.domain}.png")
        
        # Try Provider 1: Google S2
        urls_to_try = [
            f"https://www.google.com/s2/favicons?domain={urllib.parse.quote(self.domain)}&sz=64",
            f"https://icons.duckduckgo.com/ip3/{urllib.parse.quote(self.domain)}.ico"
        ]
        
        for url in urls_to_try:
            try:
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
                )
                with urllib.request.urlopen(req, timeout=3.0) as resp:
                    data = resp.read()
                    if data and len(data) > 100: # Ensure valid image data
                        with open(disk_path, "wb") as f:
                            f.write(data)
                        self.callback(self.entry_id, self.domain, disk_path)
                        return
            except (URLError, HTTPError, Exception):
                continue
                
        # If network fail, no callback needed; UI already displays monogram fallback


class AssetManager(QObject):
    """
    Centralized manager for all icons, favicons, avatars, and visual assets.
    Implements Memory -> Disk -> Network -> Monogram fallback hierarchy.
    """
    icon_loaded = Signal(int, str)  # (entry_id, icon_path_or_domain)
    _instance = None
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._memory_cache: dict[str, QIcon] = {}
        self._disk_cache_dir = build_data_path(DATA_DIR_NAME, "cache", "icons")
        self._thread_pool = QThreadPool.globalInstance()
        self._pending_fetches: set[str] = set()
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
        
    def get_favicon(self, entry_id: int, url: str, fallback_title: str = "", size: int = 24) -> QIcon:
        """
        Returns cached favicon if available in Memory or Disk.
        Otherwise immediately returns a monogram QIcon and initiates async fetch.
        """
        domain = self._extract_domain(url)
        if not domain:
            return self.get_monogram_icon(fallback_title or "V", size=size)
            
        cache_key = f"fav_{domain}_{size}"
        
        # 1. Memory Cache
        if cache_key in self._memory_cache:
            return self._memory_cache[cache_key]
            
        # 2. Disk Cache
        disk_path = os.path.join(self._disk_cache_dir, f"{domain}.png")
        if os.path.exists(disk_path):
            pixmap = QPixmap(disk_path)
            if not pixmap.isNull():
                icon = QIcon(pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self._memory_cache[cache_key] = icon
                return icon
                
        # 3. Network Fetch (if not already pending)
        if domain not in self._pending_fetches:
            self._pending_fetches.add(domain)
            self._fetch_favicon_async(domain, entry_id)
            
        # 4. Monogram Fallback Immediately
        monogram = self.get_monogram_icon(fallback_title or domain, size=size)
        return monogram
        
    def get_monogram_icon(self, text: str, size: int = 48, color_hex: str = None) -> QIcon:
        """Generates a crisp monogram QIcon badge with the first letter of text."""
        if not text:
            text = "V"
        letter = text[0].upper()
        
        try:
            bg_color = QColor(ThemeManager.colors().surface_elevated)
            fg_color = QColor(ThemeManager.colors().accent)
        except Exception:
            bg_color = QColor("#2D3748")
            fg_color = QColor("#3182CE")
            
        if color_hex:
            fg_color = QColor(color_hex)
            
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # Draw rounded background badge
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        radius = max(4, size // 4)
        painter.drawRoundedRect(0, 0, size, size, radius, radius)
        
        # Draw bold letter
        font = QFont("SF Pro Display", max(10, size // 2), QFont.Bold)
        painter.setFont(font)
        painter.setPen(fg_color)
        painter.drawText(0, 0, size, size, Qt.AlignCenter, letter)
        painter.end()
        
        return QIcon(pixmap)
        
    def _extract_domain(self, url: str) -> str:
        if not url:
            return ""
        url = url.strip()
        if "://" not in url:
            url = f"https://{url}"
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc or parsed.path
            domain = domain.split(":")[0].strip()
            if domain.startswith("www."):
                domain = domain[4:]
            return domain.lower()
        except Exception:
            return ""
            
    def _fetch_favicon_async(self, domain: str, entry_id: int):
        def _on_fetched(eid, dom, disk_path):
            if dom in self._pending_fetches:
                self._pending_fetches.discard(dom)
            # Clear memory cache for this domain so next read picks up disk file
            keys_to_clear = [k for k in self._memory_cache if k.startswith(f"fav_{dom}")]
            for k in keys_to_clear:
                self._memory_cache.pop(k, None)
            self.icon_loaded.emit(eid, disk_path)
            
        task = FaviconFetchTask(domain, entry_id, self._disk_cache_dir, _on_fetched)
        self._thread_pool.start(task)
