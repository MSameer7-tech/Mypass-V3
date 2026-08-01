from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Callable, Any
from PySide6.QtCore import QObject, Signal

class NotificationLevel(Enum):
    INFO = auto()
    SUCCESS = auto()
    WARNING = auto()
    ERROR = auto()
    PROGRESS = auto()

@dataclass
class NotificationAction:
    label: str
    # Can be a callback or a Command instance
    command: Optional[Any] = None 
    callback: Optional[Callable[[], None]] = None
    
    def execute(self):
        if self.command and hasattr(self.command, 'execute'):
            self.command.execute()
        elif self.callback:
            self.callback()

@dataclass
class Notification:
    level: NotificationLevel
    title: str
    message: str
    duration_ms: int = 3000
    primary_action: Optional[NotificationAction] = None
    secondary_action: Optional[NotificationAction] = None
    icon: Optional[str] = None
    persistent: bool = False

class NotificationService(QObject):
    """
    Centralized service for dispatching application-wide feedback.
    Decoupled from Qt widgets. A NotificationManager listens to this service
    and is responsible for the actual rendering logic.
    """
    notification_dispatched = Signal(Notification)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def notify(self, notification: Notification) -> None:
        self.notification_dispatched.emit(notification)
        
    # Helper methods for standard use cases
    def show_success(self, title: str, message: str = "", duration_ms: int = 3000, primary_action: Optional[NotificationAction] = None) -> None:
        self.notify(Notification(
            level=NotificationLevel.SUCCESS,
            title=title,
            message=message,
            duration_ms=duration_ms,
            primary_action=primary_action,
            icon="check-circle"
        ))
        
    def show_error(self, title: str, message: str = "", duration_ms: int = 5000, persistent: bool = False) -> None:
        self.notify(Notification(
            level=NotificationLevel.ERROR,
            title=title,
            message=message,
            duration_ms=duration_ms,
            persistent=persistent,
            icon="alert-circle"
        ))
        
    def show_warning(self, title: str, message: str = "", duration_ms: int = 4000) -> None:
        self.notify(Notification(
            level=NotificationLevel.WARNING,
            title=title,
            message=message,
            duration_ms=duration_ms,
            icon="alert-triangle"
        ))
        
    def show_info(self, title: str, message: str = "", duration_ms: int = 3000, primary_action: Optional[NotificationAction] = None) -> None:
        self.notify(Notification(
            level=NotificationLevel.INFO,
            title=title,
            message=message,
            duration_ms=duration_ms,
            primary_action=primary_action,
            icon="info"
        ))
