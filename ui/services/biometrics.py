import platform
from PySide6.QtCore import QObject, Signal, Slot
from utils.logging import app_logger

class BiometricService(QObject):
    """Abstract interface for biometric authentication."""
    auth_result = Signal(bool)  # Emitted with True/False after authentication
    
    def is_available(self) -> bool:
        return False
        
    def authenticate_async(self, prompt: str):
        """Start authentication. Listen to auth_result signal for the outcome."""
        self.auth_result.emit(False)

class DummyBiometricService(BiometricService):
    pass

class MacBiometricService(BiometricService):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._available = None
        
    def is_available(self) -> bool:
        if self._available is not None:
            return self._available
            
        try:
            import objc
            from LocalAuthentication import LAContext, LAPolicyDeviceOwnerAuthenticationWithBiometrics
            
            context = LAContext.alloc().init()
            success, error = context.canEvaluatePolicy_error_(LAPolicyDeviceOwnerAuthenticationWithBiometrics, None)
            self._available = bool(success)
            return self._available
        except ImportError:
            app_logger.warning("pyobjc or LocalAuthentication not installed. Biometrics unavailable.", "MacBiometricService")
            self._available = False
            return False
        except Exception as e:
            app_logger.log_exception("check biometrics availability", e, "MacBiometricService")
            self._available = False
            return False
    
    @Slot(bool)
    def _emit_result(self, success: bool):
        """Slot that runs on the main thread to emit the signal."""
        app_logger.info(f"Biometric authentication result: {success}", "MacBiometricService")
        self.auth_result.emit(success)
            
    def authenticate_async(self, prompt: str):
        """Start Touch ID authentication. Result comes via auth_result signal."""
        if not self.is_available():
            self.auth_result.emit(False)
            return
            
        try:
            import objc
            from LocalAuthentication import LAContext, LAPolicyDeviceOwnerAuthenticationWithBiometrics
            
            # Keep a strong reference so the context isn't GC'd before the callback
            self._la_context = LAContext.alloc().init()
            
            def reply_handler(success, error):
                # This runs on a background GCD queue.
                # Emit the signal directly — Qt AutoConnection will queue it
                # to the main thread since self lives on the main thread.
                val = bool(success)
                self.auth_result.emit(val)
                
            self._la_context.evaluatePolicy_localizedReason_reply_(
                LAPolicyDeviceOwnerAuthenticationWithBiometrics,
                prompt,
                reply_handler
            )
            # Returns immediately — result comes via auth_result signal
            
        except Exception as e:
            app_logger.log_exception("authenticate via biometrics", e, "MacBiometricService")
            self.auth_result.emit(False)

def create_biometric_service(parent=None) -> BiometricService:
    if platform.system() == "Darwin":
        return MacBiometricService(parent)
    return DummyBiometricService(parent)
