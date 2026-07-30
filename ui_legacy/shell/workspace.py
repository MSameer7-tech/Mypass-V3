# ui/shell/workspace.py
# Replaces SplitView; coordinates PasswordList, DetailsPane, empty states, and loading states

from typing import Any, Callable, Optional
import customtkinter as ctk

from ui_legacy.components.layout import Container
from .password_list import PasswordList
from .details_pane import DetailsPane

class Workspace(Container):
    """
    Coordinates middle and right panes of the MyPass v2 application shell:
    - Column 0: PasswordList (Finder-style credential cards, fixed/min width 280)
    - Column 1: DetailsPane (Sectioned read-only credential details, expanding weight=1)
    """
    def __init__(
        self,
        master: Any,
        on_add_item: Optional[Callable[[], None]] = None,
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
            variant="transparent",
            corner_radius=0,
            border_width=0,
            **kwargs
        )
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=280)  # Password list column
        self.grid_columnconfigure(1, weight=1)               # Details pane column
        
        # Instantiate child panes
        self.password_list = PasswordList(
            self,
            on_add_clicked=on_add_item
        )
        self.password_list.grid(row=0, column=0, sticky="nsew")
        
        self.details_pane = DetailsPane(
            self,
            on_open_url=on_open_url,
            on_edit_item=on_edit_item,
            on_delete_item=on_delete_item,
            on_copy_password=on_copy_password,
            on_copy_username=on_copy_username,
            on_copy_totp=on_copy_totp,
            on_history_item=on_history_item
        )
        self.details_pane.grid(row=0, column=1, sticky="nsew")
        
    def navigate_selection(self, direction: int) -> None:
        """
        Handle keyboard up (-1) or down (+1) navigation in the password list.
        """
        if hasattr(self.password_list, "move_selection"):
            self.password_list.move_selection(direction)

    def set_items(self, items: list, **kwargs) -> None:
        """Populate the workspace password list with items."""
        self.password_list.set_items(items, **kwargs)
