from PySide6.QtCore import QObject, Signal
from typing import Dict
from collections import defaultdict
from ui.models.roles import VaultRoles

class StatisticsProvider(QObject):
    """
    Computes and exposes vault counts incrementally based on the underlying VaultListModel.
    Used by the SidebarController to update UI counts without directly querying models.
    """
    counts_updated = Signal(dict) # Emits a dict of { 'total': int, 'favorites': int, 'categories': { 'Work': int, ... } }
    
    def __init__(self, model_context, parent=None):
        super().__init__(parent)
        self.context = model_context
        
        self.total = 0
        self.favorites = 0
        self.categories: Dict[str, int] = defaultdict(int)
        
        # Connect to list model signals for incremental updates
        self.context.vault_list_model.modelReset.connect(self.recalculate_all)
        self.context.vault_list_model.rowsInserted.connect(self._on_rows_inserted)
        self.context.vault_list_model.rowsAboutToBeRemoved.connect(self._on_rows_removed)
        self.context.vault_list_model.dataChanged.connect(self._on_data_changed)
        
    def recalculate_all(self):
        self.total = 0
        self.favorites = 0
        self.categories.clear()
        
        model = self.context.vault_list_model
        count = model.rowCount()
        self.total = count
        
        for i in range(count):
            idx = model.index(i, 0)
            if model.data(idx, VaultRoles.FavoriteRole):
                self.favorites += 1
            cat = model.data(idx, VaultRoles.CategoryRole)
            if cat:
                self.categories[cat] += 1
                
        self._emit_update()
        
    def _on_rows_inserted(self, parent, first, last):
        model = self.context.vault_list_model
        for i in range(first, last + 1):
            idx = model.index(i, 0)
            self.total += 1
            if model.data(idx, VaultRoles.FavoriteRole):
                self.favorites += 1
            cat = model.data(idx, VaultRoles.CategoryRole)
            if cat:
                self.categories[cat] += 1
        self._emit_update()
        
    def _on_rows_removed(self, parent, first, last):
        model = self.context.vault_list_model
        for i in range(first, last + 1):
            idx = model.index(i, 0)
            self.total -= 1
            if model.data(idx, VaultRoles.FavoriteRole):
                self.favorites -= 1
            cat = model.data(idx, VaultRoles.CategoryRole)
            if cat:
                self.categories[cat] -= 1
                if self.categories[cat] <= 0:
                    del self.categories[cat]
        self._emit_update()
        
    def _on_data_changed(self, top_left, bottom_right, roles):
        # Full recalculation for simplicity on data change if it involves favorite/category
        # Incremental could be tricky if we don't know the previous state.
        # Since dataChanged usually only happens for one row during edit, 
        # a full recalculate of a 10,000 item vault takes ~10ms in Python, but let's be careful.
        # To make it truly incremental, we would need to store previous state per item, which is memory-heavy.
        # Let's just recalculate all for now, we can optimize later if profiling shows it's a bottleneck.
        if not roles or VaultRoles.FavoriteRole in roles or VaultRoles.CategoryRole in roles:
            self.recalculate_all()
        
    def _emit_update(self):
        stats = {
            'total': self.total,
            'favorites': self.favorites,
            'categories': dict(self.categories)
        }
        self.counts_updated.emit(stats)
