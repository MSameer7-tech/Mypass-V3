from PySide6.QtWidgets import QVBoxLayout

from ui.widgets.base import BaseWidget
from ui.workspace.toolbar.toolbar import Toolbar
from ui.workspace.workspace import Workspace
from ui.workspace.statusbar import StatusBar

class ApplicationShell(BaseWidget):
    """
    The top-level widget that contains the persistent application environment.
    Composes Toolbar, Workspace (Splitter), and StatusBar.
    """
    def __init__(self, model_context, details_coordinator, search_controller, sidebar_controller, statistics_provider, parent=None):
        super().__init__(parent)
        self.setObjectName("ApplicationShell")
        
        self.model_context = model_context
        self.details_coordinator = details_coordinator
        self.search_controller = search_controller
        self.sidebar_controller = sidebar_controller
        self.statistics_provider = statistics_provider
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.toolbar = Toolbar(self.search_controller)
        self.workspace = Workspace(self.model_context, self.details_coordinator, self.sidebar_controller, self.statistics_provider)
        self.statusbar = StatusBar()
        
        layout.addWidget(self.toolbar)
        layout.addWidget(self.workspace, 1) # Give Workspace all remaining space
        layout.addWidget(self.statusbar)
        
    def save_state(self):
        """Delegate state saving to child components that need it."""
        self.workspace.save_state()
        
    def restore_state(self):
        """Delegate state restoration to child components that need it."""
        self.workspace.restore_state()
