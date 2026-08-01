from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QShortcut, QKeySequence
from typing import Dict, Any, Callable
from enum import Enum

from ui.actions.session import SessionActions
from ui.actions.vault import VaultActions
from ui.actions.settings import SettingsActions
from ui.actions.navigation import NavigationActions

class ActionManager(QObject):
    """
    Central registry for all semantic actions in the application.
    Decouples UI events (button clicks, shortcuts) from business logic.
    """
    
    # Generic signal that any action occurred. Handlers check the action type.
    action_triggered = Signal(Enum, object) # (Action Enum, Optional Payload)
    
    _instance = None
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = ActionManager()
        return cls._instance
        
    def __init__(self, parent=None):
        super().__init__(parent)
        self.shortcuts = []
        
    def dispatch(self, action: Enum, payload: Any = None):
        """Dispatch a semantic action."""
        print(f"Action dispatched: {action} with payload: {payload}")
        self.action_triggered.emit(action, payload)
        
    def register_shortcut(self, parent: QObject, key_sequence: str, action: Enum):
        """Bind a keyboard shortcut directly to an action."""
        shortcut = QShortcut(QKeySequence(key_sequence), parent)
        shortcut.activated.connect(lambda: self.dispatch(action))
        self.shortcuts.append(shortcut)
        
    def setup_global_shortcuts(self, main_window):
        """Initialize standard desktop shortcuts."""
        # Session
        self.register_shortcut(main_window, "Ctrl+L", SessionActions.LOCK)
        self.register_shortcut(main_window, "Cmd+L", SessionActions.LOCK)
        
        # Settings
        self.register_shortcut(main_window, "Ctrl+,", SettingsActions.OPEN)
        self.register_shortcut(main_window, "Cmd+,", SettingsActions.OPEN)
        
        # Search
        self.register_shortcut(main_window, "Ctrl+K", NavigationActions.SEARCH)
        self.register_shortcut(main_window, "Cmd+K", NavigationActions.SEARCH)
        
        # Vault
        self.register_shortcut(main_window, "Ctrl+N", VaultActions.NEW_PASSWORD)
        self.register_shortcut(main_window, "Cmd+N", VaultActions.NEW_PASSWORD)
        
        self.register_shortcut(main_window, "Ctrl+G", VaultActions.GENERATE_PASSWORD)
        self.register_shortcut(main_window, "Cmd+G", VaultActions.GENERATE_PASSWORD)
        
        self.register_shortcut(main_window, "Ctrl+E", VaultActions.EDIT)
        self.register_shortcut(main_window, "Cmd+E", VaultActions.EDIT)
