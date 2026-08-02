"""
Fallback Favicon Provider: Google S2 Favicon API.
Queries https://www.google.com/s2/favicons?domain=<domain>&sz=64.
"""
import urllib.request
import urllib.parse
from typing import Optional
from PySide6.QtGui import QPixmap

from ui.services.icons.provider import IconProvider

class GoogleProvider(IconProvider):
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    TIMEOUT = 3.0
    MAX_SIZE = 500 * 1024  # 500 KB limit

    def fetch(self, domain: str, full_url: str = "") -> Optional[QPixmap]:
        if not domain:
            return None
            
        url = f"https://www.google.com/s2/favicons?domain={urllib.parse.quote(domain)}&sz=64"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': self.USER_AGENT})
            with urllib.request.urlopen(req, timeout=self.TIMEOUT) as resp:
                data = resp.read(self.MAX_SIZE)
                if data and len(data) > 64:
                    pixmap = QPixmap()
                    if pixmap.loadFromData(data) and not pixmap.isNull() and pixmap.width() >= 8:
                        return pixmap
        except Exception:
            pass
        return None
