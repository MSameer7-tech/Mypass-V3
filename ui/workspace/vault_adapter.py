from typing import List, Optional
from PySide6.QtCore import QObject, Signal

from database.models import VaultEntryRecord
from utils.logging import app_logger

class VaultRepositoryAdapter(QObject):
    """
    Translates between VaultService and the UI Coordinator.
    Handles fetch all, add, update, delete, and emits repository change notifications.
    """
    # Signals emitted when the underlying repository changes
    entry_added = Signal(VaultEntryRecord)
    entry_updated = Signal(VaultEntryRecord)
    entry_deleted = Signal(int) # Emits the ID of the deleted entry
    repository_refreshed = Signal() # Full reset

    def __init__(self, vault_service, parent=None):
        super().__init__(parent)
        self.vault_service = vault_service
        
    def set_vault_service(self, vault_service):
        self.vault_service = vault_service
        self.refresh()
        
    def fetch_all(self) -> List[VaultEntryRecord]:
        try:
            return self.vault_service.list_all_entries()
        except Exception as e:
            app_logger.log_exception("fetch all entries", e, "VaultRepositoryAdapter")
            return []
            
    def add_entry(self, entry: VaultEntryRecord) -> Optional[VaultEntryRecord]:
        try:
            saved = self.vault_service.save_entry(
                title=entry.title,
                website=entry.website,
                username=entry.username,
                password=entry.password,
                notes=entry.notes,
                category=entry.category,
                tags=entry.tags,
                icon=entry.icon,
                favorite=entry.favorite,
                entry_id=None
            )
            if saved:
                self.entry_added.emit(saved)
                return saved
        except Exception as e:
            app_logger.log_exception("add entry", e, "VaultRepositoryAdapter")
        return None
        
    def update_entry(self, entry: VaultEntryRecord) -> bool:
        try:
            saved = self.vault_service.save_entry(
                title=entry.title,
                website=entry.website,
                username=entry.username,
                password=entry.password,
                notes=entry.notes,
                category=entry.category,
                tags=entry.tags,
                icon=entry.icon,
                favorite=entry.favorite,
                entry_id=entry.id
            )
            if saved:
                self.entry_updated.emit(saved)
                return True
        except Exception as e:
            app_logger.log_exception("update entry", e, "VaultRepositoryAdapter")
        return False
        
    def delete_entry(self, entry_id: int) -> bool:
        try:
            # Assuming vault_service has delete_entry (we fixed this in bug_fixer earlier)
            if hasattr(self.vault_service, 'delete_entry'):
                self.vault_service.delete_entry(entry_id)
                self.entry_deleted.emit(entry_id)
                return True
        except Exception as e:
            app_logger.log_exception("delete entry", e, "VaultRepositoryAdapter")
        return False
        
    def refresh(self):
        """Forces a full refresh of the repository state (e.g. after sync)."""
        self.repository_refreshed.emit()
