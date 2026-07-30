# ui/shell/password_list.py
# Finder-style credential list cards with website subtitles and luxurious 20px padding

from typing import Any, Callable, Dict, List, Optional
import customtkinter as ctk

from ui_legacy.components.layout import Container
from ui_legacy.components.label import Label
from ui_legacy.components.button import Button
from ui_legacy.components.badge import Badge
from ui_legacy.design_system import spacing, themes
from services.navigation_service import SelectedEntry

class PasswordCard(ctk.CTkFrame):
    """
    Finder-style item card representing a single saved credential.
    Features:
    - Luxurious 20px padding (spacing.L)
    - Title as primary headline
    - Website/domain as subtitle
    - Timestamp & optional favorite/category badge
    """
    def __init__(
        self,
        master: Any,
        entry: SelectedEntry,
        on_select: Optional[Callable[[SelectedEntry], None]] = None,
        is_selected: bool = False,
        **kwargs
    ):
        super().__init__(
            master=master,
            fg_color="transparent",
            corner_radius=10,
            **kwargs
        )
        self.entry = entry
        self.on_select = on_select
        self.is_selected = is_selected
        
        self.grid_columnconfigure(1, weight=1)
        
        # Icon / Monogram box
        self.icon_box = ctk.CTkFrame(self, width=38, height=38, corner_radius=8)
        self.icon_box.grid(row=0, column=0, rowspan=2, padx=(spacing.L, spacing.M), pady=spacing.M)
        self.icon_box.grid_propagate(False)
        self.icon_box.grid_rowconfigure(0, weight=1)
        self.icon_box.grid_columnconfigure(0, weight=1)
        
        monogram = (entry.title[0].upper() if entry.title else "?")
        self.icon_label = Label(self.icon_box, text=monogram, variant="heading")
        self.icon_label.grid(row=0, column=0)
        
        # Primary Title
        self.title_label = Label(self, text=entry.title, variant="subheading")
        self.title_label.grid(row=0, column=1, sticky="w", pady=(spacing.M, 2))
        
        # Username subtitle (matches mockup: shows user@email below title)
        subtitle = entry.username or entry.url or "No credentials"
        self.domain_label = Label(self, text=subtitle, variant="muted")
        self.domain_label.grid(row=1, column=1, sticky="w", pady=(0, spacing.XS))
        
        # Right column: Favorite icon & Timestamp
        self.right_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.right_frame.grid(row=0, column=2, rowspan=2, sticky="e", padx=(spacing.S, spacing.L), pady=spacing.M)
        
        if entry.favorite:
            self.fav_badge = Label(self.right_frame, text="★", variant="body")
            self.fav_badge.pack(anchor="e")
        
        # Format timestamp
        time_text = self._format_time(entry)
        self.time_label = Label(self.right_frame, text=time_text, variant="tiny")
        self.time_label.pack(anchor="e")
        
        self._set_selected_style(is_selected)
        
        # Bind click events across all children
        self._bind_click_recursive(self)

    def _bind_click_recursive(self, widget: Any) -> None:
        widget.bind("<Button-1>", lambda e: self._handle_click())
        widget.bind("<Enter>", lambda e: self._on_hover(True))
        widget.bind("<Leave>", lambda e: self._on_hover(False))
        for child in widget.winfo_children():
            self._bind_click_recursive(child)

    def set_selected(self, selected: bool) -> None:
        self.is_selected = selected
        self._set_selected_style(selected)

    def _set_selected_style(self, selected: bool) -> None:
        theme = themes.DarkTheme
        if selected:
            self.configure(fg_color=theme.surface_elevated, border_color=theme.accent, border_width=1)
            self.icon_box.configure(fg_color=theme.accent)
            self.icon_label.configure(text_color="#FFFFFF")
        else:
            self.configure(fg_color="transparent", border_width=0)
            self.icon_box.configure(fg_color=theme.surface)
            self.icon_label.configure(text_color=theme.text_primary)

    def _on_hover(self, hovering: bool) -> None:
        if not self.is_selected:
            theme = themes.DarkTheme
            self.configure(fg_color=theme.surface if hovering else "transparent")

    def _handle_click(self) -> None:
        if self.on_select:
            self.on_select(self.entry)

    @staticmethod
    def _format_time(entry: SelectedEntry) -> str:
        if not entry.data or not hasattr(entry.data, "updated_at"):
            return ""
        raw = str(entry.data.updated_at or "")
        if not raw:
            return ""
        try:
            from datetime import datetime, timezone
            dt = datetime.fromisoformat(raw)
            now = datetime.now(timezone.utc)
            if dt.tzinfo is None:
                from datetime import timezone as tz
                dt = dt.replace(tzinfo=tz.utc)
            delta = now - dt
            mins = int(delta.total_seconds() / 60)
            if mins < 1:
                return "Just now"
            elif mins < 60:
                return f"{mins} min ago"
            elif mins < 1440:
                hours = mins // 60
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            else:
                days = mins // 1440
                return f"{days} day{'s' if days > 1 else ''} ago"
        except Exception:
            return raw[:10] if len(raw) > 10 else raw


class PasswordList(Container):
    """
    Scrollable Finder-style credential list view.
    Manages active card selection and keyboard ↑/↓ arrow navigation.
    """
    def __init__(
        self,
        master: Any,
        on_item_selected: Optional[Callable[[SelectedEntry], None]] = None,
        on_add_clicked: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        super().__init__(
            master=master,
            variant="surface",
            corner_radius=0,
            border_width=0,
            **kwargs
        )
        self.on_item_selected = on_item_selected
        self.on_add_clicked = on_add_clicked
        self._items: List[SelectedEntry] = []
        self._cards: Dict[int, PasswordCard] = {}
        self._selected_index: int = -1
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Header bar
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=spacing.M, pady=(spacing.S, 0))
        self.header_frame.grid_columnconfigure(0, weight=1)
        
        self.count_label = Label(self.header_frame, text="0 items", variant="tiny")
        self.count_label.grid(row=0, column=0, sticky="w")
        
        self.sort_label = Label(self.header_frame, text="Sorted by Title", variant="tiny")
        self.sort_label.grid(row=0, column=1, sticky="e")
        
        # Scrollable list area
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Empty State frame
        self.empty_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.empty_icon = Label(self.empty_frame, text="🔍", variant="display")
        self.empty_icon.pack(pady=(spacing.XL, spacing.M))
        self.empty_title = Label(self.empty_frame, text="No Passwords Found", variant="subheading")
        self.empty_title.pack(pady=spacing.XS)
        self.empty_subtitle = Label(
            self.empty_frame,
            text="Add a new password or adjust your search filter.",
            variant="muted"
        )
        self.empty_subtitle.pack(pady=(0, spacing.L))
        self.empty_button = Button(
            self.empty_frame,
            text="+ Add First Password",
            variant="primary",
            command=self._handle_add_clicked
        )
        self.empty_button.pack()

    def set_items(self, items: List[SelectedEntry], select_first: bool = False) -> None:
        """Populate list with password entries."""
        self._items = items.copy()
        self._cards.clear()
        
        # Clear existing cards
        for child in self.scroll_frame.winfo_children():
            if child != self.empty_frame:
                child.destroy()
                
        self.count_label.configure(text=f"{len(items)} item{'s' if len(items) != 1 else ''}")
        
        if not items:
            self.empty_frame.pack(expand=True, fill="both", pady=spacing.XL)
            self._selected_index = -1
            return
        else:
            self.empty_frame.pack_forget()

        for idx, entry in enumerate(items):
            card = PasswordCard(
                self.scroll_frame,
                entry=entry,
                on_select=self._handle_item_click
            )
            card.pack(fill="x", padx=spacing.S, pady=3)
            self._cards[entry.id] = card
            
        if select_first and items:
            self._select_index(0)

    def select_by_id(self, entry_id: int) -> None:
        """Highlight card with matching entry_id."""
        for idx, item in enumerate(self._items):
            if item.id == entry_id:
                self._select_index(idx)
                break

    def move_selection(self, direction: int) -> None:
        """Keyboard Up (-1) or Down (+1) navigation."""
        if not self._items:
            return
        new_idx = max(0, min(len(self._items) - 1, self._selected_index + direction))
        if new_idx != self._selected_index:
            self._select_index(new_idx)

    def _select_index(self, idx: int) -> None:
        self._selected_index = idx
        selected_entry = self._items[idx]
        for item_id, card in self._cards.items():
            card.set_selected(item_id == selected_entry.id)
            
        if self.on_item_selected:
            self.on_item_selected(selected_entry)

    def _handle_item_click(self, entry: SelectedEntry) -> None:
        self.select_by_id(entry.id)

    def _handle_add_clicked(self) -> None:
        if self.on_add_clicked:
            self.on_add_clicked()
