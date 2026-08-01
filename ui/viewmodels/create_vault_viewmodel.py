from PySide6.QtCore import QObject, Signal

class CreateVaultViewModel(QObject):
    # Signals
    creation_started = Signal()
    creation_success = Signal()
    creation_failed = Signal(str)
    
    def __init__(self, auth_coordinator, parent=None):
        super().__init__(parent)
        self.coordinator = auth_coordinator
        
    def create_vault(self, password: str, confirm_password: str, hint: str = ""):
        if password != confirm_password:
            self.creation_failed.emit("Passwords do not match.")
            return
            
        if len(password) < 8:
            self.creation_failed.emit("Password must be at least 8 characters.")
            return
            
        self.creation_started.emit()
        
        # Call coordinator
        success = self.coordinator.create_vault(password, hint)
        if success:
            self.creation_success.emit()
        else:
            self.creation_failed.emit("Failed to create vault.")
