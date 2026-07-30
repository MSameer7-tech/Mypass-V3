# ui/shell/details_pane.py
# Sectioned read-only credential details pane with card-based grid layout
# Matches the 1Password × Raycast × Apple design mockup

from typing import Any, Callable, Optional
import customtkinter as ctk

from ui_legacy.components.layout import Container
from ui_legacy.components.label import Label
from ui_legacy.components.button import Button
from ui_legacy.components.badge import Badge
from ui_legacy.design_system import spacing, themes
from services.navigation_service import SelectedEntry


class DetailCard(ctk.CTkFrame):
    """
    A single info card cell in the details grid.
    Shows a muted label on top and the value below, with an optional action link.
    """
    def __init__(
        self,
        master: Any,
        label_text: str,
        value_text: str,
        action_text: Optional[str] = None,
        on_action: Optional[Callable[[], None]] = None,
        is_password: bool = False,
        **kwargs
    ):
        theme = themes.get_theme()
        super().__init__(
            master=master,
            fg_color=theme.surface,
            corner_radius=10,
            border_width=1,
            border_color=theme.border,
            **kwargs
        )
        self.grid_columnconfigure(0, weight=1)
        
        # Label (muted, small)
        lbl = Label(self, text=label_text, variant="muted")
        lbl.grid(row=0, column=0, sticky="w", padx=spacing.M, pady=(spacing.M, 2))
        
        # Value row (value + optional action)
        val_frame = ctk.CTkFrame(self, fg_color="transparent")
        val_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=spacing.M, pady=(0, spacing.M))
        val_frame.grid_columnconfigure(0, weight=1)
        
        display_text = value_text or "—"
        val_lbl = Label(val_frame, text=display_text, variant="body")
        val_lbl.grid(row=0, column=0, sticky="w")
        
        if action_text and on_action:
            action_btn = ctk.CTkButton(
                val_frame,
                text=action_text,
                fg_color="transparent",
                hover_color=theme.surface_elevated,
                text_color=theme.accent,
                font=("Inter", 12),
                width=0,
                height=24,
                corner_radius=6,
                command=on_action,
                cursor="hand2"
            )
            action_btn.grid(row=0, column=1, sticky="e", padx=(spacing.S, 0))


class DetailsPane(Container):
    """
    Right-hand credential Details Pane for MyPass v2.
    Card-based grid layout matching the 1Password × Raycast design mockup:
    - Header: Icon + Title + Category badge + Security badge
    - 2-column card grid for fields
    - Full-width cards for notes
    - Action bar with Edit/Delete at top
    """
    def __init__(
        self,
        master: Any,
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
            variant="surface_elevated",
            corner_radius=0,
            border_width=0,
            **kwargs
        )
        self.on_open_url = on_open_url
        self.on_edit_item = on_edit_item
        self.on_delete_item = on_delete_item
        self.on_copy_password = on_copy_password
        self.on_copy_username = on_copy_username
        self.on_copy_totp = on_copy_totp
        self.on_history_item = on_history_item
        
        self.current_entry: Optional[SelectedEntry] = None
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # --- Empty State (when nothing selected) ---
        self.empty_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.empty_icon = Label(self.empty_frame, text="🔒", variant="display")
        self.empty_icon.pack(pady=(spacing.XL, spacing.M))
        self.empty_title = Label(self.empty_frame, text="No Item Selected", variant="subheading")
        self.empty_title.pack(pady=spacing.XS)
        self.empty_subtitle = Label(
            self.empty_frame,
            text="Select a password from the list to view its details.",
            variant="muted"
        )
        self.empty_subtitle.pack()
        self.empty_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", pady=120)
        
        # --- Scrollable Content Area (hidden until entry selected) ---
        self.content_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content_scroll.grid_columnconfigure(0, weight=1)
        self.content_scroll.grid_columnconfigure(1, weight=1)

    def display_entry(self, entry: Optional[SelectedEntry]) -> None:
        """Render details for the selected credential in card-based grid layout."""
        self.current_entry = entry
        
        if entry is None:
            self.content_scroll.grid_remove()
            self.empty_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", pady=120)
            return
            
        self.empty_frame.grid_remove()
        self.content_scroll.grid(row=0, column=0, rowspan=2, sticky="nsew")
        
        # Clear previous content
        for child in self.content_scroll.winfo_children():
            child.destroy()
        
        theme = themes.get_theme()
        row = 0
        
        # ===== HEADER ROW: Icon + Title + Badges =====
        header = ctk.CTkFrame(self.content_scroll, fg_color="transparent")
        header.grid(row=row, column=0, columnspan=2, sticky="ew", padx=spacing.L, pady=(spacing.L, spacing.M))
        header.grid_columnconfigure(1, weight=1)
        
        # Monogram icon
        monogram = (entry.title[0].upper() if entry.title else "?")
        icon_box = ctk.CTkFrame(header, width=48, height=48, corner_radius=12, fg_color=theme.accent)
        icon_box.grid(row=0, column=0, rowspan=2, padx=(0, spacing.M))
        icon_box.grid_propagate(False)
        icon_box.grid_rowconfigure(0, weight=1)
        icon_box.grid_columnconfigure(0, weight=1)
        icon_lbl = ctk.CTkLabel(icon_box, text=monogram, font=("Inter", 20, "bold"), text_color="#FFFFFF")
        icon_lbl.grid(row=0, column=0)
        
        # Title + Category
        title_text = f"{entry.title}"
        if entry.category:
            title_text = f"{entry.title} ({entry.category})"
        title_lbl = Label(header, text=title_text, variant="heading")
        title_lbl.grid(row=0, column=1, sticky="w", pady=(0, 2))
        
        # Security badge row
        badge_frame = ctk.CTkFrame(header, fg_color="transparent")
        badge_frame.grid(row=1, column=1, sticky="w")
        
        self.security_badge = Badge(badge_frame, text="Strong", variant="success")
        self.security_badge.pack(side="left", padx=(0, spacing.S))
        self._update_security_badge(entry)
        
        # Action buttons (top right)
        action_frame = ctk.CTkFrame(header, fg_color="transparent")
        action_frame.grid(row=0, column=2, rowspan=2, sticky="ne")
        
        edit_btn = Button(action_frame, text="Edit", variant="secondary", size="small", command=self._handle_edit)
        edit_btn.pack(side="left", padx=(0, spacing.XS))
        
        delete_btn = Button(action_frame, text="Delete", variant="danger", size="small", command=self._handle_delete)
        delete_btn.pack(side="left")
        
        row += 1
        
        # ===== CARD GRID: 2-column layout =====
        # Row 1: Title | Username
        DetailCard(
            self.content_scroll,
            label_text="Title",
            value_text=entry.title,
        ).grid(row=row, column=0, sticky="nsew", padx=(spacing.L, spacing.XS), pady=spacing.XS)
        
        DetailCard(
            self.content_scroll,
            label_text="Username",
            value_text=entry.username or "—",
            action_text="[Copy]" if entry.username else None,
            on_action=lambda: self._handle_copy_username(entry.username)
        ).grid(row=row, column=1, sticky="nsew", padx=(spacing.XS, spacing.L), pady=spacing.XS)
        row += 1
        
        # Row 2: Password | URL
        raw_pwd = self._get_raw_password(entry)
        DetailCard(
            self.content_scroll,
            label_text="Password",
            value_text="••••••••••••",
            is_password=True,
            action_text="[Copy]",
            on_action=lambda: self._handle_copy_password(raw_pwd)
        ).grid(row=row, column=0, sticky="nsew", padx=(spacing.L, spacing.XS), pady=spacing.XS)
        
        url_display = entry.url or "—"
        DetailCard(
            self.content_scroll,
            label_text="URL",
            value_text=url_display,
            action_text="[Open]" if entry.url else None,
            on_action=lambda: self._handle_open_url(entry.url) if entry.url else None
        ).grid(row=row, column=1, sticky="nsew", padx=(spacing.XS, spacing.L), pady=spacing.XS)
        row += 1
        
        # Row 3: Password History (full width)
        if self.on_history_item:
            DetailCard(
                self.content_scroll,
                label_text="Password History",
                value_text="View and restore past passwords",
                action_text="[History]",
                on_action=lambda: self.on_history_item(entry.id)
            ).grid(row=row, column=0, columnspan=2, sticky="nsew", padx=spacing.L, pady=spacing.XS)
            row += 1
        
        # Row 4: Notes (full width)
        notes = "No notes added."
        if entry.data and hasattr(entry.data, "notes") and entry.data.notes:
            notes = entry.data.notes
        DetailCard(
            self.content_scroll,
            label_text="Notes",
            value_text=notes,
        ).grid(row=row, column=0, columnspan=2, sticky="nsew", padx=spacing.L, pady=spacing.XS)
        row += 1
        
        # Row 5: Created | Modified
        created_str = "—"
        updated_str = "—"
        if entry.data:
            if hasattr(entry.data, "created_at") and entry.data.created_at:
                raw = str(entry.data.created_at)
                # Try to make it human-readable
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(raw)
                    created_str = dt.strftime("%b %d, %Y")
                except Exception:
                    created_str = raw[:10] if len(raw) > 10 else raw
            if hasattr(entry.data, "updated_at") and entry.data.updated_at:
                raw = str(entry.data.updated_at)
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(raw)
                    updated_str = dt.strftime("%b %d, %Y")
                except Exception:
                    updated_str = raw[:10] if len(raw) > 10 else raw
        
        DetailCard(
            self.content_scroll,
            label_text="Created",
            value_text=created_str,
        ).grid(row=row, column=0, sticky="nsew", padx=(spacing.L, spacing.XS), pady=(spacing.XS, spacing.L))
        
        DetailCard(
            self.content_scroll,
            label_text="Modified",
            value_text=updated_str,
        ).grid(row=row, column=1, sticky="nsew", padx=(spacing.XS, spacing.L), pady=(spacing.XS, spacing.L))

    def _update_security_badge(self, entry: SelectedEntry) -> None:
        raw_pwd = self._get_raw_password(entry)
        length = len(raw_pwd)
        if hasattr(entry.data, "is_breached") and getattr(entry.data, "is_breached", False):
            self.security_badge.set_text("BREACHED ⚠")
            self.security_badge.set_variant("danger")
        elif length >= 16:
            self.security_badge.set_text("SECURE ✅")
            self.security_badge.set_variant("success")
        elif length >= 12:
            self.security_badge.set_text("STRONG ✅")
            self.security_badge.set_variant("success")
        elif length >= 8:
            self.security_badge.set_text("FAIR ⚠")
            self.security_badge.set_variant("warning")
        else:
            self.security_badge.set_text("WEAK ⛔")
            self.security_badge.set_variant("danger")

    def _get_raw_password(self, entry: SelectedEntry) -> str:
        if entry.data and hasattr(entry.data, "password"):
            return str(entry.data.password or "")
        return ""

    def _handle_edit(self) -> None:
        if self.current_entry and self.on_edit_item:
            self.on_edit_item(self.current_entry.id)

    def _handle_delete(self) -> None:
        if self.current_entry and self.on_delete_item:
            self.on_delete_item(self.current_entry.id)

    def _handle_open_url(self, url: str) -> None:
        if url and self.on_open_url:
            self.on_open_url(url)

    def _handle_copy_username(self, username: str) -> None:
        if username and self.on_copy_username:
            self.on_copy_username(username)

    def _handle_copy_password(self, password: str) -> None:
        if password and self.on_copy_password:
            self.on_copy_password(password)
