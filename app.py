from config import configure_ctk
from crypto.clipboard import ClipboardService
from database.database import DatabaseManager
from database.repository import VaultRepository
from services.master_password_service import MasterPasswordService
from services.password_generator import PasswordGenerator
from ui.dashboard import DashboardWindow
from utils.constants import DATA_DIR_NAME, DB_FILE_NAME, LEGACY_KEY_FILE_NAME
from utils.helpers import build_data_path


def create_app() -> DashboardWindow:
    configure_ctk()

    database_manager = DatabaseManager(build_data_path(DATA_DIR_NAME, DB_FILE_NAME))
    repository = VaultRepository(database_manager)
    master_password_service = MasterPasswordService(
        repository,
        legacy_key_file=build_data_path(DATA_DIR_NAME, LEGACY_KEY_FILE_NAME),
    )
    clipboard_service = ClipboardService()
    password_generator = PasswordGenerator()

    return DashboardWindow(
        master_password_service=master_password_service,
        password_generator=password_generator,
        clipboard_service=clipboard_service,
    )


def main() -> None:
    app = create_app()
    app.mainloop()
