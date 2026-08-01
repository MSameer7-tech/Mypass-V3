from PySide6.QtWidgets import QHBoxLayout
from ui.widgets.base import BaseFrame
from ui.resources.styles.layout_constants import Layout
from ui.resources.styles.metrics import Metrics

from ui.workspace.toolbar.logo_section import LogoSection
from ui.workspace.toolbar.search_section import SearchSection
from ui.workspace.toolbar.actions_section import ActionsSection

class Toolbar(BaseFrame):
    def __init__(self, search_controller, parent=None):
        super().__init__(parent)
        self.search_controller = search_controller
        self.setObjectName("Toolbar")
        self.setFixedHeight(Metrics.TOOL_BAR_HEIGHT)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(Layout.TOOLBAR_MARGIN, 0, Layout.TOOLBAR_MARGIN, 0)
        # We don't need a main layout spacing since we use addStretch between the sections
        main_layout.setSpacing(0)
        
        self.logo_section = LogoSection()
        self.search_section = SearchSection(self.search_controller)
        self.actions_section = ActionsSection()
        
        # Logo | Search | Actions with layout spacing (stretches)
        main_layout.addWidget(self.logo_section)
        main_layout.addStretch(1)
        main_layout.addWidget(self.search_section)
        main_layout.addStretch(1)
        main_layout.addWidget(self.actions_section)
