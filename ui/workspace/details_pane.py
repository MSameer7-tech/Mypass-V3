from PySide6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget, QLabel, QFormLayout, QScrollArea, QFrame, QHBoxLayout
from PySide6.QtCore import Qt

from ui.widgets.base import BaseFrame
from ui.widgets.indicators import EmptyState
from ui.widgets.buttons import PrimaryButton, PillButton
from ui.viewmodels.entry_details_viewmodel import EntryDetailsViewModel
from ui.workspace.entry_details_coordinator import EntryDetailsCoordinator
from ui.resources.styles.layout_constants import Layout
from ui.resources.styles.themes import ThemeManager
from ui.resources.icons import Icons
from ui.actions.action_manager import ActionManager
from ui.actions.vault import VaultActions

from ui.workspace.details_sections import (
    HeaderCard,
    CredentialsCard,
    MetadataCard,
    NotesCard,
    SecurityCard,
    HistoryCard,
    TotpCard,
)

class EntryDetailsView(QWidget):
    """
    Renders the details of an EntryDetailsViewModel as an inspector document
    composed of independent, self-contained cards.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(
            Layout.DETAILS_MARGIN,
            Layout.DETAILS_MARGIN,
            Layout.DETAILS_MARGIN,
            Layout.DETAILS_MARGIN
        )
        self.layout.setSpacing(Layout.DETAILS_SECTION_GAP)
        
        self.header = HeaderCard()
        self.credentials = CredentialsCard()
        self.security = SecurityCard()
        self.metadata = MetadataCard()
        self.notes = NotesCard()
        self.history = HistoryCard()
        self.totp = TotpCard()
        
        self.layout.addWidget(self.header)
        self.layout.addWidget(self.credentials)
        self.layout.addWidget(self.notes)
        self.layout.addWidget(self.metadata)
        
        # Edit Mode placeholder button (bottom action bar)
        self.edit_bar = QHBoxLayout()
        self.edit_bar.addStretch()
        self.edit_btn = PillButton("✏️ Edit")
        self.edit_bar.addWidget(self.edit_btn)
        self.edit_bar.addStretch()
        self.layout.addLayout(self.edit_bar)
        
        self.edit_btn.clicked.connect(self._on_edit_clicked)
        self.layout.addStretch()
        
        # Connect action signals to ActionManager
        self.credentials.copy_requested.connect(self._on_copy_requested)
        self.totp.copy_requested.connect(self._on_copy_requested)
        
    def _on_edit_clicked(self):
        if getattr(self, "current_vm", None):
            ActionManager.instance().dispatch(VaultActions.EDIT, self.current_vm)
            
    def _on_copy_requested(self, field: str, value: str):
        from ui.actions.action_manager import ActionManager
        from ui.actions.vault import VaultActions
        
        if field == "Username":
            ActionManager.instance().dispatch(VaultActions.COPY_USERNAME, value)
        elif field == "Password":
            ActionManager.instance().dispatch(VaultActions.COPY_PASSWORD, value)
        elif field == "TOTP Code":
            ActionManager.instance().dispatch(VaultActions.COPY_TOTP, value)
        
    def update_view(self, vm: EntryDetailsViewModel):
        self.current_vm = vm
        self.header.update_view(vm)
        self.credentials.update_view(vm)
        self.security.update_view(vm)
        self.metadata.update_view(vm)
        self.totp.update_view(vm)
        self.notes.update_view(vm)
        self.history.update_view(vm)

class DetailsPane(BaseFrame):
    """
    Main Details Pane container with QStackedWidget switching between
    EmptyState and scrollable EntryDetailsView.
    """
    def __init__(self, details_coordinator: EntryDetailsCoordinator, parent=None):
        super().__init__(parent)
        self.setObjectName("DetailsPane")
        self.details_coordinator = details_coordinator
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        self._init_pages()
        self._connect_signals()
        
    def _init_pages(self):
        # 1. Nothing Selected (Index 0)
        empty_page = QWidget()
        empty_layout = QVBoxLayout(empty_page)
        
        new_btn = PrimaryButton("+ New Password")
        new_btn.clicked.connect(lambda: ActionManager.instance().dispatch(VaultActions.NEW_PASSWORD))
        empty_state = EmptyState(
            icon_name=Icons.VAULT,
            title="No Password Selected",
            description="Select a password from the list\nto inspect its details.",
            action_button=new_btn
        )
        empty_layout.addWidget(empty_state)
        self.stack.addWidget(empty_page)
        
        # 2. Details View inside QScrollArea (Index 1)
        self.details_view = EntryDetailsView()
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)
        self.scroll_area.setWidget(self.details_view)
        
        self.stack.addWidget(self.scroll_area)
        
    def _connect_signals(self):
        self.details_coordinator.details_fetched.connect(self._on_details_fetched)
        self.details_coordinator.details_cleared.connect(self._on_details_cleared)
        self.details_coordinator.history_fetched.connect(self._on_history_fetched)
        
        # UI requests
        self.details_view.history.history_requested.connect(self.details_coordinator.fetch_history)
        
        # TOTP
        self.details_coordinator.totp_service.tick.connect(self.details_view.totp.update_tick)
        
    def _on_details_fetched(self, vm: EntryDetailsViewModel):
        self.details_view.update_view(vm)
        self.stack.setCurrentIndex(1)
        
    def _on_history_fetched(self, entry_id: int, history: list):
        if self.details_view.history.current_entry_id == entry_id:
            self.details_view.history.set_history_data(history)
            
    def _on_details_cleared(self):
        self.stack.setCurrentIndex(0)
        
    def show_page(self, index: int):
        if 0 <= index < self.stack.count():
            self.stack.setCurrentIndex(index)
