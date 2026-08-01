from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer
from PySide6.QtGui import QIcon

from ui.services.notification_service import Notification, NotificationLevel
from ui.widgets.base import BaseFrame
from ui.resources.styles.themes import ThemeManager

class ToastWidget(BaseFrame):
    """
    A single notification toast widget.
    """
    def __init__(self, notification: Notification, parent=None):
        super().__init__(parent)
        self.notification = notification
        
        self.setObjectName("ToastWidget")
        
        # Base styling is handled by ThemeManager/QSS, but we might inject dynamic styles
        self._apply_style_based_on_level()
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        c = ThemeManager.colors()
        # Icon
        icon_map = {
            "check-circle": ("✓", c.success),
            "alert-triangle": ("⚠", c.warning),
            "alert-circle": ("✕", c.danger),
            "info": ("ℹ", c.accent),
        }
        level_map = {
            NotificationLevel.SUCCESS: ("✓", c.success),
            NotificationLevel.WARNING: ("⚠", c.warning),
            NotificationLevel.ERROR: ("✕", c.danger),
            NotificationLevel.INFO: ("ℹ", c.accent),
        }
        symbol, color = icon_map.get(
            self.notification.icon,
            level_map.get(self.notification.level, ("ℹ", c.accent)),
        )
        self.icon_label = QLabel(symbol)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {color}26;
                color: {color};
                border-radius: 12px;
                font-weight: bold;
                font-size: 14px;
            }}
        """)
        layout.addWidget(self.icon_label)
            
        # Message Text
        self.msg_label = QLabel(self.notification.message)
        self.msg_label.setWordWrap(True)
        self.msg_label.setStyleSheet(f"color: {c.text_primary}; font-size: 13px; font-weight: 500;")
        layout.addWidget(self.msg_label, 1)
        
        # Optional Actions
        if self.notification.primary_action:
            self.primary_btn = QPushButton(self.notification.primary_action.label)
            self.primary_btn.setCursor(Qt.PointingHandCursor)
            self.primary_btn.clicked.connect(lambda: self._on_action_clicked(self.notification.primary_action))
            layout.addWidget(self.primary_btn)
            
        if self.notification.secondary_action:
            self.secondary_btn = QPushButton(self.notification.secondary_action.label)
            self.secondary_btn.setCursor(Qt.PointingHandCursor)
            self.secondary_btn.clicked.connect(lambda: self._on_action_clicked(self.notification.secondary_action))
            layout.addWidget(self.secondary_btn)
            
        # Optional Close Button (if persistent or explicitly desired, we always add one for safety)
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("ToastCloseButton")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.clicked.connect(self.hide_toast)
        layout.addWidget(self.close_btn)
        
        # Self-destruct timer
        if not self.notification.persistent:
            self.timer = QTimer(self)
            self.timer.setSingleShot(True)
            self.timer.timeout.connect(self.hide_toast)
            self.timer.start(self.notification.duration_ms)
            
    def _apply_style_based_on_level(self):
        c = ThemeManager.colors()
        bg_color = c.surface_elevated
        border_color = c.border
        
        if self.notification.level == NotificationLevel.ERROR:
            border_color = c.danger
        elif self.notification.level == NotificationLevel.WARNING:
            border_color = c.warning
        elif self.notification.level == NotificationLevel.SUCCESS:
            border_color = c.success
            
        self.setStyleSheet(f"""
            #ToastWidget {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
            #ToastCloseButton {{
                background: transparent;
                border: none;
                color: {c.text_secondary};
                font-weight: bold;
            }}
            #ToastCloseButton:hover {{
                color: {c.text_primary};
            }}
        """)
        
    def _on_action_clicked(self, action):
        if action:
            action.execute()
        self.hide_toast()
        
    def hide_toast(self):
        # We notify the manager to remove us
        # Can use a signal or direct call if parent is manager, 
        # but it's cleaner to just deleteLater and let the manager catch it
        self.deleteLater()
