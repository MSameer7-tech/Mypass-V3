# ui/shell/__init__.py
# Exports desktop workspace shell layout components

from .app_shell import ApplicationShell
from .workspace import Workspace
from .toolbar import Toolbar
from .sidebar import Sidebar
from .password_list import PasswordList
from .details_pane import DetailsPane

__all__ = [
    "ApplicationShell",
    "Workspace",
    "Toolbar",
    "Sidebar",
    "PasswordList",
    "DetailsPane",
]
