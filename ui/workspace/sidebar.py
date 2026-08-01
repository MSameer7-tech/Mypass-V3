from dataclasses import dataclass
from typing import List, Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, Signal

from ui.widgets.base import BaseFrame
from ui.widgets.buttons import IconButton
from ui.widgets.typography import BodyLabel, CaptionLabel
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
        self.setObjectName("SidebarItem")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(Metrics.SIDEBAR_ITEM_HEIGHT)
        
        # We need a custom style for the hovered/selected states, so we rely on QSS
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(Layout.BUTTON_GROUP_GAP, 0, Layout.BUTTON_GROUP_GAP, 0) # 12, 0, 12, 0
        layout.setSpacing(Layout.BUTTON_GROUP_GAP)
        
        colors = ThemeManager.colors()
        self.icon_label = QLabel()
        self.icon_label.setPixmap(Resources.icon(item.icon, color_hex=colors.text_secondary).pixmap(18, 18))
        layout.addWidget(self.icon_label)
        
        self.text_label = BodyLabel(item.label)
        layout.addWidget(self.text_label)
        
        layout.addStretch()
        
        if item.count > 0:
            self.badge = Badge(str(item.count), BadgeVariant.NEUTRAL)
            layout.addWidget(self.badge)
            
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
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(Layout.BUTTON_GROUP_GAP, Layout.SIDEBAR_MARGIN, Layout.BUTTON_GROUP_GAP, Layout.SIDEBAR_MARGIN)
        self.layout.setSpacing(Layout.LIST_ITEM_GAP)
        
        self.widgets: dict[str, SidebarItem] = {}
        self._build_static_items()
        
        # Connect to statistics provider
        self.statistics_provider.counts_updated.connect(self._on_counts_updated)
        
        # Initial fetch
        self.statistics_provider.recalculate_all()
        self.layout.addStretch()
        
    def _build_static_items(self):
        # Base items without counts (counts injected later)
        items = [
            NavItem("all", Icons.VAULT, "All Items", 0),
            NavItem("favorites", Icons.STAR, "Favorites", 0),
            NavItem("work", Icons.FOLDER, "Work", 0),
            NavItem("personal", Icons.FOLDER, "Personal", 0),
            NavItem("social", Icons.FOLDER, "Social", 0),
            NavItem("finance", Icons.FOLDER, "Finance", 0),
        ]
        
        for item in items:
            widget = SidebarItem(item)
            widget.clicked.connect(self._handle_click)
            self.layout.addWidget(widget)
            self.widgets[item.id] = widget
            
    def _handle_click(self, item_id: str):
        self.nav_item_selected.emit(item_id)
        
        if item_id == "all":
            self.sidebar_controller.select_all_items()
        elif item_id == "favorites":
            self.sidebar_controller.select_favorites()
        elif item_id in ["work", "personal", "social", "finance"]:
            self.sidebar_controller.select_category(item_id.capitalize())
            
    def _on_counts_updated(self, stats: dict):
        total = stats.get('total', 0)
        favs = stats.get('favorites', 0)
        cats = stats.get('categories', {})
        
        if "all" in self.widgets:
            self._update_widget_count("all", total)
        if "favorites" in self.widgets:
            self._update_widget_count("favorites", favs)
            
        for cat_id in ["work", "personal", "social", "finance"]:
            if cat_id in self.widgets:
                self._update_widget_count(cat_id, cats.get(cat_id.capitalize(), 0))
                
    def _update_widget_count(self, item_id: str, count: int):
        widget = self.widgets[item_id]
        widget.item.count = count
        
        # Re-render the badge
        if hasattr(widget, 'badge'):
            widget.badge.setText(str(count))
            widget.badge.setVisible(count > 0)
        elif count > 0:
            widget.badge = Badge(str(count), BadgeVariant.NEUTRAL)
            widget.layout().addWidget(widget.badge)
