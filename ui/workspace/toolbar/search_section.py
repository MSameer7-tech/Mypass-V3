from PySide6.QtWidgets import QHBoxLayout, QWidget
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtCore import Qt

from ui.widgets.inputs import SearchField
from ui.resources.styles.metrics import Metrics

class SearchSection(QWidget):
    def __init__(self, search_controller, parent=None):
        super().__init__(parent)
        self.search_controller = search_controller
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        self.search_field = SearchField("Search your vault...")
        self.search_field.setMinimumWidth(Metrics.SEARCH_FIELD_MIN_WIDTH)
        self.search_field.setMaximumWidth(Metrics.SEARCH_FIELD_MAX_WIDTH)
        # We don't set a hard preferred width but we can set a size policy to prefer expanding.
        self.search_field.setClearButtonEnabled(True)
        
        # Connect to SearchController
        if hasattr(self.search_field, 'textChanged'):
            self.search_field.textChanged.connect(self.search_controller.set_query)
        elif hasattr(self.search_field, 'text_changed'):
            self.search_field.text_changed.connect(self.search_controller.set_query)
            
        layout.addWidget(self.search_field)
        
        # Shortcuts
        self.focus_shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        # On macOS, Qt maps Ctrl to Cmd automatically for QKeySequence if using standard keys, 
        # but Ctrl+K explicitly might be literal Ctrl+K. Better to use standard keys or explicit Cmd+K.
        # "Ctrl+K" usually works as Cmd+K on macOS in Qt.
        self.focus_shortcut.activated.connect(self.search_field.setFocus)
        
        self.escape_shortcut = QShortcut(QKeySequence("Esc"), self)
        self.escape_shortcut.activated.connect(self._clear_search)
        
    def _clear_search(self):
        if self.search_field.hasFocus():
            self.search_field.clear()
            self.search_field.clearFocus()
