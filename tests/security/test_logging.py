import pytest
import logging
from io import StringIO
from utils.logging import SafeLogger, RedactingFormatter

def test_sec_002_safe_logger_no_secret_leak():
    """SEC-002: SafeLogger must not serialize full Exception objects with locals."""
    logger = SafeLogger("TestSafeLogger")
    
    # We create a dummy exception that holds a secret
    class SecretException(Exception):
        def __init__(self, msg, secret):
            super().__init__(msg)
            self.secret = secret
            
        def __repr__(self):
            return f"SecretException('{self.args[0]}', secret='{self.secret}')"
            
    # Intercept log output
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    formatter = RedactingFormatter("%(message)s")
    handler.setFormatter(formatter)
    
    logger.logger.addHandler(handler)
    logger.logger.setLevel(logging.ERROR)
    
    try:
        secret_val = "SUPER_SECRET_MASTER_PASSWORD"
        raise SecretException("Failed to decrypt", secret_val)
    except Exception as e:
        logger.log_exception("decrypt", e, "CryptoModule")
        
    log_output = stream.getvalue()
    
    # Assert the safe message was logged
    assert "Failed to decrypt: SecretException: Failed to decrypt" in log_output
    # Assert the secret was NOT logged (e.g. from __repr__)
    assert "SUPER_SECRET_MASTER_PASSWORD" not in log_output

    logger.logger.removeHandler(handler)
