from PySide6.QtWidgets import QFrame, QVBoxLayout, QGraphicsBlurEffect
from PySide6.QtCore import Qt

from ui.views.auth.unlock_view import UnlockView

class LockOverlay(QFrame):
    """
    An overlay that visually obscures the workspace and presents the UnlockView.
    """
    def __init__(self, unlock_view: UnlockView, parent=None):
        super().__init__(parent)
        self.setObjectName("LockOverlay")
        
        # Intercept mouse events so they don't reach the workspace below
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        
        # Semi-transparent dark background (fallback for blur)
        # In a real app, we might grab the parent's pixmap and apply a blur, 
        # or use QGraphicsBlurEffect on the parent widget.
        # Using a fully opaque dark background for a clean locked state
        self.setStyleSheet("background-color: rgb(18, 18, 22);")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.unlock_view = unlock_view
        # Ensure UnlockView has a transparent background so it looks good on the overlay
        self.unlock_view.setStyleSheet("background: transparent;")
        layout.addWidget(self.unlock_view)
        
    def show_overlay(self):
        self.show()
        # Make sure opacity effect is fully opaque if shown instantly
        if not hasattr(self, 'opacity_effect'):
            from PySide6.QtWidgets import QGraphicsOpacityEffect
            self.opacity_effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)
        self.unlock_view.prepare_for_input()
        
    def hide_overlay(self):
        if hasattr(self, 'opacity_effect'):
            self.opacity_effect.setOpacity(0.0)
        self.hide()

    def animate_lock_then(self, callback):
        from PySide6.QtWidgets import QGraphicsOpacityEffect
        from PySide6.QtCore import QPropertyAnimation, QEasingCurve
        
        self.show()
        
        if not hasattr(self, 'opacity_effect'):
            self.opacity_effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(self.opacity_effect)
            
        self.opacity_effect.setOpacity(0.0)
        
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(200) # 200ms fade
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        def _on_finished():
            self.unlock_view.prepare_for_input()
            callback()
            
        self.anim.finished.connect(_on_finished)
        self.anim.start()
