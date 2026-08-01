from typing import Optional
from PySide6.QtCore import QObject, Signal, QItemSelectionModel, QModelIndex

from ui.models.roles import VaultRoles
from ui.viewmodels.vault_entry_viewmodel import VaultEntryViewModel

class SelectionManager(QObject):
    """
    Semantic wrapper around QItemSelectionModel.
    Provides downstream code (e.g., Details Pane) with direct access
    to the selected ViewModel without wrestling with indexes.
    """
    selection_changed = Signal(object) # Emits VaultEntryViewModel or None
    
    def __init__(self, filter_model, parent=None):
        super().__init__(parent)
        self.filter_model = filter_model
        # We assume single selection for now
        self.selection_model = QItemSelectionModel(self.filter_model, self)
        
        self.selection_model.currentChanged.connect(self._on_current_changed)
        
        self._current_viewmodel: Optional[VaultEntryViewModel] = None
        self._current_row: int = -1
        
    def _on_current_changed(self, current: QModelIndex, previous: QModelIndex):
        if not current.isValid():
            self._current_viewmodel = None
            self._current_row = -1
        else:
            self._current_row = current.row()
            # Fetch the viewmodel directly via our custom role
            self._current_viewmodel = current.data(VaultRoles.ViewModelRole)
            
        self.selection_changed.emit(self._current_viewmodel)
        
    @property
    def current_entry(self) -> Optional[VaultEntryViewModel]:
        return self._current_viewmodel
        
    @property
    def current_row(self) -> int:
        return self._current_row
        
    @property
    def has_selection(self) -> bool:
        return self._current_viewmodel is not None
        
    def clear_selection(self):
        self.selection_model.clearSelection()
        # Also clear current index
        self.selection_model.setCurrentIndex(QModelIndex(), QItemSelectionModel.Clear)

    def select_entry_by_id(self, entry_id: int, force_emit: bool = False):
        # We need to find the row for this entry in the filter model
        if hasattr(self.filter_model, "get_row_for_id"):
            row = self.filter_model.get_row_for_id(entry_id)
            if row >= 0:
                idx = self.filter_model.index(row, 0)
                already_current = (self.selection_model.currentIndex() == idx)
                self.selection_model.setCurrentIndex(idx, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
                self._current_row = row
                self._current_viewmodel = idx.data(VaultRoles.ViewModelRole)
                if force_emit and already_current:
                    self.selection_changed.emit(self._current_viewmodel)
