from dataclasses import dataclass
from typing import List, Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, Signal

from ui.widgets.base import BaseFrame
from ui.widgets.buttons import IconButton
from ui.widgets.typography import BodyLabel, OverlineLabel
from ui.widgets.indicators import Badge
from ui.resources.styles.enums import BadgeVariant
from ui.app.resources import Resources
from ui.resources.icons import Icons
from ui.resources.styles.layout_constants import Layout
from ui.resources.styles.metrics import Metrics
from ui.resources.styles.themes import ThemeManager

@dataclass
class NavItem:
    id: str
    icon: str
    label: str
    count: int = 0

class SidebarItem(BaseFrame):
    clicked = Signal(str) # Emits the nav item ID
    
    def __init__(self, item: NavItem, parent=None):
        super().__init__(parent)
        self.item = item
        self.is_selected = False
        self.setObjectName("SidebarItem")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(36)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)
        
        colors = ThemeManager.colors()
        self.icon_label = QLabel()
        self.icon_label.setPixmap(Resources.icon(item.icon, color_hex="#38BDF8").pixmap(16, 16))
        layout.addWidget(self.icon_label)
        
        self.text_label = BodyLabel(item.label)
        layout.addWidget(self.text_label)
        
        layout.addStretch()
        
        self.badge = Badge("", BadgeVariant.NEUTRAL)
        self.badge.setVisible(False)
        layout.addWidget(self.badge)
            
    def set_selected(self, selected: bool):
        self.is_selected = selected
        if selected:
            self.setStyleSheet("""
                SidebarItem {
                    background-color: #1F69FF;
                    border-radius: 8px;
                }
            """)
            self.text_label.setStyleSheet("color: #FFFFFF; font-weight: 600;")
            self.icon_label.setPixmap(Resources.icon(self.item.icon, color_hex="#FFFFFF").pixmap(16, 16))
        else:
            self.setStyleSheet("""
                SidebarItem {
                    background-color: transparent;
                    border-radius: 8px;
                }
                SidebarItem:hover {
                    background-color: rgba(255, 255, 255, 0.06);
                }
            """)
            self.text_label.setStyleSheet("color: #E2E8F0; font-weight: 400;")
            self.icon_label.setPixmap(Resources.icon(self.item.icon, color_hex="#38BDF8").pixmap(16, 16))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.item.id)
        super().mousePressEvent(event)

class Sidebar(BaseFrame):
    nav_item_selected = Signal(str)
    
    def __init__(self, sidebar_controller, statistics_provider, parent=None):
        super().__init__(parent)
        self.sidebar_controller = sidebar_controller
        self.statistics_provider = statistics_provider
        self.setObjectName("Sidebar")
        
        # 1. Fixed width 240px & full-height container styling matching reference image
        self.setFixedWidth(240)
        self.setStyleSheet("""
            QFrame#Sidebar {
                background-color: #1B1C21;
                border: none;
            }
        """)
        
        # 2. Vertical layout scaffold with generous internal padding (18px horizontal, 20px top)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(18, 20, 18, 20)
        self.layout.setSpacing(16)
        
        self.widgets: dict[str, QWidget] = {}
        
        # 3. Add stretch scaffold for Phase A.1
        self.layout.addStretch()
        
        # Connect to statistics provider (no-op until nav items are added in Phase A.2)
        self.statistics_provider.counts_updated.connect(self._on_counts_updated)
        self.statistics_provider.recalculate_all()
        
    def _on_counts_updated(self, stats: dict):
        pass

    def _handle_click(self, item_id: str):
        self.nav_item_selected.emit(item_id)
