from PySide6.QtWidgets import QHBoxLayout, QWidget
from PySide6.QtGui import QKeySequence, QShortcut, QIcon
from PySide6.QtCore import QSize

from ui.widgets.buttons import ToolbarIconButton, PrimaryButton
from ui.resources.styles.layout_constants import Layout
from ui.resources.icons import Icons
from ui.app.resources import Resources
from ui.resources.styles.metrics import Metrics

class ActionsSection(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        self.add_btn = PrimaryButton("+ Add Items")
        self.add_btn.setIcon(Resources.icon(Icons.NEW, color_hex="#000000"))
        self.add_btn.setIconSize(QSize(Metrics.ICON_16, Metrics.ICON_16))
        self.add_btn.setToolTip("Add Items (⌘N)")
        self.add_btn.setStyleSheet("""
            QPushButton#PrimaryButton {
                background-color: #38BDF8;
                color: #000000;
                font-weight: 600;
                border-radius: 8px;
                padding: 0px 16px;
                height: 36px;
            }
            QPushButton#PrimaryButton:hover {
                background-color: #7DD3FC;
            }
        """)
        
        self.lock_btn = ToolbarIconButton(Icons.LOCK)
        self.lock_btn.setToolTip("Lock Vault (⌘L)")
        self.settings_btn = ToolbarIconButton(Icons.SETTINGS)
        self.settings_btn.setToolTip("Settings (⌘,)")
        self.profile_btn = ToolbarIconButton(Icons.USER)
        self.profile_btn.setToolTip("Vault Information")
        
        from ui.actions.action_manager import ActionManager
        from ui.actions.session import SessionActions
        from ui.actions.settings import SettingsActions
        from ui.actions.vault import VaultActions
        
        self.lock_btn.clicked.connect(lambda: ActionManager.instance().dispatch(SessionActions.LOCK))
        self.settings_btn.clicked.connect(lambda: ActionManager.instance().dispatch(SettingsActions.OPEN))
        self.profile_btn.clicked.connect(lambda: ActionManager.instance().dispatch(SettingsActions.OPEN_PROFILE))
        self.add_btn.clicked.connect(lambda: ActionManager.instance().dispatch(VaultActions.NEW_PASSWORD))
        
        layout.addWidget(self.add_btn)
        layout.addWidget(self.lock_btn)
        layout.addWidget(self.settings_btn)
        layout.addWidget(self.profile_btn)
        
        # Shortcuts for New Item, Lock, Settings
        self.new_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        self.new_shortcut.activated.connect(self.add_btn.click)
        self.lock_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        self.lock_shortcut.activated.connect(self.lock_btn.click)
        self.settings_shortcut = QShortcut(QKeySequence("Ctrl+,"), self)
        self.settings_shortcut.activated.connect(self.settings_btn.click)
