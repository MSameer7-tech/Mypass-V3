from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class LoginView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        label = QLabel("MyPass Login View\n(Phase 0 Qt App Bootstrap)", self)
        label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(label)
