from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Qt

from ui.widgets.base import BaseInput
from ui.resources.styles.widget_names import WidgetNames
from ui.app.resources import Resources
from ui.resources.icons import Icons
from ui.widgets.typography import apply_typography
from ui.resources.styles.typography import Typography

class TextField(BaseInput):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setObjectName(WidgetNames.TEXT_FIELD)
        self.setPlaceholderText(placeholder)
        apply_typography(self, Typography.Body)

class SearchField(TextField):
    def __init__(self, placeholder="Search...", parent=None):
        super().__init__(placeholder, parent)
        self.setObjectName(WidgetNames.SEARCH_FIELD)
        
        # Add a leading search icon accessory
        search_icon = Resources.icon(Icons.SEARCH)
        self.addAction(search_icon, QLineEdit.LeadingPosition)

class PasswordField(TextField):
    def __init__(self, placeholder="Password", parent=None):
        super().__init__(placeholder, parent)
        self.setObjectName(WidgetNames.PASSWORD_FIELD)
        self.setEchoMode(QLineEdit.Password)
        
        # Trailing toggle action
        self.eye_icon = Resources.icon(Icons.EYE)
        self.eye_off_icon = Resources.icon(Icons.EYE_OFF)
        
        self.toggle_action = QAction(self.eye_icon, "", self)
        self.toggle_action.triggered.connect(self.toggle_visibility)
        
        self.addAction(self.toggle_action, QLineEdit.TrailingPosition)
        
    def toggle_visibility(self):
        if self.echoMode() == QLineEdit.Password:
            self.setEchoMode(QLineEdit.Normal)
            self.toggle_action.setIcon(self.eye_off_icon)
        else:
            self.setEchoMode(QLineEdit.Password)
            self.toggle_action.setIcon(self.eye_icon)
