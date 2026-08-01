from PySide6.QtWidgets import QListView, QAbstractItemView
from PySide6.QtCore import Qt

from ui.models.model_context import ModelContext
from ui.views.vault.vault_item_delegate import VaultItemDelegate

class VaultListView(QListView):
    """
    Highly performant list view specifically configured for Vault rendering.
    Integrates with VaultFilterModel and SelectionManager via ModelContext.
    """
    def __init__(self, model_context: ModelContext, parent=None):
        super().__init__(parent)
        self.setObjectName("VaultListView")
        
        self.model_context = model_context
        
        # 1. Setup Models
        self.setModel(self.model_context.vault_filter_model)
        self.setSelectionModel(self.model_context.selection_manager.selection_model)
        
        # 2. Setup Delegate
        self.item_delegate = VaultItemDelegate(self)
        self.setItemDelegate(self.item_delegate)
        
        # 3. View Configurations
        self.setUniformItemSizes(True) # Critical for performance with 1000s of entries
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setFrameShape(QListView.NoFrame)
        self.setAttribute(Qt.WA_MacShowFocusRect, False)
        self.setMouseTracking(True)
        self.setSpacing(0) # Spacing is handled by delegate CARD_MARGIN_Y inset
        
        # Styling
        self.setStyleSheet("background: transparent;")
        
        # 4. Accessibility
        self.setAccessibleName("Vault Item List")
        self.setAccessibleDescription("List of your stored passwords and secure notes")
