from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt, Signal

from ui.widgets.base import BaseFrame
from ui.widgets.buttons import PrimaryButton, SecondaryButton
from ui.widgets.typography import HeadlineLabel, BodyLabel

class ErrorView(BaseFrame):
    primary_action_clicked = Signal()
    secondary_action_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ErrorView")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(24)
        
        container = QWidget()
        container.setFixedWidth(400)
        c_layout = QVBoxLayout(container)
        c_layout.setSpacing(16)
        
        # We can add an icon/illustration here later
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(self.icon_label)
        
        self.title = HeadlineLabel("Error")
        self.title.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(self.title)
        
        self.message = BodyLabel("An unknown error occurred.")
        self.message.setAlignment(Qt.AlignCenter)
        self.message.setWordWrap(True)
        c_layout.addWidget(self.message)
        
        btn_layout = QHBoxLayout()
        self.secondary_btn = SecondaryButton("Cancel")
        self.primary_btn = PrimaryButton("Retry")
        
        self.secondary_btn.clicked.connect(self.secondary_action_clicked.emit)
        self.primary_btn.clicked.connect(self.primary_action_clicked.emit)
        
        btn_layout.addWidget(self.secondary_btn)
        btn_layout.addWidget(self.primary_btn)
        c_layout.addLayout(btn_layout)
        
        layout.addWidget(container)
        
    def configure(self, title: str, message: str, primary_text: str, secondary_text: str = None):
        self.title.setText(title)
        self.message.setText(message)
        self.primary_btn.setText(primary_text)
        
        if secondary_text:
            self.secondary_btn.setText(secondary_text)
            self.secondary_btn.show()
        else:
            self.secondary_btn.hide()
