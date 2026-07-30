# ui/shell/sidebar.py
# Navigation sidebar with category counters and bottom user profile card

from typing import Any, Callable, Dict, Optional
import customtkinter as ctk

from ui_legacy.components.layout import Container
from ui_legacy.components.button import Button
from ui_legacy.components.label import Label
from ui_legacy.components.badge import Badge
from ui_legacy.design_system import spacing, themes

class SidebarItem(ctk.CTkFrame):
    """
    Individual clickable sidebar item with icon, label, and optional counter badge.
    """
    def __init__(
        self,
        master: Any,
        text: str,
        icon: str = "•",
        filter_id: str = "",
        on_click: Optional[Callable[[str], None]] = None,
        is_active: bool = False,
        **kwargs
    ):
        super().__init__(
            master=master,
            fg_color="transparent",
            corner_radius=6,
            height=34,
            **kwargs
        )
        self.filter_id = filter_id
        self.on_click = on_click
        self.is_active = is_active
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Icon
        self.icon_label = Label(self, text=icon, variant="body")
        self.icon_label.grid(row=0, column=0, padx=(spacing.S, spacing.XS))
        
        # Text
        self.text_label = Label(self, text=text, variant="body")
        self.text_label.grid(row=0, column=1, sticky="w")
        
        # Optional counter badge
        self.counter_label = Label(self, text="", variant="tiny")
        self.counter_label.grid(row=0, column=2, padx=(0, spacing.S))
        self.counter_label.grid_remove()  # Hide initially
        
        self._set_active_style(is_active)
        
        # Bind click events
        for widget in [self, self.icon_label, self.text_label, self.counter_label]:
            widget.bind("<Button-1>", lambda e: self._handle_click())
            widget.bind("<Enter>", lambda e: self._on_hover(True))
            widget.bind("<Leave>", lambda e: self._on_hover(False))

    def set_counter(self, count: int) -> None:
        if count > 0:
            self.counter_label.configure(text=str(count))
            self.counter_label.grid()
        else:
            self.counter_label.grid_remove()

    def set_active(self, active: bool) -> None:
        self.is_active = active
        self._set_active_style(active)

    def _set_active_style(self, active: bool) -> None:
        theme = themes.DarkTheme
        if active:
            self.configure(fg_color=theme.surface_elevated)
            self.text_label.configure(text_color=theme.text_primary, font=ctk.CTkFont(size=13, weight="bold"))
        else:
            self.configure(fg_color="transparent")
            self.text_label.configure(text_color=theme.text_secondary, font=ctk.CTkFont(size=13))

    def _on_hover(self, hovering: bool) -> None:
        if not self.is_active:
            theme = themes.DarkTheme
            self.configure(fg_color=theme.surface if hovering else "transparent")

    def _handle_click(self) -> None:
        if self.on_click:
            self.on_click(self.filter_id)


class Sidebar(Container):
    """
    Left-hand navigation sidebar for MyPass v2.
    - Top: Navigation grouped by Vault, Categories (with counters), System
    - Bottom: Slack/Linear style User Profile card
    """
    def __init__(
        self,
        master: Any,
        on_filter_selected: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(
            master=master,
            variant="surface",
            corner_radius=0,
            border_width=0,
            width=240,
            **kwargs
        )
        
        self.on_filter_selected = on_filter_selected
        self._items: Dict[str, SidebarItem] = {}
        self._active_filter: str = "all"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Navigation expands
        self.grid_rowconfigure(1, weight=0)  # Profile card at bottom
        
        # --- 1. Top Navigation Area ---
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_frame.grid(row=0, column=0, sticky="nsew", padx=spacing.S, pady=spacing.M)
        self.nav_frame.grid_columnconfigure(0, weight=1)
        
        # Group 1: Vault
        self._add_section_header(self.nav_frame, "VAULT")
        self._add_item(self.nav_frame, "all", "All Items", "🔑", is_active=True)
        self._add_item(self.nav_frame, "favorites", "Favorites", "★")

        # Group 2: Categories
        self._add_section_header(self.nav_frame, "CATEGORIES", pady=(spacing.L, spacing.XS))
        self._add_item(self.nav_frame, "Personal", "Personal", "🏠")
        self._add_item(self.nav_frame, "Work", "Work", "💼")
        self._add_item(self.nav_frame, "Banking", "Banking", "💳")

        # Group 3: System
        self._add_section_header(self.nav_frame, "SYSTEM", pady=(spacing.L, spacing.XS))
        self._add_item(self.nav_frame, "recent", "Recently Used", "⏱")
        self._add_item(self.nav_frame, "trash", "Trash", "🗑")

        # --- 2. Bottom User Profile Card (Slack/Linear style) ---
        self.profile_card = Container(
            self,
            variant="elevated",
            corner_radius=8,
            border_width=1
        )
        self.profile_card.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=spacing.S,
            pady=(0, spacing.M)
        )
        self.profile_card.grid_columnconfigure(1, weight=1)
        
        # Avatar icon
        self.avatar_label = Label(self.profile_card, text="👤", variant="heading")
        self.avatar_label.grid(row=0, column=0, rowspan=2, padx=(spacing.S, spacing.XS), pady=spacing.S)
        
        # Profile details
        self.profile_name = Label(self.profile_card, text="MyPass Master", variant="body")
        self.profile_name.grid(row=0, column=1, sticky="w", pady=(spacing.XS, 0))
        
        self.profile_status = Label(self.profile_card, text="Vault Unlocked • Active", variant="tiny")
        self.profile_status.grid(row=1, column=1, sticky="w", pady=(0, spacing.XS))

    def _add_section_header(self, parent: Any, title: str, pady: Any = (spacing.XS, spacing.XS)) -> None:
        label = Label(parent, text=title, variant="tiny")
        label.pack(anchor="w", padx=spacing.S, pady=pady)

    def _add_item(self, parent: Any, filter_id: str, text: str, icon: str, is_active: bool = False) -> None:
        item = SidebarItem(
            parent,
            text=text,
            icon=icon,
            filter_id=filter_id,
            is_active=is_active,
            on_click=self.set_active_filter
        )
        item.pack(fill="x", pady=2)
        self._items[filter_id] = item

    def set_active_filter(self, filter_id: str) -> None:
        if self._active_filter == filter_id:
            return
        self._active_filter = filter_id
        for fid, item in self._items.items():
            item.set_active(fid == filter_id)
            
        if self.on_filter_selected:
            self.on_filter_selected(filter_id)

    def update_counters(self, counts: Dict[str, int]) -> None:
        """Update category counter badges in the sidebar."""
        for fid, count in counts.items():
            if fid in self._items:
                self._items[fid].set_counter(count)
