from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt

from ui.workspace.overlay.lock_overlay import LockOverlay
# Import future overlays like ToastOverlay here

class OverlayManager(QWidget):
    """
    Manages overlays that sit on top of the ApplicationShell.
    Dynamically toggles mouse pass-through based on overlay visibility.
    """
    def __init__(self, parent=None):
        # Must be a child of ApplicationShell or MainWindow to float on top
        super().__init__(parent)
        self.setObjectName("OverlayManager")
        
        # Start transparent — no overlays active yet
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setStyleSheet("background: transparent;")
        
        self._overlays = []
        
    def add_overlay(self, overlay_widget: QWidget):
        overlay_widget.setParent(self)
        self._overlays.append(overlay_widget)
        # Force initial geometry
        overlay_widget.setGeometry(self.rect())
        
    def set_interactive(self, interactive: bool):
        """When an overlay is shown, the manager must intercept mouse events.
        When all overlays are hidden, pass events through."""
        self.setAttribute(Qt.WA_TransparentForMouseEvents, not interactive)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Ensure overlays resize to fill the manager
        for widget in self._overlays:
            widget.setGeometry(self.rect())
