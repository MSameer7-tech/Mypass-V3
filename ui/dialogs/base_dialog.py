from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QFrame
from PySide6.QtCore import Qt
from ui.widgets.typography import TitleLabel

class BaseDialog(QDialog):
    """
    A consistently styled base dialog for MyPass.
    Follows standard layout:
    [ Header ]
    ----------
    [ Content ]
    ----------
    [ Buttons ]
    """
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container with styling
        self.container = QFrame(self)
        self.container.setObjectName("DialogContainer")
        self.container.setStyleSheet("""
            #DialogContainer {
                background-color: #1E1E1E;
                border-radius: 12px;
                border: 1px solid #333333;
            }
        """)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(24, 24, 24, 24)
        self.container_layout.setSpacing(16)
        
        self.main_layout.addWidget(self.container)
        
        # Header
        self.header_layout = QHBoxLayout()
        if title:
            self.title_label = TitleLabel(title)
            self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch()
        
        # Separator 1
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.HLine)
        sep1.setStyleSheet("background-color: #333333;")
        sep1.setFixedHeight(1)
        
        # Content Area
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 8, 0, 8)
        
        # Separator 2
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet("background-color: #333333;")
        sep2.setFixedHeight(1)
        
        # Footer
        self.footer_layout = QHBoxLayout()
        self.footer_layout.addStretch()
        
        self.cancel_btn = QPushButton("Close")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #555;
                color: #CCC;
                padding: 6px 16px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #333; color: #FFF; }
        """)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("Save")
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #0066CC; }
            QPushButton:disabled { background-color: #333333; color: #777777; }
        """)
        self.save_btn.clicked.connect(self.accept)
        
        self.footer_layout.addWidget(self.cancel_btn)
        self.footer_layout.addWidget(self.save_btn)
        
        # Assemble
        self.container_layout.addLayout(self.header_layout)
        self.container_layout.addWidget(sep1)
        self.container_layout.addWidget(self.content_widget)
        self.container_layout.addWidget(sep2)
        self.container_layout.addLayout(self.footer_layout)
        
    def add_content(self, widget: QWidget):
        self.content_layout.addWidget(widget)
        
    def add_layout(self, layout):
        self.content_layout.addLayout(layout)
