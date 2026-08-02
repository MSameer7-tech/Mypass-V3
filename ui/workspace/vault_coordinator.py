from PySide6.QtCore import QObject

from ui.models.model_context import ModelContext, LoadingState
from ui.viewmodels.vault_entry_viewmodel import VaultEntryViewModel
from ui.workspace.vault_adapter import VaultRepositoryAdapter
from ui.session.controller import SessionController
from ui.session.context import SessionState
from database.models import VaultEntryRecord
from ui.actions.action_manager import ActionManager
from ui.actions.vault import VaultActions

from ui.actions.commands import UndoStack, DeleteEntryCommand
from ui.services.notification_service import NotificationService

class VaultCoordinator(QObject):
    """
    Orchestrates business logic for the Vault.
    Listens to global ActionManager triggers and coordinates backend mutations,
    then updates the ModelContext.
    """
    def __init__(self, adapter: VaultRepositoryAdapter, 
                 context: ModelContext, 
                 session_controller: SessionController,
                 icon_service,
                 notification_service: NotificationService,
                 clipboard_service,
                 parent=None):
        super().__init__(parent)
        self.adapter = adapter
        self.context = context
        self.session_controller = session_controller
        self.icon_service = icon_service
        self.notification_service = notification_service
        self.clipboard_service = clipboard_service
        
        self.undo_stack = UndoStack(self)
        
        self._connect_signals()

    def _connect_signals(self):
        # Listen to backend adapter changes
        self.adapter.entry_added.connect(self._on_entry_added)
        self.adapter.entry_updated.connect(self._on_entry_updated)
        self.adapter.entry_deleted.connect(self._on_entry_deleted)
        self.adapter.repository_refreshed.connect(self.refresh)
        
        # Listen to session changes to secure memory
        self.session_controller.state_changed.connect(self._on_session_state_changed)
        
        # Listen to global actions
        ActionManager.instance().action_triggered.connect(self._on_action_triggered)
        
        # Listen to icon service
        self.icon_service.icon_loaded.connect(self._on_icon_loaded)
        
    def _on_session_state_changed(self, state: SessionState, context):
        if state == SessionState.UNLOCKED:
            self.load()
        elif state in (SessionState.LOCKED, SessionState.NO_VAULT):
            self.clear()

    # --- Lifecycle Methods ---

    def initialize(self):
        """Prepare the coordinator. If already unlocked (e.g. fast refresh), load."""
        if self.session_controller.context.state == SessionState.UNLOCKED:
            self.load()

    def load(self):
        """Initial load of all entries."""
        print("[VaultCoordinator] Loading vault data...")
        self.context.set_state(LoadingState.LOADING)
        
        records = self.adapter.fetch_all()
        viewmodels = []
        for r in records:
            vm = VaultEntryViewModel.from_record(r)
            # Ask icon service for icon, might trigger async fetch
            cached_icon = self.icon_service.get_icon(vm.id, vm.raw_website)
            # We can use setattr since we're setting up the list, but it's frozen.
            # Instead we should recreate or just use the cache in data() role.
            # A better approach is to let the Model query the icon cache or we update it.
            # For now, we will replace the whole object if icon loads later.
            viewmodels.append(vm)
            
        self.context.vault_list_model.replace_entries(viewmodels)
        
        if len(viewmodels) == 0:
            self.context.set_state(LoadingState.EMPTY)
        else:
            self.context.set_state(LoadingState.READY)
            # Auto-select the first item on startup so Inspector opens populated immediately
            first_id = self.context.vault_filter_model.get_id_for_row(0)
            if first_id != -1:
                self.context.selection_manager.select_entry_by_id(first_id, force_emit=True)
        print(f"[VaultCoordinator] Loaded {len(viewmodels)} entries.")

    def refresh(self):
        """Reload everything from scratch."""
        self.load()

    def clear(self):
        """Wipe decrypted presentation data cleanly on session lock."""
        print("[VaultCoordinator] Clearing vault data from models...")
        self.context.vault_list_model.replace_entries([])
        self.context.selection_manager.clear_selection()
        self.context.set_state(LoadingState.EMPTY)

    def shutdown(self):
        self.clear()

    # --- Actions ---
    def _on_action_triggered(self, action, payload):
        from ui.actions.commands import CopyFieldCommand
        
        if action == VaultActions.NEW_PASSWORD:
            self.show_new_entry_dialog()
        elif action == VaultActions.EDIT:
            self.show_edit_entry_dialog(payload)
        elif action == VaultActions.DELETE:
            entry = self.context.selection_manager.current_entry
            if entry and entry.id:
                command = DeleteEntryCommand(entry.id, self, self.notification_service)
                self.undo_stack.push(command)
        elif action == VaultActions.COPY_USERNAME:
            command = CopyFieldCommand("Username", payload, self.clipboard_service, self.notification_service)
            self.undo_stack.push(command)
        elif action == VaultActions.COPY_PASSWORD:
            command = CopyFieldCommand("Password", payload, self.clipboard_service, self.notification_service)
            self.undo_stack.push(command)
        elif action == VaultActions.COPY_TOTP:
            command = CopyFieldCommand("TOTP Code", payload, self.clipboard_service, self.notification_service)
            self.undo_stack.push(command)

    # --- Incremental Updates ---
    
    def _on_entry_added(self, record: VaultEntryRecord):
        vm = VaultEntryViewModel.from_record(record)
        self.icon_service.get_icon(record.id, record.website, record.title)
        self.context.vault_list_model.insert_entry(vm)
        self.context.set_state(LoadingState.READY)
        self.context.selection_manager.select_entry_by_id(record.id, force_emit=True)
        
    def _on_entry_updated(self, record: VaultEntryRecord):
        vm = VaultEntryViewModel.from_record(record)
        self.icon_service.get_icon(record.id, record.website, record.title)
        self.context.vault_list_model.update_entry(vm)
        if self.context.selection_manager.current_entry and self.context.selection_manager.current_entry.id == record.id:
            self.context.selection_manager.select_entry_by_id(record.id, force_emit=True)
            
    def show_new_entry_dialog(self):
        from ui.dialogs.entry_dialog import EntryDialog
        from database.models import VaultEntryRecord
        from PySide6.QtWidgets import QApplication
        
        dialog = EntryDialog(parent=QApplication.activeWindow())
        if dialog.exec():
            vals = dialog.get_values()
            if not vals["title"]:
                vals["title"] = "Untitled"
            record = VaultEntryRecord(
                id=None,
                title=vals["title"],
                website=vals["website"],
                username=vals["username"],
                password=vals["password"],
                notes=vals["notes"],
                category=vals["category"],
                tags="",
                icon="",
                favorite=vals["favorite"],
                created_at="",
                updated_at=""
            )
            saved = self.adapter.add_entry(record)
            if saved and self.notification_service:
                self.notification_service.show_success("Item Added", f"'{vals['title']}' has been added to your vault.")

    def show_edit_entry_dialog(self, vm=None):
        from ui.dialogs.entry_dialog import EntryDialog
        from database.models import VaultEntryRecord
        from PySide6.QtWidgets import QApplication
        
        if vm is None:
            vm = self.context.selection_manager.current_entry
        if not vm or not getattr(vm, "id", None):
            return
            
        try:
            full_record = self.adapter.vault_service.get_entry(vm.id)
            if not full_record:
                return
        except Exception:
            return
            
        dialog = EntryDialog(entry_vm=full_record, parent=QApplication.activeWindow())
        if dialog.exec():
            vals = dialog.get_values()
            if not vals["title"]:
                vals["title"] = "Untitled"
            record = VaultEntryRecord(
                id=full_record.id,
                title=vals["title"],
                website=vals["website"],
                username=vals["username"],
                password=vals["password"],
                notes=vals["notes"],
                category=vals["category"],
                tags=full_record.tags,
                icon=full_record.icon,
                favorite=vals["favorite"],
                created_at=full_record.created_at,
                updated_at=""
            )
            success = self.adapter.update_entry(record)
            if success and self.notification_service:
                self.notification_service.show_success("Item Updated", f"'{vals['title']}' has been updated.")
        
    def _on_entry_deleted(self, entry_id: int):
        # Selection persistence logic
        row = self.context.selection_manager.current_row
        
        self.context.vault_list_model.remove_entry(entry_id)
        
        if self.context.vault_list_model.rowCount() == 0:
            self.context.selection_manager.clear_selection()
            self.context.set_state(LoadingState.EMPTY)
        else:
            # Select next row, or previous if at end
            new_row = min(row, self.context.vault_list_model.rowCount() - 1)
            next_id = self.context.vault_filter_model.get_id_for_row(new_row)
            if next_id != -1:
                self.context.selection_manager.select_entry_by_id(next_id, force_emit=True)
            
    def _on_icon_loaded(self, entry_id: int, icon_path: str):
        vm = self.context.vault_list_model.get_entry_by_id(entry_id)
        if vm:
            # Create a new immutable VM with the new icon path
            new_vm = VaultEntryViewModel(
                id=vm.id,
                raw_title=vm.raw_title,
                raw_username=vm.raw_username,
                raw_website=vm.raw_website,
                raw_created_at=vm.raw_created_at,
                raw_updated_at=vm.raw_updated_at,
                raw_favorite=vm.raw_favorite,
                raw_category=vm.raw_category,
                raw_tags=vm.raw_tags,
                display_title=vm.display_title,
                display_username=vm.display_username,
                display_url=vm.display_url,
                icon_path=icon_path, # Updated
                formatted_created_at=vm.formatted_created_at,
                formatted_updated_at=vm.formatted_updated_at
            )
            self.context.vault_list_model.update_entry(new_vm)
