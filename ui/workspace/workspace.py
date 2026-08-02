from PySide6.QtWidgets import QSplitter
from PySide6.QtCore import Qt, QSettings

from ui.widgets.base import BaseWidget
from ui.workspace.toolbar.toolbar import Toolbar
from ui.workspace.sidebar import Sidebar
from ui.workspace.content_region import ContentRegion
from ui.workspace.details_pane import DetailsPane
from ui.workspace.controller import WorkspaceController
from ui.resources.styles.layout_constants import Layout
from ui.resources.styles.metrics import Metrics

class Workspace(QSplitter):
    """
    Central 3-pane layout coordinator.
    Owns the Sidebar, VaultList (Content), and Details pane.
    """
    def __init__(self, model_context, details_coordinator, sidebar_controller, statistics_provider, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setObjectName("Workspace")
        
        self.model_context = model_context
        self.details_coordinator = details_coordinator
        self.sidebar_controller = sidebar_controller
        self.statistics_provider = statistics_provider
        
        # Build Panes
        self.sidebar = Sidebar(self.sidebar_controller, self.statistics_provider)
        self.content_region = ContentRegion(self.model_context)
        self.details_pane = DetailsPane(self.details_coordinator)
        
        # Add to splitter
        self.addWidget(self.sidebar)
        self.addWidget(self.content_region)
        self.addWidget(self.details_pane)
        
        # Stretch factors: Sidebar fixed (0), Vault List fixed (0), Inspector expanding (1)
        self.setStretchFactor(0, 0)
        self.setStretchFactor(1, 0)
        self.setStretchFactor(2, 1)
        
        # Set constraints
        self.sidebar.setFixedWidth(240)
        self.content_region.setFixedWidth(320)
        self.details_pane.setMinimumWidth(480)
        
        self.controller = WorkspaceController(self)
        
        # Connect signals
        self.sidebar.nav_item_selected.connect(self.controller.handle_sidebar_selection)
        self.controller.content_page_changed.connect(self.content_region.show_page)
        self.controller.details_page_changed.connect(self.details_pane.show_page)
        
    def save_state(self):
        settings = QSettings("MyPass", "MyPassApp")
        settings.setValue("workspace/splitter_state", self.saveState())
        
    def restore_state(self):
        self.setSizes([240, 320, 680])
