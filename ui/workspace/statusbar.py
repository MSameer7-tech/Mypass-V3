from PySide6.QtWidgets import QHBoxLayout
from PySide6.QtCore import Qt

from ui.widgets.base import BaseFrame
from ui.widgets.typography import CaptionLabel

class StatusBar(BaseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("StatusBar")
        self.setFixedHeight(32)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 0, 16, 0)
        
        # --- LEFT ZONE ---
        self.left_label = CaptionLabel("Ready")
        
        # --- CENTER ZONE ---
        self.center_label = CaptionLabel("")
        self.center_label.setAlignment(Qt.AlignCenter)
        
        # --- RIGHT ZONE ---
        self.right_label = CaptionLabel("Vault Locked | Offline")
        self.right_label.setAlignment(Qt.AlignRight)
        
        main_layout.addWidget(self.left_label, 1)
        main_layout.addWidget(self.center_label, 1)
        main_layout.addWidget(self.right_label, 1)
