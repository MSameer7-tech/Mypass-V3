from PySide6.QtCore import QObject
import dataclasses
from typing import Optional

from ui.models.workspace_state import WorkspaceState

class SidebarController(QObject):
    """
    Owns filter transitions triggered by the Sidebar view.
    Executes transactional updates to the ModelContext's WorkspaceState.
    The Sidebar acts as a dumb view interacting with this controller.
    """
    def __init__(self, model_context, statistics_provider, parent=None):
        super().__init__(parent)
        self.context = model_context
        self.statistics_provider = statistics_provider
        
    def select_all_items(self):
        self._update_filter_state(
            show_favorites_only=False,
            category_filter=None,
            tag_filters=[]
        )
        
    def select_favorites(self):
        self._update_filter_state(
            show_favorites_only=True,
            category_filter=None,
            tag_filters=[]
        )
        
    def select_category(self, category: str):
        self._update_filter_state(
            show_favorites_only=False,
            category_filter=category,
            tag_filters=[]
        )
        
    def select_tag(self, tag: str):
        self._update_filter_state(
            show_favorites_only=False,
            category_filter=None,
            tag_filters=[tag]
        )
        
    def clear_filters(self):
        self.select_all_items()
        
    def _update_filter_state(self, show_favorites_only: bool, category_filter: Optional[str], tag_filters: list):
        # We perform a transactional update on the workspace state.
        # Note: the search query is NOT cleared when navigating the sidebar.
        # This matches the user's acceptance criteria: "Search survives category changes."
        
        old_ws = self.context.workspace_state
        old_fs = old_ws.filter_state
        
        # We also need to apply selection persistence rules. 
        # But `ModelContext` handles the active selection currently.
        # A more robust approach is for VaultCoordinator or ModelContext itself to handle selection persistence
        # during filter invalidation. `SelectionManager` has logic for this if wired correctly, or we do it here.
        
        current_entry = self.context.selection_manager.current_entry
        
        new_fs = dataclasses.replace(
            old_fs,
            show_favorites_only=show_favorites_only,
            category_filter=category_filter,
            tag_filters=tag_filters
        )
        new_ws = dataclasses.replace(old_ws, filter_state=new_fs)
        self.context.set_workspace_state(new_ws)
        
        # Re-apply selection rules
        if current_entry:
            # Check if it's still in the filtered model
            idx = self.context.vault_filter_model.get_row_for_id(current_entry.id)
            if idx >= 0:
                # Still visible, preserve it
                self.context.selection_manager.select_entry_by_id(current_entry.id)
            else:
                # Try to select the first visible item, or clear
                if self.context.vault_filter_model.rowCount() > 0:
                    first_id = self.context.vault_filter_model.get_id_for_row(0)
                    if first_id:
                        self.context.selection_manager.select_entry_by_id(first_id)
                else:
                    self.context.selection_manager.clear_selection()
