from enum import IntEnum
from PySide6.QtCore import Qt

class VaultRoles(IntEnum):
    """
    Strongly typed roles for the VaultListModel.
    Qt.UserRole starts at 0x0100 (256). We allocate custom roles from here.
    """
    IdRole = Qt.UserRole + 1
    TitleRole = Qt.UserRole + 2
    UsernameRole = Qt.UserRole + 3
    UrlRole = Qt.UserRole + 4
    IconRole = Qt.UserRole + 5
    CreatedRole = Qt.UserRole + 6
    ModifiedRole = Qt.UserRole + 7
    FavoriteRole = Qt.UserRole + 8
    CategoryRole = Qt.UserRole + 9
    TagsRole = Qt.UserRole + 10
    
    # Future-proof roles
    HasTotpRole = Qt.UserRole + 11
    WeakPasswordRole = Qt.UserRole + 12
    BreachedRole = Qt.UserRole + 13
    
    # Presentation
    HighlightedRangesRole = Qt.UserRole + 303
    
    # We might want the entire view model available via a role for advanced python-side operations
    ViewModelRole = Qt.UserRole + 100
