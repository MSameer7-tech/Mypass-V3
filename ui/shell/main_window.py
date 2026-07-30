from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget
from ui.views.login.login_view import LoginView
from ui.views.dashboard.dashboard_view import DashboardView

class MainWindow(QMainWindow):
    """
    Root MainWindow for the MyPass application.
    Composes layout shells (Toolbar, Sidebar, Workspace).
    Does not contain business logic.
    """
    
    def __init__(self, navigation_service, parent=None):
        super().__init__(parent)
        self.navigation_service = navigation_service
        self.setWindowTitle("MyPass")
        self.resize(1120, 700)
        self._init_ui()
        self._setup_navigation()

    def _init_ui(self):
        # We use a stacked widget for the top-level views: Login vs App Shell
        self.central_stacked = QStackedWidget(self)
        self.setCentralWidget(self.central_stacked)
        
        # Placeholders for Phase 0
        self.login_view = LoginView(self)
        self.dashboard_view = DashboardView(self)
        
        self.central_stacked.addWidget(self.login_view)
        self.central_stacked.addWidget(self.dashboard_view)

    def _setup_navigation(self):
        # Subscribe to view changes from NavigationService
        self.navigation_service.on_view_changed(self._on_view_changed)
        
        # Initial view state
        self._on_view_changed(self.navigation_service.get_current_view())

    def _on_view_changed(self, view_name: str) -> None:
        if view_name == "login":
            self.central_stacked.setCurrentWidget(self.login_view)
        elif view_name == "dashboard":
            self.central_stacked.setCurrentWidget(self.dashboard_view)
        else:
            # Default fallback for testing
            self.central_stacked.setCurrentWidget(self.login_view)
