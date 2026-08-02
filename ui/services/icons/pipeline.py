"""
Favicon Pipeline Orchestrator for MyPass.
Implements Domain Normalization, 3-Layer Cache, and Instant Monogram Fallback with Async Background Refreshes.
"""
import urllib.parse
from typing import Optional
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPixmap, QIcon

from ui.services.icons.cache import IconCache
from ui.services.icons.downloader import IconDownloader
from ui.services.icons.monogram_provider import MonogramProvider

def normalize_domain(url: str) -> str:
    """
    Normalizes any URL or raw domain into a clean registrable domain.
    Examples:
      https://github.com/login -> github.com
      https://docs.github.com -> github.com
      https://m.amazon.in -> amazon.in
      https://mail.google.com:8080/inbox?user=1 -> google.com
    """
    if not url:
        return ""
    url = url.strip()
    if "://" not in url:
        url = f"https://{url}"
        
    try:
        parsed = urllib.parse.urlparse(url)
        netloc = parsed.netloc or parsed.path
        # Strip credentials user:pass@
        if "@" in netloc:
            netloc = netloc.split("@")[-1]
        # Strip port
        netloc = netloc.split(":")[0].strip().lower()
        if not netloc:
            return ""
            
        parts = netloc.split(".")
        if len(parts) >= 3:
            # Common subdomains: www, m, docs, mail, login, app
            if parts[0] in ("www", "m", "docs", "mail", "login", "app", "mobile"):
                netloc = ".".join(parts[1:])
        elif len(parts) == 2 and parts[0] == "www":
            netloc = parts[1]
            
        return netloc
    except Exception:
        return ""


class IconPipeline(QObject):
    icon_loaded = Signal(int, str)  # (entry_id, disk_path_or_domain)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cache = IconCache()
        self.downloader = IconDownloader(self.cache)
        self.monogram_provider = MonogramProvider()

    def get_icon_pixmap(self, entry_id: int, url: str, fallback_title: str = "", size: int = 44) -> QPixmap:
        domain = normalize_domain(url)
        
        # 1. Check Memory Cache
        if domain:
            pixmap = self.cache.get_memory(domain)
            if pixmap and not pixmap.isNull():
                return pixmap
                
            # 2. Check Disk Cache
            pixmap = self.cache.get_disk(domain)
            if pixmap and not pixmap.isNull():
                # If disk cache is expired, trigger background refresh asynchronously
                if self.cache.is_disk_expired(domain) and not self.cache.is_negative_cached(domain):
                    self._trigger_async_fetch(domain, url, entry_id)
                return pixmap
                
            # 3. Trigger Async Download if not negative cached
            if not self.cache.is_negative_cached(domain):
                self._trigger_async_fetch(domain, url, entry_id)
                
        # 4. Immediate Fallback Monogram while network loads (Zero UI Blocking!)
        monogram_pixmap = self.monogram_provider.fetch(domain, url, size=size, letter_override=fallback_title)
        return monogram_pixmap or QPixmap()

    def get_icon(self, entry_id: int, url: str, fallback_title: str = "", size: int = 44) -> QIcon:
        pixmap = self.get_icon_pixmap(entry_id, url, fallback_title=fallback_title, size=size)
        return QIcon(pixmap)

    def _trigger_async_fetch(self, domain: str, full_url: str, entry_id: int):
        def _on_download_complete(eid: int, dom: str, disk_path: str):
            self.icon_loaded.emit(eid, disk_path)

        self.downloader.fetch_async(domain, full_url, entry_id, _on_download_complete)
