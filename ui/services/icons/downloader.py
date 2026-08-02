"""
Background Favicon Downloader with Request Coalescing and Provider Chaining.
"""
from typing import Callable, Set, Dict, List
from PySide6.QtCore import QRunnable, QThreadPool

from ui.services.icons.website_provider import WebsiteProvider
from ui.services.icons.google_provider import GoogleProvider
from ui.services.icons.monogram_provider import MonogramProvider
from ui.services.icons.cache import IconCache

class FaviconFetchTask(QRunnable):
    def __init__(self, domain: str, full_url: str, entry_ids: List[int], cache: IconCache, callback: Callable):
        super().__init__()
        self.domain = domain
        self.full_url = full_url
        self.entry_ids = entry_ids
        self.cache = cache
        self.callback = callback
        
        self.website_provider = WebsiteProvider()
        self.google_provider = GoogleProvider()
        self.monogram_provider = MonogramProvider()

    def run(self):
        pixmap = None
        real_favicon_downloaded = False
        
        # 1. Primary: Website Provider
        try:
            pixmap = self.website_provider.fetch(self.domain, self.full_url)
            if pixmap and not pixmap.isNull():
                real_favicon_downloaded = True
        except Exception:
            pixmap = None
            
        # 2. Fallback: Google S2 Provider
        if not real_favicon_downloaded:
            try:
                pixmap = self.google_provider.fetch(self.domain, self.full_url)
                if pixmap and not pixmap.isNull():
                    real_favicon_downloaded = True
            except Exception:
                pixmap = None

        if real_favicon_downloaded and pixmap and not pixmap.isNull():
            disk_path = self.cache.save(self.domain, pixmap)
            for eid in self.entry_ids:
                self.callback(eid, self.domain, disk_path)
        else:
            self.cache.record_failure(self.domain)


class IconDownloader:
    def __init__(self, cache: IconCache):
        self.cache = cache
        self.thread_pool = QThreadPool.globalInstance()
        self._pending_domain_entries: Dict[str, List[int]] = {}

    def fetch_async(self, domain: str, full_url: str, entry_id: int, callback: Callable):
        if not domain:
            return
            
        # Request Coalescing: If task for domain already pending, append entry_id
        if domain in self._pending_domain_entries:
            if entry_id not in self._pending_domain_entries[domain]:
                self._pending_domain_entries[domain].append(entry_id)
            return
            
        self._pending_domain_entries[domain] = [entry_id]
        
        def _on_finished(eid: int, dom: str, path: str):
            eids = self._pending_domain_entries.pop(dom, [eid])
            for target_eid in eids:
                callback(target_eid, dom, path)

        task = FaviconFetchTask(
            domain=domain,
            full_url=full_url,
            entry_ids=self._pending_domain_entries[domain],
            cache=self.cache,
            callback=_on_finished
        )
        self.thread_pool.start(task)
