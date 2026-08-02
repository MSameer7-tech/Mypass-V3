from typing import List, Optional
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QColor

from ui.models.roles import VaultRoles
from ui.viewmodels.vault_entry_viewmodel import VaultEntryViewModel

class VaultListModel(QAbstractListModel):
    """
    Read-only Qt Model exposing a list of VaultEntryViewModels to views.
    Only VaultCoordinator should call the mutating methods.
    """
    def __init__(self, icon_service, parent=None):
        super().__init__(parent)
        self.icon_service = icon_service
        self._entries: List[VaultEntryViewModel] = []
        
        self.icon_service.icon_loaded.connect(self._on_icon_loaded)

    def _on_icon_loaded(self, entry_id: int, icon_path: str):
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id:
                idx = self.index(i, 0)
                self.dataChanged.emit(idx, idx, [VaultRoles.IconRole])
                break

    def rowCount(self, parent=QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._entries)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()):
            return None

        entry = self._entries[index.row()]

        if role == VaultRoles.IdRole:
            return entry.id
        elif role == VaultRoles.TitleRole:
            return entry.display_title
        elif role == VaultRoles.UsernameRole:
            return entry.display_username
        elif role == VaultRoles.UrlRole:
            return entry.display_url
        elif role == VaultRoles.IconRole:
            return self.icon_service.request_website_icon(entry.id, entry.display_url, fallback_title=entry.display_title)
        elif role == VaultRoles.CreatedRole:
            return entry.raw_created_at
        elif role == VaultRoles.ModifiedRole:
            return entry.raw_updated_at
        elif role == VaultRoles.FavoriteRole:
            return entry.raw_favorite
        elif role == VaultRoles.CategoryRole:
            return entry.raw_category
        elif role == VaultRoles.TagsRole:
            return entry.raw_tags
        elif role == VaultRoles.ViewModelRole:
            return entry
        elif role == Qt.AccessibleTextRole:
            fav = "Favorite" if entry.raw_favorite else ""
            return f"{entry.display_title}, Username: {entry.display_username}, {fav}".strip(", ")

        return None

    def roleNames(self):
        return {
            VaultRoles.IdRole: b"id",
            VaultRoles.TitleRole: b"title",
            VaultRoles.UsernameRole: b"username",
            VaultRoles.UrlRole: b"url",
            VaultRoles.IconRole: b"icon",
            VaultRoles.CreatedRole: b"created",
            VaultRoles.ModifiedRole: b"modified",
            VaultRoles.FavoriteRole: b"favorite",
            VaultRoles.CategoryRole: b"category",
            VaultRoles.TagsRole: b"tags",
            VaultRoles.ViewModelRole: b"viewmodel",
        }
        
    # --- Internal API for Coordinator ---

    def replace_entries(self, new_entries: List[VaultEntryViewModel]):
        """Replace all data cleanly."""
        self.beginResetModel()
        self._entries = new_entries
        self.endResetModel()

    def insert_entry(self, entry: VaultEntryViewModel):
        """Append an entry incrementally."""
        row = len(self._entries)
        self.beginInsertRows(QModelIndex(), row, row)
        self._entries.append(entry)
        self.endInsertRows()

    def update_entry(self, updated_entry: VaultEntryViewModel):
        """Replace a specific entry, emitting dataChanged."""
        for i, entry in enumerate(self._entries):
            if entry.id == updated_entry.id:
                self._entries[i] = updated_entry
                idx = self.index(i, 0)
                # Emitting dataChanged with no roles implies all roles might have changed
                self.dataChanged.emit(idx, idx, [])
                break

    def remove_entry(self, entry_id: int):
        """Remove an entry incrementally."""
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id:
                self.beginRemoveRows(QModelIndex(), i, i)
                self._entries.pop(i)
                self.endRemoveRows()
                break

    def get_entry_by_id(self, entry_id: int) -> Optional[VaultEntryViewModel]:
        """Lookup utility"""
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        return None
