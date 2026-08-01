from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
from ui.dialogs.base_dialog import BaseDialog

class VaultInfoDialog(BaseDialog):
    def __init__(self, model_context, parent=None):
        super().__init__("Vault Information", parent)
        self.setMinimumWidth(400)
        self.model_context = model_context
        
        # Hide the save button since this is mostly informational
        self.save_btn.hide()
        
        w = QWidget()
        layout = QFormLayout(w)
        layout.setLabelAlignment(Qt.AlignRight)
        
        # Safe access to vault data
        vault = self.model_context.vault if self.model_context else None
        
        name = vault.name if vault else "Unknown"
        created = "Unknown" # Not tracked in current schema easily, but could fetch from metadata
        entries_count = len(vault.entries) if vault else 0
        fav_count = len([e for e in (vault.entries if vault else []) if e.is_favorite])
        encryption = "Argon2 + AES-256-GCM"
        last_unlock = "Just now" # Or track it in session context
        
        layout.addRow("Vault Name:", QLabel(f"<b>{name}</b>"))
        layout.addRow("Created:", QLabel(created))
        layout.addRow("Entries:", QLabel(str(entries_count)))
        layout.addRow("Favorites:", QLabel(str(fav_count)))
        layout.addRow("Encryption:", QLabel(encryption))
        layout.addRow("Last Unlock:", QLabel(last_unlock))
        
        self.change_pwd_btn = QPushButton("Change Master Password")
        self.change_pwd_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #555;
                color: #CCC;
                padding: 6px 16px;
                border-radius: 6px;
                margin-top: 16px;
            }
            QPushButton:hover { background-color: #333; color: #FFF; }
        """)
        
        self.change_pwd_btn.clicked.connect(self._on_change_password)
        layout.addRow("", self.change_pwd_btn)
        
        self.add_content(w)
        
    def _on_change_password(self):
        # We can implement this fully later, or show a toast message for now
        # The ActionManager can be used or a sub-dialog.
        print("Change password clicked")
        # Could show a "Not implemented yet" or actual change password dialog.
