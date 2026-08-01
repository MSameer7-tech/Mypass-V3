from PySide6.QtCore import QObject, Signal, QTimer, QEvent, QCoreApplication
from PySide6.QtGui import QKeyEvent, QMouseEvent

class IdleMonitor(QObject):
    """
    Monitors user activity and emits a timeout signal after a specified duration of inactivity.
    Installed as a global event filter on the QApplication.
    """
    timeout_occurred = Signal()
    activity_detected = Signal()

    def __init__(self, timeout_seconds=300, parent=None):
        super().__init__(parent)
        self.timeout_ms = timeout_seconds * 1000
        
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._on_timeout)
        
    def start(self):
        # We need to install the event filter on the application instance
        app = QCoreApplication.instance()
        if app:
            app.installEventFilter(self)
        self.timer.start(self.timeout_ms)
        
    def stop(self):
        app = QCoreApplication.instance()
        if app:
            app.removeEventFilter(self)
        self.timer.stop()
        
    def reset(self):
        if self.timer.isActive():
            self.timer.start(self.timeout_ms)
        self.activity_detected.emit()
            
    def _on_timeout(self):
        self.timeout_occurred.emit()
        
    def eventFilter(self, obj, event):
        """Catch relevant events to reset the idle timer."""
        # We track MouseMove, MouseButtonPress, KeyPress, WindowActivate
        if event.type() in (QEvent.MouseMove, QEvent.MouseButtonPress, 
                            QEvent.KeyPress, QEvent.WindowActivate,
                            QEvent.Clipboard):
            self.reset()
        
        return super().eventFilter(obj, event)
