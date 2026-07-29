from config import configure_ctk
from crypto.clipboard import ClipboardService
from database.database import DatabaseManager
from database.repository import VaultRepository
from services.master_password_service import MasterPasswordService
from services.backup_service import BackupService
from services.import_service import ImportService
from services.password_generator import PasswordGenerator
from services.password_health import PasswordHealthService
from services.session_lock import SessionLockService
from ui.dashboard import DashboardWindow
from utils.constants import (
    CLIPBOARD_CLEAR_SECONDS,
    DATA_DIR_NAME,
    DB_FILE_NAME,
    DEFAULT_AUTO_LOCK_SECONDS,
    LEGACY_KEY_FILE_NAME,
)
from utils.helpers import build_data_path


def create_app() -> DashboardWindow:
    configure_ctk()

    database_manager = DatabaseManager(build_data_path(DATA_DIR_NAME, DB_FILE_NAME))
    repository = VaultRepository(database_manager)
    master_password_service = MasterPasswordService(
        repository,
        legacy_key_file=build_data_path(DATA_DIR_NAME, LEGACY_KEY_FILE_NAME),
    )
    clipboard_service = ClipboardService(clear_after_seconds=CLIPBOARD_CLEAR_SECONDS)
    password_generator = PasswordGenerator()
    password_health_service = PasswordHealthService()
    backup_service = BackupService()
    import_service = ImportService()
    session_lock_service = SessionLockService(timeout_seconds=DEFAULT_AUTO_LOCK_SECONDS)

    return DashboardWindow(
        master_password_service=master_password_service,
        password_generator=password_generator,
        password_health_service=password_health_service,
        backup_service=backup_service,
        import_service=import_service,
        clipboard_service=clipboard_service,
        session_lock_service=session_lock_service,
    )


def main() -> None:
    app = create_app()
    app.mainloop()
