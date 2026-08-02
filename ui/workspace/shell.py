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
        
        self.workspace = Workspace(self.model_context, self.details_coordinator, self.search_controller, self.sidebar_controller, self.statistics_provider)
        self.statusbar = StatusBar()
        self.statusbar.hide()
        
        layout.addWidget(self.workspace, 1)
        
    @property
    def toolbar(self):
        return self.workspace.toolbar
        
    def save_state(self):
        """Delegate state saving to child components that need it."""
        self.workspace.save_state()
        
    def restore_state(self):
        """Delegate state restoration to child components that need it."""
        self.workspace.restore_state()
