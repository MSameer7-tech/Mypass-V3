from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSplitter
from PySide6.QtCore import Qt, QSettings

from ui.widgets.base import BaseWidget
from ui.workspace.toolbar.toolbar import Toolbar
from ui.workspace.sidebar import Sidebar
from ui.workspace.content_region import ContentRegion
from ui.workspace.details_pane import DetailsPane
from ui.workspace.controller import WorkspaceController
from ui.resources.styles.layout_constants import Layout
from ui.resources.styles.metrics import Metrics

class Workspace(BaseWidget):
    """
    Central layout coordinator for Phase A.10.
    Full-height Sidebar on the left (240px).
    Right side contains Toolbar at top and QSplitter (VaultList + Details Inspector) below.
    """
    def __init__(self, model_context, details_coordinator, search_controller, sidebar_controller, statistics_provider, parent=None):
        super().__init__(parent)
        self.setObjectName("Workspace")
        
        self.model_context = model_context
        self.details_coordinator = details_coordinator
        self.search_controller = search_controller
        self.sidebar_controller = sidebar_controller
        self.statistics_provider = statistics_provider
        
        # 1. Full height Sidebar (Task 1)
        self.sidebar = Sidebar(self.sidebar_controller, self.statistics_provider)
        self.sidebar.setFixedWidth(240)
        
        # 2. Right Side Vertical Container (Toolbar + Splitter)
        right_container = QWidget()
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        self.toolbar = Toolbar(self.search_controller)
        
        # 3. Horizontal Splitter for Vault List & Details Inspector (Task 4)
        self.splitter = QSplitter(Qt.Horizontal)
        self.content_region = ContentRegion(self.model_context)
        self.details_pane = DetailsPane(self.details_coordinator)
        
        self.splitter.addWidget(self.content_region)
        self.splitter.addWidget(self.details_pane)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        
        self.content_region.setFixedWidth(320)
        self.details_pane.setMinimumWidth(480)
        
        right_layout.addWidget(self.toolbar)
        right_layout.addWidget(self.splitter, 1)
        
        # 4. Main Layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(right_container, 1)
        
        self.controller = WorkspaceController(self)
        
        # Connect signals
        self.sidebar.nav_item_selected.connect(self.controller.handle_sidebar_selection)
        self.controller.content_page_changed.connect(self.content_region.show_page)
        self.controller.details_page_changed.connect(self.details_pane.show_page)
        
    def save_state(self):
        settings = QSettings("MyPass", "MyPassApp")
        settings.setValue("workspace/splitter_state", self.splitter.saveState())
        
    def restore_state(self):
        # Task 4 Splitter proportions: Vault List 320px (27%), Inspector 960px (55%+)
        self.splitter.setSizes([320, 960])
