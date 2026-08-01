from PySide6.QtCore import QObject, Signal

class UnlockViewModel(QObject):
    # Signals
    unlock_started = Signal()
    unlock_success = Signal()
    unlock_failed = Signal(str)
    biometric_prompt = Signal(str)
    
    def __init__(self, auth_coordinator, biometric_service, parent=None):
        super().__init__(parent)
        self.coordinator = auth_coordinator
        self.biometrics = biometric_service
        
        # Connect biometric result signal
        self.biometrics.auth_result.connect(self._on_biometric_result)
        
    def unlock(self, password: str):
        if not password:
            self.unlock_failed.emit("Password cannot be empty.")
            return
            
        self.unlock_started.emit()
        success = self.coordinator.unlock_vault(password)
        
        if success:
            self.unlock_success.emit()
        else:
            self.unlock_failed.emit("Incorrect master password.")
            
    def attempt_biometric_unlock(self):
        if self.biometrics.is_available():
            # Check if we actually have a way to unlock (cached password or vault service)
            has_cached = (self.coordinator._cached_password is not None or 
                         self.coordinator.active_vault_service is not None)
            if not has_cached:
                self.unlock_failed.emit("Please unlock with your password first to enable Touch ID.")
                return
                
            self.biometric_prompt.emit("Unlock MyPass Vault")
            # This returns immediately — result comes via _on_biometric_result
            self.biometrics.authenticate_async("Unlock MyPass")
    
    def _on_biometric_result(self, success: bool):
        """Called on main thread when Touch ID completes."""
        if success:
            # Use cached password or vault service to actually unlock
            if self.coordinator.active_vault_service:
                self.coordinator.session_controller.request_unlock_start()
                self.coordinator.session_controller.notify_unlock_success()
                self.unlock_success.emit()
            elif self.coordinator._cached_password:
                result = self.coordinator.unlock_vault(self.coordinator._cached_password)
                if result:
                    self.unlock_success.emit()
                else:
                    self.unlock_failed.emit("Failed to unlock vault.")
            else:
                self.unlock_failed.emit("No cached credentials available.")
        else:
            self.unlock_failed.emit("Touch ID authentication was canceled.")
