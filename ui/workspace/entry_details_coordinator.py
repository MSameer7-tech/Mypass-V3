from PySide6.QtCore import QObject, Signal

from ui.models.model_context import ModelContext
from ui.workspace.vault_adapter import VaultRepositoryAdapter
from ui.viewmodels.entry_details_viewmodel import EntryDetailsViewModel
from ui.session.controller import SessionController
from ui.session.context import SessionState
from utils.logging import app_logger

class EntryDetailsCoordinator(QObject):
    """
    Orchestrates fetching sensitive details when selection changes.
    Maintains a small cache of EntryDetailsViewModel to avoid re-fetching 
    the backend during rapid UI navigation.
    """
    details_fetched = Signal(EntryDetailsViewModel)
    details_cleared = Signal()
    history_fetched = Signal(int, list) # (entry_id, history_records)
    
    def __init__(self, 
                 adapter: VaultRepositoryAdapter, 
                 context: ModelContext,
                 session_controller: SessionController,
                 totp_service,
                 parent=None):
        super().__init__(parent)
        self.adapter = adapter
        self.context = context
        self.session_controller = session_controller
        self.totp_service = totp_service
        
        self._cache = {} # entry_id -> EntryDetailsViewModel
        
        self._connect_signals()
        
    def _connect_signals(self):
        self.context.selection_manager.selection_changed.connect(self._on_selection_changed)
        self.session_controller.state_changed.connect(self._on_session_state_changed)
        self.adapter.entry_updated.connect(self._on_entry_updated)
        self.adapter.entry_deleted.connect(self._on_entry_deleted)
        
    def _on_selection_changed(self, viewmodel):
        if not viewmodel or not viewmodel.id:
            self.clear()
            return
            
        self.fetch_details(viewmodel.id)

    def _on_session_state_changed(self, state, context=None):
        if state in (SessionState.LOCKED, SessionState.NO_VAULT):
            self.clear()
            self._cache.clear()

    def _on_entry_updated(self, record):
        if record and record.id:
            self._cache.pop(record.id, None)
            if self.context.selection_manager.current_entry and self.context.selection_manager.current_entry.id == record.id:
                self.fetch_details(record.id)

    def _on_entry_deleted(self, entry_id: int):
        self._cache.pop(entry_id, None)
        if self.context.selection_manager.current_entry and self.context.selection_manager.current_entry.id == entry_id:
            self.clear()
            
    def fetch_details(self, entry_id: int):
        if entry_id in self._cache:
            self.details_fetched.emit(self._cache[entry_id])
            return
            
        try:
            record = self.adapter.vault_service.get_entry(entry_id)
            if record:
                details_vm = EntryDetailsViewModel.from_record(record)
                self._cache[entry_id] = details_vm
                self.details_fetched.emit(details_vm)
            else:
                self.clear()
        except Exception as e:
            app_logger.log_exception("fetch details", e, "EntryDetailsCoordinator")
            self.clear()
            
    def fetch_history(self, entry_id: int):
        try:
            history = self.adapter.vault_service.get_password_history(entry_id)
            self.history_fetched.emit(entry_id, history)
        except Exception as e:
            app_logger.log_exception("fetch history", e, "EntryDetailsCoordinator")
            self.history_fetched.emit(entry_id, [])
            
    def clear(self):
        self.details_cleared.emit()
