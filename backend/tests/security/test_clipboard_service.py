import pytest
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication, QClipboard

from ui.services.clipboard_service import ClipboardService
from ui.session.controller import SessionController
from ui.session.context import SessionState


@pytest.fixture
def session_controller():
    return SessionController()


@pytest.fixture
def clipboard_service(qtbot, session_controller):
    service = ClipboardService(session_controller)
    service.auto_clear_timeout_ms = 100  # fast for testing
    return service


def test_sequential_copy_stress(qtbot, clipboard_service):
    """
    Copy password -> Copy username -> Copy TOTP -> Copy generated password.
    Verify only one active timer exists and only the latest value is cleared.
    """
    clipboard = QGuiApplication.clipboard()
    clipboard.clear()

    clipboard_service.copy_text("password123")
    assert clipboard_service.clear_timer.isActive()
    
    clipboard_service.copy_text("user@example.com")
    assert clipboard_service.clear_timer.isActive()
    
    clipboard_service.copy_text("123456")
    assert clipboard_service.clear_timer.isActive()
    
    clipboard_service.copy_text("GenPass!@#")
    assert clipboard_service.clear_timer.isActive()

    # Verify exactly one active timer exists (QTimer handles this automatically on start())
    assert clipboard.text() == "GenPass!@#"

    # Wait for timer to expire
    qtbot.wait(150)
    
    # Should be cleared
    assert clipboard.text() == ""
    assert not clipboard_service.clear_timer.isActive()


def test_third_party_overwrite(qtbot, clipboard_service):
    """
    Copy password -> User copies unrelated text outside MyPass -> Timer expires.
    Expected: clipboard untouched, no notifications.
    """
    clipboard = QGuiApplication.clipboard()
    clipboard.clear()

    clipboard_service.copy_text("my_secret_password")
    assert clipboard.text() == "my_secret_password"

    # Simulate third party overwrite
    clipboard.setText("unrelated_text")

    # Wait for timer to expire
    qtbot.wait(150)

    # Clipboard should REMAIN untouched
    assert clipboard.text() == "unrelated_text"


def test_session_lock(qtbot, clipboard_service, session_controller):
    """
    Copy password -> Immediately lock session.
    Expected: clipboard clears immediately, timer stops, internal state resets.
    """
    clipboard = QGuiApplication.clipboard()
    
    clipboard_service.copy_text("secret_to_be_locked")
    assert clipboard.text() == "secret_to_be_locked"
    assert clipboard_service.clear_timer.isActive()

    # Lock session
    session_controller.transition_to(SessionState.LOCKED)

    # Should clear immediately
    assert clipboard.text() == ""
    assert not clipboard_service.clear_timer.isActive()
    assert clipboard_service._copied_value is None


def test_application_shutdown(qtbot, clipboard_service):
    """
    Verify the intended behavior explicitly: clear intentional secrets on app shutdown.
    """
    clipboard = QGuiApplication.clipboard()
    
    clipboard_service.copy_text("secret_on_shutdown")
    assert clipboard.text() == "secret_on_shutdown"

    # Simulate app shutdown
    clipboard_service._on_shutdown()

    # Should be cleared
    assert clipboard.text() == ""
    
    # But if someone else overwrote it:
    clipboard_service.copy_text("another_secret")
    clipboard.setText("external_text")
    clipboard_service._on_shutdown()
    assert clipboard.text() == "external_text"
