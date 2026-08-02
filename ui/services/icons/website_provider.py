"""
Primary Favicon Provider: Website Direct HTML/Favicon Fetch.
Parses HTML <link rel="icon">, <link rel="apple-touch-icon">, or falls back to /favicon.ico directly.
"""
import re
import urllib.request
import urllib.parse
from typing import Optional
from PySide6.QtGui import QPixmap

from ui.services.icons.provider import IconProvider

class WebsiteProvider(IconProvider):
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    MAX_DOWNLOAD_SIZE = 2 * 1024 * 1024  # 2 MB limit
    TIMEOUT = 3.0                        # 3.0s timeout

    def fetch(self, domain: str, full_url: str = "") -> Optional[QPixmap]:
        if not domain:
            return None
            
        base_url = full_url if full_url and full_url.startswith("http") else f"https://{domain}"
        
        # 1. Try parsing HTML <link> tags first
        icon_url = self._extract_icon_link(base_url)
        if icon_url:
            pixmap = self._download_pixmap(icon_url)
            if pixmap and not pixmap.isNull() and pixmap.width() >= 8:
                return pixmap
                
        # 2. Direct fallback to https://domain/favicon.ico
        fallback_ico_url = f"https://{domain}/favicon.ico"
        pixmap = self._download_pixmap(fallback_ico_url)
        if pixmap and not pixmap.isNull() and pixmap.width() >= 8:
            return pixmap
            
        return None

    def _extract_icon_link(self, page_url: str) -> Optional[str]:
        try:
            req = urllib.request.Request(page_url, headers={'User-Agent': self.USER_AGENT})
            with urllib.request.urlopen(req, timeout=self.TIMEOUT) as resp:
                # Limit HTML read to first 64KB for speed and safety
                content = resp.read(65536).decode('utf-8', errors='ignore')
                
            # Regex match <link ... rel="(icon|shortcut icon|apple-touch-icon|mask-icon)" ... href="...">
            pattern = re.compile(
                r'<link\s+[^>]*?rel=["\']?(?:shortcut\s+)?(?:apple-touch-)?icon["\']?[^>]*?href=["\']?([^"\'\s>]+)["\']?',
                re.IGNORECASE
            )
            match = pattern.search(content)
            if match:
                href = match.group(1).strip()
                return urllib.parse.urljoin(page_url, href)
        except Exception:
            pass
        return None

    def _download_pixmap(self, url: str) -> Optional[QPixmap]:
        try:
            req = urllib.request.Request(url, headers={'User-Agent': self.USER_AGENT})
            with urllib.request.urlopen(req, timeout=self.TIMEOUT) as resp:
                data = resp.read(self.MAX_DOWNLOAD_SIZE)
                if data and len(data) > 64:
                    pixmap = QPixmap()
                    if pixmap.loadFromData(data) and not pixmap.isNull():
                        return pixmap
        except Exception:
            pass
        return None
