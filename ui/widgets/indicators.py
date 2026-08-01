from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt
from typing import Optional

from ui.widgets.base import BaseWidget, BaseLabel
from ui.widgets.typography import DisplayLabel, HeadlineLabel, BodyLabel, TitleLabel
from ui.resources.styles.widget_names import WidgetNames
from ui.resources.styles.enums import BadgeVariant
from ui.app.resources import Resources
from ui.resources.styles.themes import ThemeManager

class Badge(BaseLabel):
    def __init__(self, text: str, variant: BadgeVariant = BadgeVariant.NEUTRAL, parent=None):
        super().__init__(text, parent)
        self.setObjectName(WidgetNames.BADGE)
        self.setProperty("variant", variant.value)
        self.setAlignment(Qt.AlignCenter)

class LoadingIndicator(BaseWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName(WidgetNames.LOADING_INDICATOR)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress = QProgressBar(self)
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 0) # Indeterminate
        
        layout.addWidget(self.progress)

class EmptyState(BaseWidget):
    def __init__(
        self, 
        icon_name: str, 
        title: str, 
        description: str, 
        action_button: Optional[QWidget] = None,
        secondary_action: Optional[QWidget] = None,
        parent=None
    ):
        super().__init__(parent)
        self.setObjectName(WidgetNames.EMPTY_STATE)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)
        
        # Icon / Emoji
        self.icon_label = QLabel(self)
        self.icon_label.setAlignment(Qt.AlignCenter)
        if len(icon_name) <= 2:
            font = self.font()
            font.setPointSize(36)
            self.icon_label.setFont(font)
            self.icon_label.setText(icon_name)
        else:
            colors = ThemeManager.colors()
            self.icon_label.setPixmap(Resources.icon(icon_name, color_hex=colors.text_tertiary).pixmap(48, 48))
        layout.addWidget(self.icon_label)
        
        # Title
        self.title_label = TitleLabel(title, self)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Description
        self.desc_label = BodyLabel(description, self)
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setWordWrap(True)
        layout.addWidget(self.desc_label)
        
        # Actions
        if action_button or secondary_action:
            actions_layout = QHBoxLayout()
            actions_layout.setAlignment(Qt.AlignCenter)
            actions_layout.setSpacing(12)
            if secondary_action:
                actions_layout.addWidget(secondary_action)
            if action_button:
                actions_layout.addWidget(action_button)
            layout.addLayout(actions_layout)
