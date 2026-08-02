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
    has_chevron: bool = False
    is_category: bool = False

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
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(18, 18)
        self.icon_label.setPixmap(Resources.icon(item.icon, color_hex="#38BDF8").pixmap(18, 18))
        layout.addWidget(self.icon_label)
        
        self.text_label = BodyLabel(item.label)
        self.text_label.setStyleSheet("color: #E2E8F0; font-size: 14px; font-weight: 500; border: none; background: transparent;")
        layout.addWidget(self.text_label)
        
        layout.addStretch()
        
        self.badge_label = QLabel()
        self.badge_label.setStyleSheet("color: #9498A6; font-size: 13px; font-weight: 500; border: none; background: transparent;")
        self.badge_label.setVisible(False)
        layout.addWidget(self.badge_label)
        
        if item.has_chevron:
            self.chevron_label = QLabel()
            self.chevron_label.setFixedSize(14, 14)
            self.chevron_label.setPixmap(Resources.icon(Icons.CHEVRON_DOWN, color_hex="#71717A").pixmap(14, 14))
            layout.addWidget(self.chevron_label)
        else:
            self.chevron_label = None
            
        from PySide6.QtCore import QVariantAnimation, QAbstractAnimation
        from PySide6.QtGui import QColor
        self.anim = QVariantAnimation(self)
        self.anim.setDuration(120)
        self.anim.valueChanged.connect(self._on_anim_value_changed)
        self._target_bg = QColor(0, 0, 0, 0)

    def _on_anim_value_changed(self, value):
        col = value
        self.setStyleSheet(f"""
            SidebarItem {{
                background-color: rgba({col.red()}, {col.green()}, {col.blue()}, {col.alphaF()});
                border-radius: 8px;
                border: none;
            }}
        """)

    def set_selected(self, selected: bool):
        from PySide6.QtGui import QColor
        self.is_selected = selected
        
        if selected:
            if self.item.is_category:
                bg_color = QColor("#2563EB") # Vibrant reference blue pill
            else:
                bg_color = QColor("#2D3039") # Dark reference primary nav pill
                
            icon_hex = "#FFFFFF" # Crisp white icon ONLY for active item
            chevron_hex = "#FFFFFF"
                
            self.text_label.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: 500; border: none; background: transparent;")
            self.icon_label.setPixmap(Resources.icon(self.item.icon, color_hex=icon_hex).pixmap(18, 18))
            if self.chevron_label:
                self.chevron_label.setPixmap(Resources.icon(Icons.CHEVRON_DOWN, color_hex=chevron_hex).pixmap(14, 14))
                
            self.anim.stop()
            self.anim.setStartValue(QColor(0, 0, 0, 0))
            self.anim.setEndValue(bg_color)
            self.anim.start()
        else:
            self.text_label.setStyleSheet("color: #E2E8F0; font-size: 14px; font-weight: 500; border: none; background: transparent;")
            self.icon_label.setPixmap(Resources.icon(self.item.icon, color_hex="#38BDF8").pixmap(18, 18)) # Accent blue for inactive icons
            if self.chevron_label:
                self.chevron_label.setPixmap(Resources.icon(Icons.CHEVRON_DOWN, color_hex="#71717A").pixmap(14, 14))
                
            self.setStyleSheet("""
                SidebarItem {
                    background-color: transparent;
                    border-radius: 8px;
                    border: none;
                }
                SidebarItem:hover {
                    background-color: rgba(255, 255, 255, 0.05);
                }
            """)

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
        
        # 2. Vertical layout with calibrated margins (16px horizontal, 24px top padding)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 24, 16, 16)
        self.layout.setSpacing(2)
        
        # 3. Phase A.2 Logo Header (36x36 circular avatar + "MyPass v2" title)
        header_box = QHBoxLayout()
        header_box.setContentsMargins(0, 0, 0, 0)
        header_box.setSpacing(12)
        
        # 36x36 Circular User Avatar
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(36, 36)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.12);
                border-radius: 18px;
                border: none;
            }
        """)
        self.avatar_label.setPixmap(Resources.icon(Icons.USER, color_hex="#CCCCCC").pixmap(20, 20))
        
        # Title "MyPass v2"
        self.title_label = BodyLabel("MyPass v2")
        self.title_label.setStyleSheet("color: #FFFFFF; font-size: 15px; font-weight: 600; border: none; background: transparent;")
        
        header_box.addWidget(self.avatar_label)
        header_box.addWidget(self.title_label)
        header_box.addStretch()
        
        self.layout.addLayout(header_box)
        
        # 20px Spacing below header before primary navigation begins
        self.layout.addSpacing(20)
        
        # 4. Phase A.3 Primary Navigation Group
        self.widgets: dict[str, SidebarItem] = {}
        primary_items = [
            NavItem("all", Icons.KEY, "All Items", 0),
            NavItem("favorites", Icons.STAR, "Favorites", 0),
            NavItem("recents", Icons.CLOCK, "Recents", 0),
        ]
        
        for item in primary_items:
            w = SidebarItem(item)
            w.clicked.connect(self._handle_click)
            self.layout.addWidget(w)
            self.widgets[item.id] = w
            
        # 5. Phase A.4 & A.7 Categories Section (including Trash)
        self.layout.addSpacing(24)
        
        cat_hdr = BodyLabel("Categories")
        cat_hdr.setStyleSheet("color: #9498A6; font-size: 13px; font-weight: 500; padding: 4px 12px 6px 12px; border: none; background: transparent;")
        self.layout.addWidget(cat_hdr)
        
        category_items = [
            NavItem("personal", Icons.HOME, "Personal", 0, has_chevron=True, is_category=True),
            NavItem("work", Icons.BRIEFCASE, "Work", 0, has_chevron=True, is_category=True),
            NavItem("banking", Icons.CREDIT_CARD, "Banking", 0, has_chevron=True, is_category=True),
            NavItem("trash", Icons.TRASH, "Trash", 0, has_chevron=False, is_category=True),
        ]
        
        for item in category_items:
            w = SidebarItem(item)
            w.clicked.connect(self._handle_click)
            self.layout.addWidget(w)
            self.widgets[item.id] = w
            
        self._set_active_selection("work") # Work category active by default matching reference image
        
        self.layout.addStretch()
        
        # Connect to statistics provider
        self.statistics_provider.counts_updated.connect(self._on_counts_updated)
        self.statistics_provider.recalculate_all()
        
    def _handle_click(self, item_id: str):
        self._set_active_selection(item_id)
        self.nav_item_selected.emit(item_id)
        
        if item_id == "all":
            self.sidebar_controller.select_all_items()
        elif item_id == "favorites":
            self.sidebar_controller.select_favorites()
        elif item_id in ["personal", "work", "banking"]:
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
            
        for cat_id in ["personal", "work", "banking"]:
            if cat_id in self.widgets:
                self._update_widget_count(cat_id, cats.get(cat_id.capitalize(), 0))

    def _update_widget_count(self, item_id: str, count: int):
        widget = self.widgets[item_id]
        widget.item.count = count
        if hasattr(widget, 'badge_label'):
            widget.badge_label.setText(str(count))
            widget.badge_label.setVisible(count > 0)
