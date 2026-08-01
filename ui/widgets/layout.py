from PySide6.QtWidgets import QFrame
from ui.widgets.base import BaseFrame
from ui.resources.styles.widget_names import WidgetNames

class Card(BaseFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName(WidgetNames.CARD)

class Divider(BaseFrame):
    def __init__(self, orientation="horizontal", parent=None):
        super().__init__(parent)
        if orientation == "horizontal":
            self.setObjectName(WidgetNames.DIVIDER_H)
            self.setFrameShape(QFrame.HLine)
        else:
            self.setObjectName(WidgetNames.DIVIDER_V)
            self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Plain)
