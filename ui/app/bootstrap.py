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
    
    # 1. Create Application
    app = MyPassApplication(sys.argv)
    
    logger.info("Loading services...")
    # 2. Build Services (Same as legacy app)
    database_manager = DatabaseManager(build_data_path(DATA_DIR_NAME, DB_FILE_NAME))
    repository = VaultRepository(database_manager)
    authentication_service = AuthenticationService(repository)
    master_password_service = MasterPasswordService(
        repository,
        legacy_key_file=build_data_path(DATA_DIR_NAME, LEGACY_KEY_FILE_NAME),
    )
    clipboard_service = ClipboardService(clear_after_seconds=CLIPBOARD_CLEAR_SECONDS)
    password_generator = PasswordGenerator()
    breach_detection_service = BreachDetectionService()
    password_health_service = PasswordHealthService(breach_detection_service=breach_detection_service)
    backup_service = BackupService()
    import_service = ImportService()
    session_lock_service = SessionLockService(timeout_seconds=DEFAULT_AUTO_LOCK_SECONDS)
    
    navigation_service = NavigationService()
    navigation_service.register_liveness_adapter(qt_liveness_adapter)

    # 3. Create ViewModels (Placeholders for now)
    logger.info("Initializing ViewModels...")
    
    # 4. Create Main Window
    logger.info("Creating MainWindow...")
    main_window = MainWindow(navigation_service=navigation_service)
    
    main_window.show()
    
    logger.info("Executing Qt Event Loop...")
    sys.exit(app.exec())
