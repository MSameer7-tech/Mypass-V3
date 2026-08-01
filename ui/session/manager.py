from PySide6.QtCore import QObject

from ui.session.controller import SessionController
from ui.session.idle_monitor import IdleMonitor
from ui.session.context import SessionState, LockReason
from utils.logging import app_logger
from ui.actions.action_manager import ActionManager
from ui.actions.session import SessionActions

class SessionManager(QObject):
    """
    Coordinates policies around session state (e.g., locking on idle timeout) 
    and subscribes to global session actions.
    """
    def __init__(self, session_controller: SessionController, parent=None):
        super().__init__(parent)
        self.controller = session_controller
        
        self.idle_monitor = IdleMonitor(timeout_seconds=300, parent=self) # 5 minutes default
        self.idle_monitor.timeout_occurred.connect(self._on_idle_timeout)
        
        # Listen to state changes to start/stop the idle monitor
        self.controller.state_changed.connect(self._on_state_changed)
        
        # Subscribe to global actions
        ActionManager.instance().action_triggered.connect(self._on_action_triggered)
        
    def _on_state_changed(self, state: SessionState, context):
        if state == SessionState.UNLOCKED:
            self.idle_monitor.start()
        else:
            self.idle_monitor.stop()
            
    def _on_idle_timeout(self):
        """Called when the user has been inactive for too long."""
        app_logger.info("Idle timeout reached. Requesting lock.", "SessionManager")
        self.controller.request_lock(reason=LockReason.IDLE_TIMEOUT)
        
    def _on_action_triggered(self, action, payload):
        if action == SessionActions.LOCK:
            app_logger.info("Global lock action triggered.", "SessionManager")
            self.controller.request_lock(reason=LockReason.USER_REQUEST)
        # SessionActions.UNLOCK is typically handled via AuthenticationCoordinator
