from enum import Enum, auto
from dataclasses import dataclass
from PySide6.QtCore import QObject, Signal

from ui.models.vault_list_model import VaultListModel
from ui.models.vault_filter_model import VaultFilterModel
from ui.models.selection_manager import SelectionManager
from ui.models.workspace_state import WorkspaceState
from ui.services.asset_manager import AssetManager
from ui.services.icon_service import IconService

class LoadingState(Enum):
    EMPTY = auto()
    LOADING = auto()
    READY = auto()
    ERROR = auto()

class ModelContext(QObject):
    """
    A unified container for Qt Models and Selection State.
    Injected into the workspace so UI views don't need to juggle multiple model references.
    """
    state_changed = Signal(LoadingState)
    workspace_state_changed = Signal(WorkspaceState)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.asset_manager = AssetManager(self)
        self.icon_service = self.asset_manager  # backwards compatibility alias
        self.vault_list_model = VaultListModel(self.asset_manager, self)
        
        self.vault_filter_model = VaultFilterModel(self)
        self.vault_filter_model.setSourceModel(self.vault_list_model)
        
        self.selection_manager = SelectionManager(self.vault_filter_model, self)
        
        self._state = LoadingState.EMPTY
        self._workspace_state = WorkspaceState()
        
    @property
    def state(self) -> LoadingState:
        return self._state
        
    def set_state(self, new_state: LoadingState):
        if self._state != new_state:
            self._state = new_state
            self.state_changed.emit(self._state)
            
    @property
    def workspace_state(self) -> WorkspaceState:
        return self._workspace_state
        
    def set_workspace_state(self, new_state: WorkspaceState):
        self._workspace_state = new_state
        self.workspace_state_changed.emit(self._workspace_state)
        # Notify the filter model that the underlying filter configuration changed
        self.vault_filter_model.invalidateFilter()
        # Auto-select the first entry in the filtered view if items exist
        if self.vault_filter_model.rowCount() > 0:
            first_id = self.vault_filter_model.get_id_for_row(0)
            if first_id != -1:
                self.selection_manager.select_entry_by_id(first_id, force_emit=True)
        else:
            self.selection_manager.clear_selection()

    def clear(self):
        """Reset everything securely."""
        self.vault_list_model.replace_entries([])
        self.selection_manager.clear_selection()
        self.set_workspace_state(WorkspaceState()) # Reset filters
        self.set_state(LoadingState.EMPTY)
