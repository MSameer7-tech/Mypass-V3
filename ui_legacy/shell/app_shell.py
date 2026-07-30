# ui/shell/app_shell.py
# Root application shell for MyPass v2 (Toolbar + Sidebar + Workspace)

from typing import Any, Callable, Optional
import customtkinter as ctk

from ui_legacy.components.layout import Container
from ui_legacy.design_system import spacing
from .toolbar import Toolbar
from .sidebar import Sidebar
from .workspace import Workspace

class ApplicationShell(Container):
    """
    Main 3-pane desktop workspace shell for MyPass v2.
    Row 0: Toolbar (Top across full width)
    Row 1:
      Column 0: Navigation Sidebar (220px fixed/minsize)
      Column 1: Workspace (Password List + Details Pane, flexible width)
    """
    def __init__(
        self,
        master: Any,
        on_add_item: Optional[Callable[[], None]] = None,
        on_lock: Optional[Callable[[], None]] = None,
        on_settings: Optional[Callable[[], None]] = None,
        on_open_url: Optional[Callable[[str], None]] = None,
        on_edit_item: Optional[Callable[[int], None]] = None,
        on_delete_item: Optional[Callable[[int], None]] = None,
        on_copy_password: Optional[Callable[[str], None]] = None,
        on_copy_username: Optional[Callable[[str], None]] = None,
        on_copy_totp: Optional[Callable[[str], None]] = None,
        on_history_item: Optional[Callable[[int], None]] = None,
        **kwargs
    ):
        super().__init__(
            master=master,
            variant="surface",
            corner_radius=0,
            border_width=0,
            **kwargs
        )
        
        self.on_add_item = on_add_item
        self.on_lock = on_lock
        self.on_settings = on_settings
        self.on_open_url = on_open_url
        self.on_edit_item = on_edit_item
        self.on_delete_item = on_delete_item
        self.on_copy_password = on_copy_password
        self.on_copy_username = on_copy_username
        self.on_copy_totp = on_copy_totp
        self.on_history_item = on_history_item

        # Grid configuration for main shell
        self.grid_rowconfigure(0, weight=0, minsize=52)   # Toolbar row
        self.grid_rowconfigure(1, weight=1)               # Content row (Sidebar + Workspace)
        self.grid_columnconfigure(0, weight=0, minsize=220)  # Sidebar column
        self.grid_columnconfigure(1, weight=1)            # Workspace column (List + Details)
        
        # Instantiate Shell Children
        self.toolbar = Toolbar(
            self,
            on_add=self._handle_add,
            on_lock=self._handle_lock,
            on_settings=self._handle_settings
        )
        self.toolbar.grid(row=0, column=0, columnspan=2, sticky="nsew")
        
        self.sidebar = Sidebar(
            self,
            on_filter_selected=self._handle_filter
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew")
        
        self.workspace = Workspace(
            self,
            on_add_item=self._handle_add,
            on_open_url=self._handle_open_url,
            on_edit_item=self._handle_edit_item,
            on_delete_item=self._handle_delete_item,
            on_copy_password=self._handle_copy_password,
            on_copy_username=self._handle_copy_username,
            on_copy_totp=self._handle_copy_totp,
            on_history_item=self._handle_history_item
        )
        self.workspace.grid(row=1, column=1, sticky="nsew")
        
        # Setup Global Keyboard Shortcuts
        self._setup_keyboard_shortcuts()
        
    def _setup_keyboard_shortcuts(self) -> None:
        try:
            top = self.winfo_toplevel()
            # Search focus: Cmd+F (Mac) or Ctrl+F (Win/Linux)
            top.bind("<Command-f>", lambda e: self.toolbar.focus_search())
            top.bind("<Control-f>", lambda e: self.toolbar.focus_search())
            # Add Item: Cmd+N or Ctrl+N
            top.bind("<Command-n>", lambda e: self._handle_add())
            top.bind("<Control-n>", lambda e: self._handle_add())
            # Lock Vault: Cmd+L or Ctrl+L
            top.bind("<Command-l>", lambda e: self._handle_lock())
            top.bind("<Control-l>", lambda e: self._handle_lock())
            # List selection arrows: Up/Down
            top.bind("<Up>", lambda e: self.workspace.navigate_selection(-1))
            top.bind("<Down>", lambda e: self.workspace.navigate_selection(1))
        except Exception:
            pass

    def _handle_add(self) -> None:
        if self.on_add_item:
            self.on_add_item()

    def _handle_lock(self) -> None:
        if self.on_lock:
            self.on_lock()

    def _handle_settings(self) -> None:
        if self.on_settings:
            self.on_settings()

    def _handle_filter(self, filter_name: str) -> None:
        pass  # Handled via NavigationService in Sidebar/Workspace

    def _handle_open_url(self, url: str) -> None:
        if self.on_open_url:
            self.on_open_url(url)

    def _handle_edit_item(self, item_id: int) -> None:
        if self.on_edit_item:
            self.on_edit_item(item_id)

    def _handle_delete_item(self, item_id: int) -> None:
        if self.on_delete_item:
            self.on_delete_item(item_id)

    def _handle_copy_password(self, password: str) -> None:
        if self.on_copy_password:
            self.on_copy_password(password)

    def _handle_copy_username(self, username: str) -> None:
        if self.on_copy_username:
            self.on_copy_username(username)

    def _handle_copy_totp(self, totp: str) -> None:
        if self.on_copy_totp:
            self.on_copy_totp(totp)

    def _handle_history_item(self, item_id: int) -> None:
        if self.on_history_item:
            self.on_history_item(item_id)
