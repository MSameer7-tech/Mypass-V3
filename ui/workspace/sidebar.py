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
        self.icon_label.setPixmap(Resources.icon(item.icon, color_hex=colors.text_secondary).pixmap(16, 16))
        layout.addWidget(self.icon_label)
        
        self.text_label = BodyLabel(item.label)
        layout.addWidget(self.text_label)
        
        layout.addStretch()
        
        self.badge = Badge("", BadgeVariant.NEUTRAL)
        self.badge.setVisible(False)
        layout.addWidget(self.badge)
            
    def set_selected(self, selected: bool):
        self.is_selected = selected
        colors = ThemeManager.colors()
        if selected:
            self.setStyleSheet(f"""
                SidebarItem {{
                    background-color: {colors.accent}24;
                    border-radius: 8px;
                }}
            """)
            self.text_label.setStyleSheet(f"color: {colors.accent}; font-weight: 600;")
            self.icon_label.setPixmap(Resources.icon(self.item.icon, color_hex=colors.accent).pixmap(16, 16))
        else:
            self.setStyleSheet("""
                SidebarItem {
                    background-color: transparent;
                    border-radius: 8px;
                }
                SidebarItem:hover {
                    background-color: rgba(255, 255, 255, 0.05);
                }
            """)
            self.text_label.setStyleSheet(f"color: {colors.text_primary}; font-weight: 400;")
            self.icon_label.setPixmap(Resources.icon(self.item.icon, color_hex=colors.text_secondary).pixmap(16, 16))

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
        self.layout.setContentsMargins(12, 16, 12, 16)
        self.layout.setSpacing(4)
        
        self.widgets: dict[str, SidebarItem] = {}
        self._build_static_items()
        
        # Connect to statistics provider
        self.statistics_provider.counts_updated.connect(self._on_counts_updated)
        
        # Select "all" by default
        self._set_active_selection("all")
        
        # Initial fetch
        self.statistics_provider.recalculate_all()
        self.layout.addStretch()
        
    def _build_static_items(self):
        # Section 1: VAULT
        vault_header = OverlineLabel("VAULT")
        vault_header.setStyleSheet("color: #636366; font-size: 11px; font-weight: 600; padding: 4px 8px;")
        self.layout.addWidget(vault_header)
        
        vault_items = [
            NavItem("all", Icons.VAULT, "All Items", 0),
            NavItem("favorites", Icons.STAR, "Favorites", 0),
        ]
        
        for item in vault_items:
            widget = SidebarItem(item)
            widget.clicked.connect(self._handle_click)
            self.layout.addWidget(widget)
            self.widgets[item.id] = widget
            
        self.layout.addSpacing(12)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: rgba(255, 255, 255, 0.06); max-height: 1px;")
        self.layout.addWidget(divider)
        
        self.layout.addSpacing(12)
        
        # Section 2: CATEGORIES
        cat_header = OverlineLabel("CATEGORIES")
        cat_header.setStyleSheet("color: #636366; font-size: 11px; font-weight: 600; padding: 4px 8px;")
        self.layout.addWidget(cat_header)
        
        cat_items = [
            NavItem("work", Icons.FOLDER, "Work", 0),
            NavItem("personal", Icons.FOLDER, "Personal", 0),
            NavItem("social", Icons.FOLDER, "Social", 0),
            NavItem("finance", Icons.FOLDER, "Finance", 0),
        ]
        
        for item in cat_items:
            widget = SidebarItem(item)
            widget.clicked.connect(self._handle_click)
            self.layout.addWidget(widget)
            self.widgets[item.id] = widget
            
    def _handle_click(self, item_id: str):
        self._set_active_selection(item_id)
        self.nav_item_selected.emit(item_id)
        
        if item_id == "all":
            self.sidebar_controller.select_all_items()
        elif item_id == "favorites":
            self.sidebar_controller.select_favorites()
        elif item_id in ["work", "personal", "social", "finance"]:
            self.sidebar_controller.select_category(item_id.capitalize())
            
    def _set_active_selection(self, selected_id: str):
        for item_id, widget in self.widgets.items():
            widget.set_selected(item_id == selected_id)

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
        
        if hasattr(widget, 'badge'):
            widget.badge.setText(str(count))
            widget.badge.setVisible(count > 0)
