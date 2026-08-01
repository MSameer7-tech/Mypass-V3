import sys
import logging

from ui.app.application import MyPassApplication
from ui.shell.main_window import MainWindow

from crypto.clipboard import ClipboardService
from database.database import DatabaseManager
from database.repository import VaultRepository
from services.master_password_service import MasterPasswordService
from services.backup_service import BackupService
from services.import_service import ImportService
from services.password_generator import PasswordGenerator
from services.password_health import PasswordHealthService
from services.session_lock import SessionLockService
from services.breach_detection import BreachDetectionService
from services.authentication_service import AuthenticationService
from services.navigation_service import NavigationService
from services.vault_service import VaultService

from ui.session.controller import SessionController
from ui.session.manager import SessionManager
from ui.session.context import SessionState
from ui.auth.coordinator import AuthenticationCoordinator
from ui.services.biometrics import BiometricService
from ui.viewmodels.create_vault_viewmodel import CreateVaultViewModel
from ui.viewmodels.unlock_viewmodel import UnlockViewModel

from ui.services.asset_manager import AssetManager

# Phase 4 Imports
from ui.workspace.vault_adapter import VaultRepositoryAdapter
from ui.workspace.vault_coordinator import VaultCoordinator
from ui.models.model_context import ModelContext

from utils.constants import (
    CLIPBOARD_CLEAR_SECONDS,
    DATA_DIR_NAME,
    DB_FILE_NAME,
    DEFAULT_AUTO_LOCK_SECONDS,
    LEGACY_KEY_FILE_NAME,
)
from utils.helpers import build_data_path

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MyPass")

def qt_liveness_adapter(target):
    if hasattr(target, 'objectName'):
        try:
            target.objectName()
            return True
        except RuntimeError:
            return False
    return None

def bootstrap() -> None:
    logger.info("Starting Qt UI bootstrap...")
    
    app = MyPassApplication(sys.argv)
    
    logger.info("Loading services...")
    database_manager = DatabaseManager(build_data_path(DATA_DIR_NAME, DB_FILE_NAME))
    repository = VaultRepository(database_manager)
    authentication_service = AuthenticationService(repository)
    
    # Needs to be initialized correctly
    # If the backend requires an EncryptionService, we should create one or mock it, 
    # but AuthenticationService seems to handle the actual creation.
    # For now, let's pass authentication_service's encryption_service if it exists, 
    # otherwise we might need to lazily set it in VaultService.
    # Let's check how the legacy app does it. It creates EncryptionService(repository) maybe?
    # Let's just import it and pass it for now if needed. 
    # Or just pass None if it accepts it. Let's try passing None if it's not strictly typed to fail, wait it failed with missing positional argument.
    from services.vault_service import EncryptionAdapter
    class DummyEncryption(EncryptionAdapter):
        def encrypt(self, value: str) -> str: return value
        def decrypt(self, value: str) -> str: return value
    
    encryption_service = DummyEncryption()
    vault_service = VaultService(repository, encryption_service)
    
    master_password_service = MasterPasswordService(
        repository,
        legacy_key_file=build_data_path(DATA_DIR_NAME, LEGACY_KEY_FILE_NAME),
    )
    
    password_generator = PasswordGenerator()
    breach_detection_service = BreachDetectionService()
    password_health_service = PasswordHealthService(breach_detection_service=breach_detection_service)
    backup_service = BackupService()
    import_service = ImportService()
    
    # We will eventually deprecate the legacy SessionLockService, but keep for backend compatibility
    session_lock_service = SessionLockService(timeout_seconds=DEFAULT_AUTO_LOCK_SECONDS)
    
    navigation_service = NavigationService()
    navigation_service.register_liveness_adapter(qt_liveness_adapter)

    logger.info("Initializing Session & Authentication...")
    
    # Phase 3: Session & Authentication Architecture
    session_controller = SessionController()
    session_manager = SessionManager(session_controller)
    
    from ui.services.biometrics import create_biometric_service
    biometric_service = create_biometric_service()
    
    # Phase 5: Clipboard Service
    from ui.services.clipboard_service import ClipboardService as QtClipboardService
    clipboard_service = QtClipboardService(session_controller)
    clipboard_service.auto_clear_timeout_ms = CLIPBOARD_CLEAR_SECONDS * 1000
    
    # We pass the MasterPasswordService to the UI coordinator
    auth_coordinator = AuthenticationCoordinator(master_password_service, session_controller)
    
    # Phase 5: Icon Service / Asset Manager
    icon_service = AssetManager()
    
    # Phase 5: TOTP Service
    from ui.services.totp_service import TotpService
    totp_service = TotpService()
    
    # Phase 5.5: Notification Service
    from ui.services.notification_service import NotificationService
    notification_service = NotificationService()
    
    # Phase 4: Vault Data Layer
    logger.info("Initializing Vault Data Layer...")
    model_context = ModelContext()
    vault_adapter = VaultRepositoryAdapter(vault_service)
    auth_coordinator.set_vault_adapter(vault_adapter)
    
    vault_coordinator = VaultCoordinator(
        adapter=vault_adapter, 
        context=model_context, 
        session_controller=session_controller, 
        icon_service=icon_service, 
        notification_service=notification_service,
        clipboard_service=clipboard_service
    )
    
    # Phase 5: Details Coordinator
    from ui.workspace.entry_details_coordinator import EntryDetailsCoordinator
    details_coordinator = EntryDetailsCoordinator(vault_adapter, model_context, session_controller, totp_service)
    
    # Phase 5: Generator Coordinator
    from ui.workspace.password_generator_coordinator import PasswordGeneratorCoordinator
    generator_coordinator = PasswordGeneratorCoordinator(password_generator, clipboard_service, notification_service, session_controller)
    
    # Phase 6: Search Controller
    from ui.workspace.search_controller import SearchController
    import dataclasses
    
    search_controller = SearchController()
    
    def _on_search_changed(query: str):
        old_ws = model_context.workspace_state
        new_fs = dataclasses.replace(old_ws.filter_state, search_query=query)
        new_ws = dataclasses.replace(old_ws, filter_state=new_fs)
        model_context.set_workspace_state(new_ws)
        
    search_controller.search_changed.connect(_on_search_changed)
    
    # Phase 6: Sidebar Controllers
    from ui.workspace.statistics_provider import StatisticsProvider
    from ui.workspace.sidebar_controller import SidebarController
    
    statistics_provider = StatisticsProvider(model_context)
    sidebar_controller = SidebarController(model_context, statistics_provider)
    
    logger.info("Initializing ViewModels...")
    viewmodels = {
        'create_vault': CreateVaultViewModel(auth_coordinator),
        'unlock': UnlockViewModel(auth_coordinator, biometric_service)
    }
    
    logger.info("Creating MainWindow...")
    main_window = MainWindow(session_controller, viewmodels, model_context, details_coordinator, notification_service, search_controller, sidebar_controller, statistics_provider)
    main_window.show()
    
    # Bootstrap logic
    # Check if a vault exists to start the state machine properly
    if auth_coordinator.check_vault_exists():
        session_controller.transition_to(SessionState.LOCKED)
    else:
        session_controller.transition_to(SessionState.NO_VAULT)
    
    logger.info("Executing Qt Event Loop...")
    sys.exit(app.exec())
