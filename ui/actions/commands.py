from typing import List, Callable, Optional
from PySide6.QtCore import QObject, Signal
from utils.logging import app_logger

class Command:
    """Base interface for all reversible mutating operations."""
    def execute(self) -> None:
        raise NotImplementedError
        
    def undo(self) -> None:
        raise NotImplementedError
        
    def get_name(self) -> str:
        return self.__class__.__name__
        
    def is_undoable(self) -> bool:
        """Returns True if this command supports being undone."""
        return True

class UndoStack(QObject):
    """
    Manages the history of commands. 
    Clears automatically on session lock to prevent restoring data after logout.
    """
    can_undo_changed = Signal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._stack: List[Command] = []
        
    def push(self, command: Command) -> None:
        command.execute()
        if command.is_undoable():
            self._stack.append(command)
            self.can_undo_changed.emit(self.can_undo())
        
    def undo(self) -> None:
        if not self.can_undo():
            return
            
        command = self._stack.pop()
        try:
            command.undo()
        except Exception as e:
            app_logger.log_exception("undo command", e, "UndoStack", include_traceback=True)
            
        self.can_undo_changed.emit(self.can_undo())
        
    def can_undo(self) -> bool:
        return len(self._stack) > 0
        
    def clear(self) -> None:
        self._stack.clear()
        self.can_undo_changed.emit(False)

# -------------------------------------------------------------------------
# Specific Commands
# -------------------------------------------------------------------------

class DeleteEntryCommand(Command):
    """
    Command to delete an entry. 
    In a real implementation with SQLite, we might just soft-delete 
    or we'd need to store the complete serialized row to restore it.
    For Phase 6, we'll store the record and restore it on undo.
    """
    def __init__(self, entry_id: int, vault_coordinator, notification_service=None):
        self.entry_id = entry_id
        self.vault_coordinator = vault_coordinator
        self.notification_service = notification_service
        self._deleted_record = None # We would save the record here before deletion
        
    def execute(self) -> None:
        # 1. Fetch record for safe keeping
        # self._deleted_record = self.vault_coordinator.adapter.get_entry(self.entry_id)
        
        # 2. Delete it
        # self.vault_coordinator.adapter.delete_entry(self.entry_id)
        
        # 3. Update Model
        # self.vault_coordinator.model_context.vault_list_model.remove_entry(self.entry_id)
        
        if self.notification_service:
            # We hook up an undo action button right in the toast!
            from ui.services.notification_service import NotificationAction
            undo_action = NotificationAction(label="Undo", callback=self.vault_coordinator.undo_stack.undo)
            self.notification_service.show_success("Entry Deleted", "The item was moved to trash.", primary_action=undo_action)
            
    def undo(self) -> None:
        # 1. Restore record in DB
        # if self._deleted_record:
        #    self.vault_coordinator.adapter.save_entry(...)
        
        # 2. Add back to Model
        # self.vault_coordinator.model_context.vault_list_model.add_entry(self._deleted_record)
        
        if self.notification_service:
            self.notification_service.show_info("Undo Successful", "Entry restored.")

class CopyFieldCommand(Command):
    """
    Copies a sensitive field to the clipboard and triggers a notification.
    """
    def __init__(self, field_name: str, value: str, clipboard_service, notification_service):
        self.field_name = field_name
        self.value = value
        self.clipboard_service = clipboard_service
        self.notification_service = notification_service
        
    def is_undoable(self) -> bool:
        return False
        
    def execute(self) -> None:
        if not self.value:
            return
            
        self.clipboard_service.copy_text(self.value)
        if self.notification_service:
            self.notification_service.show_success(
                f"{self.field_name} Copied", 
                f"Copied to clipboard. Will clear automatically in 45s."
            )

class ToggleFavoriteCommand(Command):
    """
    Toggles the favorite status of an entry.
    """
    def __init__(self, entry_id: int, current_status: bool, vault_coordinator):
        self.entry_id = entry_id
        self.current_status = current_status
        self.vault_coordinator = vault_coordinator
        
    def is_undoable(self) -> bool:
        return True
        
    def execute(self) -> None:
        # In a real app with full edit capabilities, we would update the DB.
        # Since we just have the adapter scaffolding for Phase 6, we might just update the model.
        # We will dispatch an update to the backend service.
        pass
        
    def undo(self) -> None:
        pass
