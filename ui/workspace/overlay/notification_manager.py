from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer
from ui.services.notification_service import NotificationService, Notification
from ui.widgets.notifications import ToastWidget

class NotificationManager(QWidget):
    """
    Subscribes to the NotificationService.
    Responsible for stacking and animating ToastWidgets over the workspace.
    """
    def __init__(self, service: NotificationService, parent=None, session_controller=None):
        super().__init__(parent)
        self.setObjectName("NotificationManager")
        self.service = service
        self.session_controller = session_controller
        
        # We must be transparent and let clicks pass through to the workspace
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setStyleSheet("background: transparent;")
        
        # We will manually position toasts rather than using a layout
        # so they can float and animate independently at the bottom right or center.
        self.active_toasts = []
        
        self.service.notification_dispatched.connect(self._on_notification)
        if self.session_controller:
            self.session_controller.state_changed.connect(self._on_session_state_changed)
            
    def _on_session_state_changed(self, state, context):
        from ui.session.context import SessionState
        if state in (SessionState.LOCKED, SessionState.NO_VAULT):
            self.clear_all()
            
    def clear_all(self):
        for toast in list(self.active_toasts):
            toast.deleteLater()
        self.active_toasts.clear()
        self._recalculate_positions()
        
    def _on_notification(self, notification: Notification):
        toast = ToastWidget(notification, self)
        # Re-enable mouse events for the toast itself
        toast.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        # Handle cleanup
        toast.destroyed.connect(lambda: self._remove_toast(toast))
        
        self.active_toasts.append(toast)
        toast.show()
        
        self._recalculate_positions()
        
    def _remove_toast(self, toast: ToastWidget):
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
        self._recalculate_positions()
        
    def _recalculate_positions(self):
        # Position toasts at the bottom right of the widget
        margin_x = 24
        margin_y = 24
        spacing = 12
        
        current_y = self.height() - margin_y
        
        for toast in reversed(self.active_toasts):
            toast.adjustSize()
            toast_w = toast.width()
            toast_h = toast.height()
            
            target_x = self.width() - toast_w - margin_x
            target_y = current_y - toast_h
            
            # Basic animation
            start_rect = toast.geometry()
            # If it's new, it might be at 0,0, so start it off-screen
            if start_rect.x() == 0 and start_rect.y() == 0:
                start_rect = QRect(target_x + 50, target_y, toast_w, toast_h)
                toast.setGeometry(start_rect)
            
            anim = QPropertyAnimation(toast, b"geometry", self)
            anim.setDuration(250)
            anim.setStartValue(start_rect)
            anim.setEndValue(QRect(target_x, target_y, toast_w, toast_h))
            anim.setEasingCurve(QEasingCurve.OutCubic)
            anim.start()
            
            # Keep reference to avoid garbage collection
            toast._anim = anim 
            
            current_y = target_y - spacing
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._recalculate_positions()
