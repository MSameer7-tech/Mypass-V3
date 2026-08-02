"""
3-Layer Favicon Cache (Memory, Disk, Network) with 30-Day TTL and 1-Hour Negative Cache.
"""
import os
import time
from typing import Optional, Dict
from PySide6.QtGui import QPixmap

from utils.helpers import build_data_path
from utils.constants import DATA_DIR_NAME

class IconCache:
    TTL_SECONDS = 30 * 86400        # 30 Days TTL
    NEGATIVE_TTL_SECONDS = 3600    # 1 Hour Negative Cache TTL

    def __init__(self, disk_dir: str = None):
        if not disk_dir:
            disk_dir = build_data_path(DATA_DIR_NAME, "cache", "favicons")
        self.disk_dir = disk_dir
        os.makedirs(self.disk_dir, exist_ok=True)
        
        self._memory_cache: Dict[str, QPixmap] = {}
        self._negative_cache: Dict[str, float] = {}

    def get_memory(self, domain: str) -> Optional[QPixmap]:
        return self._memory_cache.get(domain)

    def get_disk(self, domain: str) -> Optional[QPixmap]:
        filepath = os.path.join(self.disk_dir, f"{domain}.png")
        if not os.path.exists(filepath):
            return None
            
        # Check TTL
        mtime = os.path.getmtime(filepath)
        if (time.time() - mtime) > self.TTL_SECONDS:
            # File expired, but return stale pixmap while background refresh queues
            pixmap = QPixmap(filepath)
            return pixmap if not pixmap.isNull() else None
            
        pixmap = QPixmap(filepath)
        if not pixmap.isNull():
            self._memory_cache[domain] = pixmap
            return pixmap
        return None

    def is_disk_expired(self, domain: str) -> bool:
        filepath = os.path.join(self.disk_dir, f"{domain}.png")
        if not os.path.exists(filepath):
            return True
        return (time.time() - os.path.getmtime(filepath)) > self.TTL_SECONDS

    def save(self, domain: str, pixmap: QPixmap) -> str:
        if not domain or pixmap.isNull():
            return ""
            
        filepath = os.path.join(self.disk_dir, f"{domain}.png")
        pixmap.save(filepath, "PNG")
        self._memory_cache[domain] = pixmap
        
        # Clear negative cache on success
        self._negative_cache.pop(domain, None)
        return filepath

    def record_failure(self, domain: str):
        if domain:
            self._negative_cache[domain] = time.time()

    def is_negative_cached(self, domain: str) -> bool:
        failed_at = self._negative_cache.get(domain)
        if failed_at is None:
            return False
        if (time.time() - failed_at) > self.NEGATIVE_TTL_SECONDS:
            self._negative_cache.pop(domain, None)
            return False
        return True

    def clear(self):
        self._memory_cache.clear()
        self._negative_cache.clear()
