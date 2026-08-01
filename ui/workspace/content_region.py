from PySide6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget
from ui.widgets.base import BaseFrame
from ui.widgets.indicators import EmptyState
from ui.widgets.buttons import PrimaryButton, SecondaryButton
from ui.models.model_context import ModelContext, LoadingState
from ui.views.vault.vault_list_view import VaultListView
from ui.actions.action_manager import ActionManager
from ui.actions.vault import VaultActions
from ui.resources.icons import Icons

class ContentRegion(BaseFrame):
    def __init__(self, model_context: ModelContext, parent=None):
        super().__init__(parent)
        self.setObjectName("ContentRegion")
        self.model_context = model_context
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)
        
        self._init_pages()
        self._connect_signals()
        
    def _init_pages(self):
        # 0. Loading State
        loading_page = QWidget()
        loading_layout = QVBoxLayout(loading_page)
        self.loading_state = EmptyState(
            icon_name="loader",
            title="Loading Vault...",
            description="Decrypting your secure data."
        )
        loading_layout.addWidget(self.loading_state)
        self.stack.addWidget(loading_page)
        
        # 1. Vault Empty
        empty_vault_page = QWidget()
        empty_vault_layout = QVBoxLayout(empty_vault_page)
        add_btn = PrimaryButton("Create Password")
        add_btn.clicked.connect(lambda: ActionManager.instance().dispatch(VaultActions.NEW_PASSWORD))
        
        self.empty_vault_state = EmptyState(
            icon_name=Icons.SHIELD,
            title="Your Vault is Empty",
            description="Get started by adding your first password or secure note.",
            action_button=add_btn,
            secondary_action=SecondaryButton("Import Passwords")
        )
        empty_vault_layout.addWidget(self.empty_vault_state)
        self.stack.addWidget(empty_vault_page)
        
        # 2. Search Empty
        empty_search_page = QWidget()
        empty_search_layout = QVBoxLayout(empty_search_page)
        self.empty_search_state = EmptyState(
            icon_name=Icons.SEARCH,
            title="No Results Found",
            description="Try adjusting your search or filters."
        )
        empty_search_layout.addWidget(self.empty_search_state)
        self.stack.addWidget(empty_search_page)
        
        # 3. Vault List
        self.vault_list_view = VaultListView(self.model_context)
        self.stack.addWidget(self.vault_list_view)
        
    def _connect_signals(self):
        self.model_context.state_changed.connect(self._on_model_state_changed)
        self.model_context.vault_filter_model.layoutChanged.connect(self._on_filter_changed)
        self.model_context.vault_filter_model.rowsInserted.connect(self._on_filter_changed)
        self.model_context.vault_filter_model.rowsRemoved.connect(self._on_filter_changed)
        self.model_context.vault_filter_model.modelReset.connect(self._on_filter_changed)
        
    def _on_model_state_changed(self, state: LoadingState):
        if state == LoadingState.LOADING:
            self.stack.setCurrentIndex(0)
        elif state == LoadingState.EMPTY:
            self.stack.setCurrentIndex(1)
        elif state == LoadingState.READY:
            self._on_filter_changed()
            
    def _on_filter_changed(self, *args, **kwargs):
        if self.model_context.state != LoadingState.READY:
            return
            
        if self.model_context.vault_filter_model.rowCount() == 0:
            self.stack.setCurrentIndex(2) # Search Empty
        else:
            self.stack.setCurrentIndex(3) # Vault List
            
    def show_page(self, index: int):
        # Override for external manual control (e.g. settings page) if we had one
        pass
