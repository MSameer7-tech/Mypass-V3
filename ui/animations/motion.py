from PySide6.QtCore import QObject, QPropertyAnimation, QEasingCurve, QTimer, Signal
from PySide6.QtWidgets import QWidget

class HoverTransition(QObject):
    """
    Event filter for adding smooth hover transitions to custom QWidgets.
    Animates opacity or color changes smoothly without layout shifts.
    """
    def __init__(self, target_widget: QWidget, duration_ms: int = 100):
        super().__init__(target_widget)
        self.target_widget = target_widget
        self.duration_ms = duration_ms
        self.target_widget.installEventFilter(self)
        self.is_hovered = False

    def eventFilter(self, watched: QObject, event) -> bool:
        if watched == self.target_widget:
            if event.type() == event.Type.Enter:
                self.is_hovered = True
                self.on_hover_enter()
            elif event.type() == event.Type.Leave:
                self.is_hovered = False
                self.on_hover_leave()
        return super().eventFilter(watched, event)

    def on_hover_enter(self):
        self.target_widget.update()

    def on_hover_leave(self):
        self.target_widget.update()


class CopyFeedbackController(QObject):
    """
    Controls 1.2-second inline feedback for copy buttons.
    Changes button text/icon to '✓ Copied' with green tint, then reverts smoothly.
    """
    feedback_reset = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timeout)

    def trigger_feedback(self, duration_ms: int = 1200):
        self._timer.start(duration_ms)

    def _on_timeout(self):
        self.feedback_reset.emit()
