# ui/shell/toolbar.py
# Premium simplified toolbar for MyPass v2

from typing import Any, Callable, Optional
import customtkinter as ctk

from ui_legacy.components.layout import Container
from ui_legacy.components.button import Button
from ui_legacy.components.inputs import SearchField
from ui_legacy.components.label import Label
from ui_legacy.design_system import spacing, themes

class Toolbar(Container):
    """
    Top-level application toolbar for MyPass v2.
    Features:
    - Left: Subtle app logo & title ('MyPass')
    - Center (flexible width): Wide Spotlight-style Search bar
    - Right: '+ Add Item' button, Lock icon ('🔒'), Settings gear icon ('⚙')
    """
    def __init__(
        self,
        master: Any,
        on_add: Optional[Callable[[], None]] = None,
        on_lock: Optional[Callable[[], None]] = None,
        on_settings: Optional[Callable[[], None]] = None,
        on_search_change: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(
            master=master,
            variant="surface",
            corner_radius=0,
            border_width=0,
            **kwargs
        )
        
        self.on_add = on_add
        self.on_lock = on_lock
        self.on_settings = on_settings
        self.on_search_change = on_search_change

        # Grid setup: 0=Logo, 1=Search(weight=1), 2=Add, 3=Lock, 4=Settings
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=140)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_columnconfigure(3, weight=0)
        self.grid_columnconfigure(4, weight=0)
        
        # 1. Subtle Logo
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, sticky="w", padx=(spacing.M, spacing.M))
        
        self.logo_label = Label(
            self.logo_frame,
            text="🛡 MyPass",
            variant="heading"
        )
        self.logo_label.pack(side="left")

        # 2. Wide Spotlight-style Search Field
        self.search_field = SearchField(
            self,
            placeholder="Search items, domains, or tags (⌘F)...",
            on_search=self._handle_search
        )
        self.search_field.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(spacing.L, spacing.XL),
            pady=spacing.S
        )

        # 3. '+ Add Item' Button
        self.add_button = Button(
            self,
            text="+ Add Item",
            variant="primary",
            command=self._handle_add
        )
        self.add_button.grid(
            row=0,
            column=2,
            sticky="e",
            padx=(0, spacing.S),
            pady=spacing.S
        )

        # 4. Lock Button (🔒 only)
        self.lock_button = Button(
            self,
            text="🔒",
            variant="ghost",
            width=36,
            command=self._handle_lock
        )
        self.lock_button.grid(
            row=0,
            column=3,
            sticky="e",
            padx=(0, spacing.XS),
            pady=spacing.S
        )

        # 5. Settings Gear Button (⚙ only)
        self.settings_button = Button(
            self,
            text="⚙",
            variant="ghost",
            width=36,
            command=self._handle_settings
        )
        self.settings_button.grid(
            row=0,
            column=4,
            sticky="e",
            padx=(0, spacing.M),
            pady=spacing.S
        )

    def focus_search(self) -> None:
        """Focus the search entry input box."""
        try:
            self.search_field.entry.focus_set()
        except Exception:
            pass

    def _handle_search(self, query: str) -> None:
        if self.on_search_change:
            self.on_search_change(query)

    def _handle_add(self) -> None:
        if self.on_add:
            self.on_add()

    def _handle_lock(self) -> None:
        if self.on_lock:
            self.on_lock()

    def _handle_settings(self) -> None:
        if self.on_settings:
            self.on_settings()
