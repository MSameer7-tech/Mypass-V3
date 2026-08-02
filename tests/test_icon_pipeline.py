import sys
import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QIcon

from ui.services.icons.pipeline import IconPipeline, normalize_domain
from ui.services.icons.cache import IconCache
from ui.services.icons.downloader import IconDownloader
from ui.services.icons.monogram_provider import MonogramProvider
from ui.services.asset_manager import AssetManager

@pytest.fixture(autouse=True)
def init_qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app

def test_normalize_domain():
    assert normalize_domain("https://github.com/login") == "github.com"
    assert normalize_domain("https://docs.github.com") == "github.com"
    assert normalize_domain("https://m.amazon.in") == "amazon.in"
    assert normalize_domain("https://mail.google.com:8080/inbox?user=1") == "google.com"
    assert normalize_domain("github.com") == "github.com"
    assert normalize_domain("") == ""

def test_monogram_provider():
    provider = MonogramProvider()
    pixmap = provider.fetch("github.com", size=64)
    assert isinstance(pixmap, QPixmap)
    assert not pixmap.isNull()
    assert pixmap.width() == 64
    assert pixmap.height() == 64

def test_cache_memory_and_disk(tmp_path):
    cache = IconCache(disk_dir=str(tmp_path))
    
    # Check initial empty
    assert cache.get_memory("example.com") is None
    assert cache.get_disk("example.com") is None
    
    # Save pixmap
    pm = QPixmap(32, 32)
    pm.fill()
    cache.save("example.com", pm)
    
    # Check memory and disk hits
    assert cache.get_memory("example.com") is not None
    assert cache.get_disk("example.com") is not None

def test_negative_cache(tmp_path):
    cache = IconCache(disk_dir=str(tmp_path))
    assert not cache.is_negative_cached("failed.domain")
    
    cache.record_failure("failed.domain")
    assert cache.is_negative_cached("failed.domain")

def test_request_coalescing(tmp_path):
    cache = IconCache(disk_dir=str(tmp_path))
    downloader = IconDownloader(cache)
    
    callbacks_called = []
    def _cb(eid, dom, path):
        callbacks_called.append((eid, dom))
        
    downloader.fetch_async("coalesce.domain", "https://coalesce.domain", 101, _cb)
    downloader.fetch_async("coalesce.domain", "https://coalesce.domain", 102, _cb)
    
    # Pending dictionary should coalesce into 1 entry with 2 IDs
    assert "coalesce.domain" in downloader._pending_domain_entries
    assert downloader._pending_domain_entries["coalesce.domain"] == [101, 102]

def test_pipeline_instant_fallback():
    pipeline = IconPipeline()
    # For an uncached domain, it returns a monogram QPixmap immediately (0ms UI wait)
    pixmap = pipeline.get_icon_pixmap(1, "https://github.com/login", fallback_title="GitHub", size=44)
    assert isinstance(pixmap, QPixmap)
    assert not pixmap.isNull()

def test_asset_manager_integration():
    manager = AssetManager.instance()
    icon = manager.request_website_icon(1, "https://amazon.com", fallback_title="Amazon", size=44)
    assert isinstance(icon, QPixmap)
    assert not icon.isNull()
