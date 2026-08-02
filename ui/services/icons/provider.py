"""
Abstract base class for favicon providers.
Providers MUST NOT touch Qt UI widgets; they return QPixmap or None.
"""
from abc import ABC, abstractmethod
from typing import Optional
from PySide6.QtGui import QPixmap

class IconProvider(ABC):
    @abstractmethod
    def fetch(self, domain: str, full_url: str = "") -> Optional[QPixmap]:
        """
        Fetch QPixmap for the given domain or URL.
        Returns QPixmap on success, or None on failure.
        """
        pass
