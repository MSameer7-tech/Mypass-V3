from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QFrame, QPushButton, QLineEdit, QLabel

class BaseComponent:
    """Utilities for all reusable design system components."""
    pass

class BaseWidget(QWidget, BaseComponent):
    """Top-level visual base for custom components."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground) # helps QSS apply properly

class BaseFrame(QFrame, BaseComponent):
    """Base class for layout components like Cards, Dividers."""
    def __init__(self, parent=None):
        super().__init__(parent)

class BaseButton(QPushButton, BaseComponent):
    """Base class for all buttons."""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)

class BaseInput(QLineEdit, BaseComponent):
    """Base class for text inputs."""
    def __init__(self, parent=None):
        super().__init__(parent)

class BaseLabel(QLabel, BaseComponent):
    """Base class for all typography components."""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
