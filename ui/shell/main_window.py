from PySide6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout
from PySide6.QtCore import QSettings

from ui.views.auth.create_vault_view import CreateVaultView
from ui.views.auth.unlock_view import UnlockView
from ui.views.auth.error_view import ErrorView
from ui.workspace.shell import ApplicationShell
from ui.workspace.overlay.manager import OverlayManager
from ui.workspace.overlay.lock_overlay import LockOverlay
from ui.session.context import SessionState, SessionContext
from ui.resources.styles.metrics import Metrics
from ui.actions.action_manager import ActionManager

from ui.workspace.overlay.notification_manager import NotificationManager

class MainWindow(QMainWindow):
    """
    Root MainWindow for the MyPass application.
    Reacts to SessionController state changes to switch views.
    Never makes business decisions or queries backend.
    """
    def __init__(self, session_controller, viewmodels, model_context, details_coordinator, notification_service, search_controller, sidebar_controller, statistics_provider, parent=None):
        super().__init__(parent)
        self.session_controller = session_controller
        self.viewmodels = viewmodels
        self.model_context = model_context
        self.details_coordinator = details_coordinator
        self.notification_service = notification_service
        self.search_controller = search_controller
        self.sidebar_controller = sidebar_controller
        self.statistics_provider = statistics_provider
        self.setWindowTitle("MyPass")
        self.setMinimumSize(Metrics.WINDOW_MIN_WIDTH, Metrics.WINDOW_MIN_HEIGHT)
        
        self._init_ui()
        self._restore_geometry()
        self._connect_signals()
        
        # Register global shortcuts for this window
        ActionManager.instance().setup_global_shortcuts(self)

    def _init_ui(self):
        # We need a root widget to hold the stack and the overlay manager on top
        self.root_widget = QWidget(self)
        self.setCentralWidget(self.root_widget)
        
        # We use absolute positioning or a layout that allows overlapping. 
        # A simple way to overlap is to give OverlayManager the root widget as parent 
        # and resize it in resizeEvent.
        
        # 1. Base Stack
        self.central_stacked = QStackedWidget(self.root_widget)
        self.root_layout = QVBoxLayout(self.root_widget)
        self.root_layout.setContentsMargins(0,0,0,0)
        self.root_layout.addWidget(self.central_stacked)
        
        # 2. Views
        self.create_vault_view = CreateVaultView(self.viewmodels['create_vault'])
        self.unlock_view = UnlockView(self.viewmodels['unlock'])
        self.error_view = ErrorView()
        self.app_shell = ApplicationShell(self.model_context, self.details_coordinator, self.search_controller, self.sidebar_controller, self.statistics_provider, self)
        
        self.central_stacked.addWidget(self.create_vault_view)
        self.central_stacked.addWidget(self.unlock_view)
        self.central_stacked.addWidget(self.error_view)
        self.central_stacked.addWidget(self.app_shell)
        
        # 3. Overlays
        self.overlay_manager = OverlayManager(self.root_widget)
        # Create a second unlock view specifically for the overlay (or share it, but separate is safer for now)
        self.overlay_unlock_view = UnlockView(self.viewmodels['unlock'])
        self.lock_overlay = LockOverlay(self.overlay_unlock_view, self.overlay_manager)
        self.overlay_manager.add_overlay(self.lock_overlay)
        self.lock_overlay.hide_overlay()
        
        # Notifications overlay
        self.notification_manager = NotificationManager(self.notification_service, self.overlay_manager, self.session_controller)
        self.overlay_manager.add_overlay(self.notification_manager)

    def _connect_signals(self):
        self.session_controller.state_changed.connect(self._on_session_state_changed)
        ActionManager.instance().action_triggered.connect(self._on_global_action)
        
    def _on_global_action(self, action, payload):
        from ui.actions.settings import SettingsActions
        if action == SettingsActions.OPEN:
            from ui.dialogs.settings_dialog import SettingsDialog
            dialog = SettingsDialog(self)
            dialog.exec()
        elif action == SettingsActions.OPEN_PROFILE:
            from ui.dialogs.vault_info_dialog import VaultInfoDialog
            dialog = VaultInfoDialog(self.model_context, self)
            dialog.exec()
            
    def _on_session_state_changed(self, state: SessionState, context: SessionContext):
        """Pure UI reaction to state machine changes."""
        from utils.logging import app_logger
        app_logger.info(f"Reacting to state: {state.name}", "MainWindow")
        
        if state == SessionState.BOOTING:
            # Maybe show a loading spinner, for now nothing
            pass
            
        elif state == SessionState.NO_VAULT:
            self.lock_overlay.hide_overlay()
            self.central_stacked.setCurrentWidget(self.create_vault_view)
            
        elif state == SessionState.LOCKED:
            # Always show the lock overlay when locked.
            # If we came from LOCKING, the overlay is already visible (animated in).
            # If we're on cold start, switch to the unlock_view in the stack.
            if self.central_stacked.currentWidget() == self.app_shell:
                self.lock_overlay.show_overlay()
                self.overlay_manager.set_interactive(True)
                self.overlay_manager.raise_()
            else:
                self.central_stacked.setCurrentWidget(self.unlock_view)
                
        elif state == SessionState.LOCKING:
            if self.central_stacked.currentWidget() == self.app_shell:
                self.overlay_manager.set_interactive(True)
                self.overlay_manager.raise_()
                self.lock_overlay.animate_lock_then(lambda: self.session_controller.transition_to(SessionState.LOCKED))
            else:
                self.session_controller.transition_to(SessionState.LOCKED)
                
        elif state == SessionState.UNLOCKED:
            self.lock_overlay.hide_overlay()
            self.overlay_manager.set_interactive(False)
            self.overlay_manager.lower()
            self.central_stacked.setCurrentWidget(self.app_shell)
            
        elif state == SessionState.ERROR:
            self.lock_overlay.hide_overlay()
            self.error_view.configure(
                title="Application Error",
                message="An irrecoverable error occurred with the vault.",
                primary_text="Retry"
            )
            self.central_stacked.setCurrentWidget(self.error_view)
            
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.overlay_manager.setGeometry(self.root_widget.rect())

    def closeEvent(self, event):
        self._save_geometry()
        self.app_shell.save_state()
        super().closeEvent(event)
        
    def _save_geometry(self):
        settings = QSettings("MyPass", "MyPassApp")
        settings.setValue("window/geometry", self.saveGeometry())
        settings.setValue("window/state", self.saveState())
        
    def _restore_geometry(self):
        settings = QSettings("MyPass", "MyPassApp")
        geometry = settings.value("window/geometry")
        state = settings.value("window/state")
        if geometry:
            self.restoreGeometry(geometry)
        if state:
            self.restoreState(state)
        self.app_shell.restore_state()
