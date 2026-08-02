"""
Local Monogram Provider (Zero Network).
Generates a crisp rounded-square monogram icon with initial letter in theme-aware colors.
"""
import hashlib
from typing import Optional
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont

from ui.services.icons.provider import IconProvider
from ui.resources.styles.themes import ThemeManager

class MonogramProvider(IconProvider):
    # Palette of clean dark-theme friendly accent colors
    PALETTE = [
        "#3B82F6", # Blue
        "#10B981", # Emerald
        "#8B5CF6", # Violet
        "#F59E0B", # Amber
        "#EC4899", # Pink
        "#6366F1", # Indigo
        "#14B8A6", # Teal
        "#F97316", # Orange
    ]

    def fetch(self, domain: str, full_url: str = "", size: int = 64, letter_override: str = "") -> Optional[QPixmap]:
        letter = letter_override
        if not letter and domain:
            letter = domain[0]
        if not letter:
            letter = "V"
        letter = letter[0].upper()
        
        # Pick background color deterministically from domain name
        color_idx = int(hashlib.md5((domain or letter).encode('utf-8')).hexdigest(), 16) % len(self.PALETTE)
        bg_hex = self.PALETTE[color_idx]
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        # Draw rounded square container (radius = size / 4)
        bg_color = QColor(bg_hex)
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        radius = max(6, size // 4)
        painter.drawRoundedRect(0, 0, size, size, radius, radius)
        
        # Draw bold letter
        font = QFont("SF Pro Display", max(14, int(size * 0.45)), QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(QRect(0, 0, size, size), Qt.AlignCenter, letter)
        painter.end()
        
        return pixmap
