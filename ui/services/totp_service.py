from PySide6.QtCore import QObject, Signal, QTimer
import time
import math

class TotpService(QObject):
    """
    Acts as the single source of truth for TOTP timing and generation across the UI.
    Emits signals every second to keep all UI components synchronized without them needing their own timers.
    """
    # Emits: remaining_seconds, progress_percentage (0.0 to 1.0)
    tick = Signal(int, float)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.period = 30
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(1000)
        
    def _on_tick(self):
        current_time = time.time()
        # TOTP period is usually 30 seconds, starting from Unix Epoch 0
        time_elapsed = current_time % self.period
        remaining_seconds = int(math.ceil(self.period - time_elapsed))
        if remaining_seconds == 0:
            remaining_seconds = self.period
            
        progress = (self.period - time_elapsed) / self.period
        
        self.tick.emit(remaining_seconds, max(0.0, min(1.0, progress)))
        
    def generate_code(self, secret: str) -> str:
        """
        Scaffolding for TOTP generation. 
        Will integrate with pyotp or a similar backend service in the future.
        """
        if not secret:
            return ""
        return "123456" # Placeholder for Phase 6 scaffolding
