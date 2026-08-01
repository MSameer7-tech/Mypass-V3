import dataclasses
from PySide6.QtCore import QSortFilterProxyModel, QModelIndex, Qt

from ui.models.roles import VaultRoles

class VaultFilterModel(QSortFilterProxyModel):
    """
    Separates semantic filtering (Favorites, Categories) from search text.
    Sorts based on raw values from ViewModels.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.context = parent # Should be ModelContext
        
        # Sort configuration
        self.setSortRole(VaultRoles.TitleRole)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)
        
    def _get_filter_state(self):
        return self.context.workspace_state.filter_state

    def set_search_query(self, query: str):
        fs = self._get_filter_state()
        new_fs = dataclasses.replace(fs, search_query=query)
        self.context.set_workspace_state(dataclasses.replace(self.context.workspace_state, filter_state=new_fs))
        
    def set_category_filter(self, category: str):
        fs = self._get_filter_state()
        new_fs = dataclasses.replace(fs, category_filter=category)
        self.context.set_workspace_state(dataclasses.replace(self.context.workspace_state, filter_state=new_fs))
        
    def set_favorites_only(self, show: bool):
        fs = self._get_filter_state()
        new_fs = dataclasses.replace(fs, show_favorites_only=show)
        self.context.set_workspace_state(dataclasses.replace(self.context.workspace_state, filter_state=new_fs))

    def get_row_for_id(self, entry_id: int) -> int:
        for i in range(self.rowCount()):
            idx = self.index(i, 0)
            vm = self.data(idx, VaultRoles.ViewModelRole)
            if vm and vm.id == entry_id:
                return i
        return -1

    def get_id_for_row(self, row: int) -> int:
        idx = self.index(row, 0)
        vm = self.data(idx, VaultRoles.ViewModelRole)
        if vm:
            return vm.id
        return -1

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        model = self.sourceModel()
        idx = model.index(source_row, 0, source_parent)
        
        fs = self._get_filter_state()
        
        # 1. Semantic Filtering
        if fs.show_favorites_only:
            is_favorite = model.data(idx, VaultRoles.FavoriteRole)
            if not is_favorite:
                return False
                
        if fs.category_filter:
            category = model.data(idx, VaultRoles.CategoryRole)
            if category != fs.category_filter:
                return False
                
        # 2. Text Search
        query = fs.search_query.lower()
        if not query:
            return True
            
        title = (model.data(idx, VaultRoles.TitleRole) or "").lower()
        username = (model.data(idx, VaultRoles.UsernameRole) or "").lower()
        url = (model.data(idx, VaultRoles.UrlRole) or "").lower()
        
        return (query in title or 
                query in username or 
                query in url)

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        """
        Sort using raw values instead of display strings.
        For example, if sorting by Created, use raw_created_at.
        """
        # If we sort by Title
        if self.sortRole() == VaultRoles.TitleRole:
            # We can use display_title directly, but lowercased
            left_val = (self.sourceModel().data(left, VaultRoles.TitleRole) or "").lower()
            right_val = (self.sourceModel().data(right, VaultRoles.TitleRole) or "").lower()
            return left_val < right_val
            
        # If we added a SortByCreated action later, we'd use CreatedRole
        if self.sortRole() == VaultRoles.CreatedRole:
            left_val = self.sourceModel().data(left, VaultRoles.CreatedRole) or ""
            right_val = self.sourceModel().data(right, VaultRoles.CreatedRole) or ""
            return left_val < right_val

        # Fallback to default behavior
        return super().lessThan(left, right)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        """
        Intercept requests for HighlightedRangesRole to compute match ranges on the fly based on the current search query.
        """
        if role == VaultRoles.HighlightedRangesRole:
            fs = self._get_filter_state()
            query = fs.search_query.lower()
            if not query:
                return {}
                
            title = (super().data(index, VaultRoles.TitleRole) or "").lower()
            username = (super().data(index, VaultRoles.UsernameRole) or "").lower()
            
            def get_ranges(text: str):
                ranges = []
                start = 0
                q_len = len(query)
                while True:
                    idx = text.find(query, start)
                    if idx == -1:
                        break
                    ranges.append((idx, q_len))
                    start = idx + q_len
                return ranges
                
            return {
                VaultRoles.TitleRole: get_ranges(title),
                VaultRoles.UsernameRole: get_ranges(username)
            }
            
        return super().data(index, role)
