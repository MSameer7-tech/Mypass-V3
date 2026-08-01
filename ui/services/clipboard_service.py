from PySide6.QtCore import QObject, QTimer
from PySide6.QtGui import QGuiApplication
from ui.session.controller import SessionController
from ui.session.context import SessionState

class ClipboardService(QObject):
    """
    Manages secure clipboard interactions.
    Handles copying sensitive data, automatically clearing the clipboard after a timeout (only if unchanged),
    and securely purging the clipboard upon session lock.
    """
    def __init__(self, session_controller: SessionController, parent=None):
        super().__init__(parent)
        self.session_controller = session_controller
        self.clear_timer = QTimer(self)
        self.clear_timer.setSingleShot(True)
        self.clear_timer.timeout.connect(self._clear_if_unchanged)
        
        self.auto_clear_timeout_ms = 45000 # 45 seconds
        self._copied_value = None
        
        # Subscribe to session lock
        self.session_controller.state_changed.connect(self._on_session_state_changed)
        
        # Subscribe to application shutdown
        app = QGuiApplication.instance()
        if app:
            app.aboutToQuit.connect(self._on_shutdown)
            
    def _on_shutdown(self):
        """Intentionally clear owned secrets upon application exit."""
        self._clear_if_unchanged()
        
    def copy_text(self, text: str):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)
        self._copied_value = text
        
        # Start or restart the auto-clear timer
        self.clear_timer.start(self.auto_clear_timeout_ms)
        
    def _clear_if_unchanged(self):
        if not self._copied_value:
            return
            
        clipboard = QGuiApplication.clipboard()
        if clipboard.text() == self._copied_value:
            clipboard.clear()
            
        self._copied_value = None
            
    def clear_clipboard(self):
        self.clear_timer.stop()
        clipboard = QGuiApplication.clipboard()
        clipboard.clear()
        self._copied_value = None
        
    def _on_session_state_changed(self, state: SessionState, context):
        if state in (SessionState.LOCKED, SessionState.NO_VAULT):
            self.clear_clipboard()
