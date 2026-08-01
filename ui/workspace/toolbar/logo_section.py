from PySide6.QtWidgets import QHBoxLayout, QWidget
from ui.widgets.buttons import IconButton
from ui.widgets.typography import BodyLabel
from ui.resources.styles.layout_constants import Layout

class LogoSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(Layout.BUTTON_GROUP_GAP)
        
        self.logo_btn = IconButton("shield")
        self.logo_btn.setEnabled(False) # Decorative
        
        # Using BodyLabel to make it smaller as requested
        self.title = BodyLabel("MyPass")
        
        layout.addWidget(self.logo_btn)
        layout.addWidget(self.title)
