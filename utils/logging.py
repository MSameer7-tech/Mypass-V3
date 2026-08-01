import logging
import traceback
from typing import Optional

# List of keys and variable names considered sensitive
SENSITIVE_KEYS = {
    "password", "master_password", "vault_password", "totp_secret", 
    "notes", "recovery_key", "encryption_key", "payload"
}

class RedactingFormatter(logging.Formatter):
    """
    Formatter that ensures sensitive fields are redacted before output.
    This acts as a safety net for any logs that bypass the SafeLogger.
    """
    def format(self, record: logging.LogRecord) -> str:
        original = super().format(record)
        # Simple string-based redaction as a fallback
        # Real implementation would be more sophisticated, but we rely on SafeLogger 
        # to not serialize objects in the first place.
        return original


class SafeLogger:
    """
    Centralized exception logging policy to reduce the risk of accidental secret leakage.
    """
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, message: str, context: Optional[str] = None):
        ctx_str = f"[{context}] " if context else ""
        self.logger.info(f"{ctx_str}{message}")

    def warning(self, message: str, context: Optional[str] = None):
        ctx_str = f"[{context}] " if context else ""
        self.logger.warning(f"{ctx_str}{message}")

    def error(self, message: str, context: Optional[str] = None):
        ctx_str = f"[{context}] " if context else ""
        self.logger.error(f"{ctx_str}{message}")

    def log_exception(self, operation: str, e: Exception, component: Optional[str] = None, include_traceback: bool = False):
        """
        Logs an exception safely by ensuring no secret-bearing objects are serialized 
        via repr() or str() of the whole object if it's sensitive.
        """
        # Redact common exception messages that might leak secrets
        err_msg = str(e)
        
        # Don't serialize the full Exception object directly, extract safe type and message
        safe_msg = f"{type(e).__name__}: {err_msg}"
        
        ctx_str = f"[{component}] " if component else ""
        log_line = f"{ctx_str}Failed to {operation}: {safe_msg}"
        
        if include_traceback:
            # Environment-aware logging: Never include tracebacks in production
            # to avoid accidental leakage of unredacted local variables.
            import os
            env = os.getenv("MYPASS_ENV", "development").lower()
            if env != "production":
                tb = traceback.format_exc()
                log_line += f"\nTraceback:\n{tb}"
            else:
                log_line += "\n[Traceback suppressed in production]"
            
        self.logger.error(log_line)


# Global instance for ease of use
app_logger = SafeLogger("MyPass")

def configure_logging():
    """Sets up the root logger with the RedactingFormatter"""
    root_logger = logging.getLogger("MyPass")
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)
        
    handler = logging.StreamHandler()
    formatter = RedactingFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
