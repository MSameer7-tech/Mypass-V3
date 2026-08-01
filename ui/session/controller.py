from PySide6.QtCore import QObject, Signal
from datetime import datetime
from utils.logging import app_logger

from ui.session.context import SessionState, SessionContext, LockReason

class SessionController(QObject):
    """
    The strict state machine for the application session.
    Only this component is allowed to mutate the session state.
    """
    
    # Emitted whenever the session state or context changes
    state_changed = Signal(SessionState, SessionContext)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.context = SessionContext()
        
    def _is_transition_allowed(self, current: SessionState, target: SessionState) -> bool:
        allowed = {
            SessionState.BOOTING: [SessionState.NO_VAULT, SessionState.LOCKED, SessionState.ERROR],
            SessionState.NO_VAULT: [SessionState.UNLOCKING],
            SessionState.LOCKED: [SessionState.UNLOCKING],
            SessionState.UNLOCKING: [SessionState.UNLOCKED, SessionState.ERROR, SessionState.LOCKED],
            SessionState.UNLOCKED: [SessionState.LOCKING],
            SessionState.LOCKING: [SessionState.LOCKED],
            SessionState.ERROR: [SessionState.LOCKED, SessionState.NO_VAULT]
        }
        return target in allowed.get(current, [])

    def transition_to(self, target_state: SessionState, **kwargs):
        """
        Request a state transition. Updates the context and emits state_changed if allowed.
        Accepts kwargs to update the context (e.g., lock_reason).
        """
        if not self._is_transition_allowed(self.context.state, target_state):
            app_logger.warning(f"Invalid transition requested: {self.context.state.name} -> {target_state.name}", "SessionController")
            return False
        app_logger.info(f"Transition: {self.context.state.name} -> {target_state.name}", "SessionController")
        self.context.state = target_state
        self.context.last_activity = datetime.now()
        
        # Update context with any provided kwargs
        for k, v in kwargs.items():
            if hasattr(self.context, k):
                setattr(self.context, k, v)
                
        self.state_changed.emit(self.context.state, self.context)
        return True
        
    def request_lock(self, reason: LockReason = LockReason.USER_REQUEST):
        """Helper to begin the locking process."""
        if self.context.state == SessionState.UNLOCKED:
            # We transition to LOCKING, and the UI should animate the fade,
            # then call transition_to(SessionState.LOCKED) when done.
            self.transition_to(SessionState.LOCKING, lock_reason=reason)
                
    def request_unlock_start(self):
        """Helper to begin the unlocking process."""
        if self.context.state in [SessionState.LOCKED, SessionState.NO_VAULT]:
            self.transition_to(SessionState.UNLOCKING)
            
    def notify_unlock_success(self):
        """Helper for coordinator to report success."""
        if self.context.state == SessionState.UNLOCKING:
            self.transition_to(SessionState.UNLOCKED, lock_reason=LockReason.NONE)
            
    def notify_unlock_failure(self):
        """Helper for coordinator to report failure."""
        if self.context.state == SessionState.UNLOCKING:
            self.transition_to(SessionState.LOCKED, lock_reason=LockReason.FAILED_AUTH)
