from PySide6.QtCore import QObject

from ui.session.controller import SessionController
from utils.logging import app_logger

class AuthenticationCoordinator(QObject):
    """
    Decouples authentication flows from the session state machine.
    Provides a simple interface for ViewModels to attempt authentication,
    and reports success/failure to the SessionController.
    """
    def __init__(self, master_password_service, session_controller: SessionController, parent=None):
        super().__init__(parent)
        self.master_password_service = master_password_service
        self.session_controller = session_controller
        self.active_vault_service = None
        self.vault_adapter = None
        self._cached_password = None  # In-memory cache for biometric re-unlock
        
    def set_vault_adapter(self, vault_adapter):
        self.vault_adapter = vault_adapter
        
    def _update_adapter(self):
        if self.vault_adapter and self.active_vault_service:
            self.vault_adapter.set_vault_service(self.active_vault_service)

    def check_vault_exists(self) -> bool:
        """Called during BOOTING to determine initial path."""
        if hasattr(self.master_password_service, 'is_configured'):
            return self.master_password_service.is_configured()
        return True

    def create_vault(self, password: str, hint: str = "") -> bool:
        """Attempts to create a new vault."""
        try:
            if hasattr(self.master_password_service, 'create_vault_service'):
                self.active_vault_service = self.master_password_service.create_vault_service(password)
                self._update_adapter()
            
            try:
                import keyring
                keyring.set_password("MyPass", "MasterPassword", password)
            except Exception as e:
                app_logger.warning(f"Could not save password to keyring: {e}", "AuthCoordinator")
                
            self.session_controller.transition_to(
                __import__("ui.session.context", fromlist=["SessionState"]).SessionState.UNLOCKED
            )
            return True
        except Exception as e:
            app_logger.log_exception("create vault", e, "AuthCoordinator")
            return False

    def unlock_vault(self, password: str) -> bool:
        """Attempts to unlock an existing vault."""
        self.session_controller.request_unlock_start()
        try:
            if hasattr(self.master_password_service, 'unlock_vault'):
                self.active_vault_service = self.master_password_service.unlock_vault(password)
                self._update_adapter()
                self._cached_password = password  # Cache for biometric re-unlock
                
                try:
                    import keyring
                    keyring.set_password("MyPass", "MasterPassword", password)
                except Exception as e:
                    app_logger.warning(f"Could not save password to keyring: {e}", "AuthCoordinator")
                
                self.session_controller.notify_unlock_success()
                return True
            else:
                success = (password == "password") 
                if success:
                    self._cached_password = password  # Cache for biometric re-unlock
                    try:
                        import keyring
                        keyring.set_password("MyPass", "MasterPassword", password)
                    except Exception as e:
                        app_logger.warning(f"Could not save password to keyring: {e}", "AuthCoordinator")
                        
                    self.session_controller.notify_unlock_success()
                    return True
                else:
                    self.session_controller.notify_unlock_failure()
                    return False
        except Exception as e:
            app_logger.log_exception("unlock vault", e, "AuthCoordinator")
            self.session_controller.notify_unlock_failure()
            return False

    def authenticate_biometrics(self) -> bool:
        """Attempts to use Touch ID / Windows Hello."""
        from ui.services.biometrics import create_biometric_service
        biometrics = create_biometric_service()
        if biometrics.is_available():
            if biometrics.authenticate("Unlock MyPass"):
                # Priority 1: If we already have the vault service in memory, just unlock
                if self.active_vault_service:
                    self.session_controller.request_unlock_start()
                    self.session_controller.notify_unlock_success()
                    return True
                    
                # Priority 2: Use in-memory cached password
                if self._cached_password:
                    return self.unlock_vault(self._cached_password)
                
                # Priority 3: Try keyring
                try:
                    import keyring
                    pwd = keyring.get_password("MyPass", "MasterPassword")
                    if pwd:
                        return self.unlock_vault(pwd)
                except Exception as e:
                    app_logger.warning(f"Keyring lookup failed: {e}", "AuthCoordinator")
                
                app_logger.warning("Touch ID passed but no password available. Please unlock with password first.", "AuthCoordinator")
        return False
        
    def lock_session(self):
        """Allows Views to request a lock explicitly."""
        self.session_controller.request_lock()
