from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFormLayout, QPushButton, QFrame, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from ui.viewmodels.entry_details_viewmodel import EntryDetailsViewModel
from ui.resources.styles.layout_constants import Layout
from ui.resources.styles.themes import ThemeManager
from ui.resources.styles.widget_names import WidgetNames
from ui.resources.styles.typography import Typography
from ui.widgets.typography import OverlineLabel, HeadlineLabel, CaptionLabel, TitleLabel, BodyLabel
from ui.widgets.buttons import PillButton, GhostIconButton
from ui.resources.icons import Icons
from ui.services.asset_manager import AssetManager
from ui.app.resources import Resources

class CardSection(QFrame):
    """
    Base card container for Details Pane sections.
    Provides 20px padding, 12px rounded corners, surface background, and subtle border.
    """
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName(WidgetNames.CARD_SECTION)
        colors = ThemeManager.colors()
        self.setStyleSheet(f"""
            QFrame#{WidgetNames.CARD_SECTION} {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {Layout.DETAILS_CARD_RADIUS}px;
            }}
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(
            Layout.DETAILS_CARD_PADDING,
            Layout.DETAILS_CARD_PADDING,
            Layout.DETAILS_CARD_PADDING,
            Layout.DETAILS_CARD_PADDING
        )
        self.layout.setSpacing(Layout.DETAILS_ROW_GAP)
        
        if title:
            self.title_label = OverlineLabel(title.upper())
            self.title_label.setStyleSheet(f"color: {colors.text_secondary}; border: none; background: transparent;")
            self.layout.addWidget(self.title_label)
            
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(Layout.DETAILS_ROW_GAP)
        self.layout.addLayout(self.content_layout)

    def update_view(self, vm: EntryDetailsViewModel):
        pass

class HeaderCard(CardSection):
    """
    Top header card displaying Monogram/Favicon, large Title, website URL, and Favorite star badge.
    """
    def __init__(self, parent=None):
        super().__init__("", parent)
        colors = ThemeManager.colors()
        
        h_layout = QHBoxLayout()
        h_layout.setSpacing(16)
        
        # 48x48 Monogram / Favicon container
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)
        self.icon_label.setAlignment(Qt.AlignCenter)
        
        # Title and URL
        text_vbox = QVBoxLayout()
        text_vbox.setSpacing(2)
        self.title_label = TitleLabel()
        self.title_label.setStyleSheet(f"color: {colors.text_primary}; border: none; background: transparent;")
        self.url_label = CaptionLabel()
        self.url_label.setStyleSheet(f"color: {colors.text_secondary}; border: none; background: transparent;")
        text_vbox.addWidget(self.title_label)
        text_vbox.addWidget(self.url_label)
        
        # Favorite Star
        self.star_btn = GhostIconButton(Icons.STAR, size=32, icon_size=20)
        
        h_layout.addWidget(self.icon_label)
        h_layout.addLayout(text_vbox)
        h_layout.addStretch()
        h_layout.addWidget(self.star_btn)
        
        self.content_layout.addLayout(h_layout)

    def update_view(self, vm: EntryDetailsViewModel):
        self.title_label.setText(vm.title or "Untitled")
        self.url_label.setText(vm.website or "")
        self.url_label.setVisible(bool(vm.website))
        
        icon = AssetManager.instance().get_favicon(vm.id, vm.website, vm.title, size=48)
        self.icon_label.setPixmap(icon.pixmap(48, 48))
        
        is_fav = bool(getattr(vm, "is_favorite", False))
        self.star_btn.setIcon(Resources.icon(Icons.STAR_FILLED if is_fav else Icons.STAR, color_hex="#D97706" if is_fav else None))

class CredentialsCard(CardSection):
    """
    Card containing Username and Password in self-contained field boxes with inline Copy/Reveal pill buttons.
    """
    copy_requested = Signal(str, str) # (field, value)
    
    def __init__(self, parent=None):
        super().__init__("Credentials", parent)
        self.current_username = ""
        self.current_password = ""
        self.password_revealed = False
        
        # Username Box
        self.username_label = BodyLabel()
        self.username_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.copy_user_btn = PillButton("Copy", icon_identifier=Icons.COPY)
        self.copy_user_btn.clicked.connect(lambda: self.copy_requested.emit("Username", self.current_username))
        
        self._add_field_box("USERNAME", self.username_label, [self.copy_user_btn])
        
        # Password Box
        self.password_label = BodyLabel()
        self.password_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.reveal_pass_btn = PillButton("Show", icon_identifier=Icons.EYE)
        self.reveal_pass_btn.clicked.connect(self._toggle_reveal)
        self.copy_pass_btn = PillButton("Copy", icon_identifier=Icons.COPY)
        self.copy_pass_btn.clicked.connect(lambda: self.copy_requested.emit("Password", self.current_password))
        
        self._add_field_box("PASSWORD", self.password_label, [self.reveal_pass_btn, self.copy_pass_btn])

    def _add_field_box(self, caption_text: str, val_widget: QLabel, buttons: list):
        colors = ThemeManager.colors()
        cap_label = CaptionLabel(caption_text)
        cap_label.setStyleSheet(f"color: {colors.text_secondary}; border: none; background: transparent;")
        self.content_layout.addWidget(cap_label)
        
        field_frame = QFrame()
        field_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.input_bg};
                border: 1px solid {colors.border};
                border-radius: 8px;
            }}
        """)
        h_layout = QHBoxLayout(field_frame)
        h_layout.setContentsMargins(12, 10, 12, 10)
        h_layout.setSpacing(8)
        
        val_widget.setStyleSheet(f"color: {colors.text_primary}; border: none; background: transparent;")
        h_layout.addWidget(val_widget)
        h_layout.addStretch()
        for btn in buttons:
            h_layout.addWidget(btn)
            
        self.content_layout.addWidget(field_frame)

    def _toggle_reveal(self):
        self.password_revealed = not self.password_revealed
        if self.password_revealed:
            self.password_label.setText(self.current_password)
            self.reveal_pass_btn.setText("Hide")
            self.reveal_pass_btn.setIcon(Resources.icon(Icons.EYE_OFF))
        else:
            self.password_label.setText("•••••••••••••" if self.current_password else "")
            self.reveal_pass_btn.setText("Show")
            self.reveal_pass_btn.setIcon(Resources.icon(Icons.EYE))

    def update_view(self, vm: EntryDetailsViewModel):
        self.current_username = vm.username or ""
        self.current_password = vm.password or ""
        self.password_revealed = False
        
        self.username_label.setText(self.current_username or "None")
        self.password_label.setText("•••••••••••••" if self.current_password else "None")
        self.reveal_pass_btn.setText("Show")
        self.reveal_pass_btn.setIcon(Resources.icon(Icons.EYE))

class SecurityCard(CardSection):
    """
    Card displaying visual password strength blocks and health indicator.
    """
    def __init__(self, parent=None):
        super().__init__("Security", parent)
        colors = ThemeManager.colors()
        
        # Strength Box
        cap_strength = CaptionLabel("STRENGTH")
        cap_strength.setStyleSheet(f"color: {colors.text_secondary}; border: none; background: transparent;")
        self.content_layout.addWidget(cap_strength)
        
        self.strength_frame = QFrame()
        self.strength_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.input_bg};
                border: 1px solid {colors.border};
                border-radius: 8px;
            }}
        """)
        strength_layout = QHBoxLayout(self.strength_frame)
        strength_layout.setContentsMargins(12, 10, 12, 10)
        strength_layout.setSpacing(6)
        
        self.blocks = []
        for _ in range(5):
            blk = QFrame()
            blk.setFixedHeight(8)
            blk.setStyleSheet(f"background-color: {colors.border}; border-radius: 4px; border: none;")
            strength_layout.addWidget(blk, 1)
            self.blocks.append(blk)
            
        self.strength_text = BodyLabel("Unknown")
        self.strength_text.setStyleSheet(f"color: {colors.text_primary}; border: none; background: transparent; padding-left: 8px;")
        strength_layout.addWidget(self.strength_text)
        self.content_layout.addWidget(self.strength_frame)
        
        # Health Box
        cap_health = CaptionLabel("HEALTH")
        cap_health.setStyleSheet(f"color: {colors.text_secondary}; border: none; background: transparent;")
        self.content_layout.addWidget(cap_health)
        
        self.health_frame = QFrame()
        self.health_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.input_bg};
                border: 1px solid {colors.border};
                border-radius: 8px;
            }}
        """)
        health_layout = QHBoxLayout(self.health_frame)
        health_layout.setContentsMargins(12, 10, 12, 10)
        health_layout.setSpacing(6)
        self.health_icon = QLabel()
        self.health_icon.setPixmap(Resources.icon(Icons.SHIELD_CHECK, color_hex=colors.success).pixmap(18, 18))
        self.health_text = BodyLabel("Safe")
        self.health_text.setStyleSheet(f"color: {colors.success}; border: none; background: transparent;")
        health_layout.addWidget(self.health_icon)
        health_layout.addWidget(self.health_text)
        health_layout.addStretch()
        self.content_layout.addWidget(self.health_frame)

    def update_view(self, vm: EntryDetailsViewModel):
        colors = ThemeManager.colors()
        pw_len = len(vm.password) if vm.password else 0
        if pw_len >= 16:
            strength = "Strong"
            color = colors.success
            active_blocks = 5
        elif pw_len >= 8:
            strength = "Fair"
            color = colors.warning
            active_blocks = 3
        elif pw_len > 0:
            strength = "Weak"
            color = colors.danger
            active_blocks = 1
        else:
            strength = "None"
            color = colors.border
            active_blocks = 0
            
        self.strength_text.setText(strength)
        for i, blk in enumerate(self.blocks):
            if i < active_blocks:
                blk.setStyleSheet(f"background-color: {color}; border-radius: 4px; border: none;")
            else:
                blk.setStyleSheet(f"background-color: {colors.border}; border-radius: 4px; border: none;")
        self.health_text.setText("Safe")

class MetadataCard(CardSection):
    """
    Card displaying Created, Modified, and Category in generously spaced rows.
    """
    def __init__(self, parent=None):
        super().__init__("Metadata", parent)
        self.rows_layout = QVBoxLayout()
        self.rows_layout.setSpacing(12)
        self.content_layout.addLayout(self.rows_layout)
        
        self.created_val = self._add_row("Created")
        self.modified_val = self._add_row("Modified")
        self.category_val = self._add_row("Category")

    def _add_row(self, label_text: str) -> BodyLabel:
        colors = ThemeManager.colors()
        row = QHBoxLayout()
        lbl = CaptionLabel(label_text)
        lbl.setStyleSheet(f"color: {colors.text_secondary}; border: none; background: transparent;")
        val = BodyLabel()
        val.setStyleSheet(f"color: {colors.text_primary}; border: none; background: transparent;")
        row.addWidget(lbl)
        row.addStretch()
        row.addWidget(val)
        self.rows_layout.addLayout(row)
        return val

    def update_view(self, vm: EntryDetailsViewModel):
        self.created_val.setText(getattr(vm, 'created_at', 'Unknown'))
        self.modified_val.setText(getattr(vm, 'updated_at', 'Unknown'))
        self.category_val.setText(getattr(vm, 'category', 'None'))

class NotesCard(CardSection):
    """
    Card displaying secure notes in a clean container.
    """
    def __init__(self, parent=None):
        super().__init__("Secure Notes", parent)
        colors = ThemeManager.colors()
        self.notes_label = BodyLabel()
        self.notes_label.setWordWrap(True)
        self.notes_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.notes_label.setStyleSheet(f"color: {colors.text_primary}; border: none; background: transparent;")
        self.content_layout.addWidget(self.notes_label)

    def update_view(self, vm: EntryDetailsViewModel):
        self.notes_label.setText(vm.notes if vm.notes else "No notes.")
        self.setVisible(bool(vm.notes))

class TotpCard(CardSection):
    """
    Card displaying TOTP code and timer with inline Copy pill button.
    """
    copy_requested = Signal(str, str)
    
    def __init__(self, parent=None):
        super().__init__("Authenticator (TOTP)", parent)
        colors = ThemeManager.colors()
        self.layout_box = QHBoxLayout()
        self.content_layout.addLayout(self.layout_box)
        
        self.code_label = HeadlineLabel("------")
        self.code_label.setStyleSheet(f"color: {colors.text_primary}; border: none; background: transparent;")
        self.time_label = CaptionLabel("30s")
        self.time_label.setStyleSheet(f"color: {colors.text_secondary}; border: none; background: transparent;")
        
        self.copy_btn = PillButton("Copy", icon_identifier=Icons.COPY)
        self.copy_btn.clicked.connect(lambda: self.copy_requested.emit("TOTP Code", self.current_code))
        
        self.layout_box.addWidget(self.code_label)
        self.layout_box.addWidget(self.time_label)
        self.layout_box.addStretch()
        self.layout_box.addWidget(self.copy_btn)
        
        self.current_code = ""
        self.setVisible(False)

    def set_code(self, code: str):
        self.current_code = code
        self.code_label.setText(code[:3] + " " + code[3:] if len(code) == 6 else code)
        self.setVisible(bool(code))
        
    def update_tick(self, remaining: int, progress: float):
        self.time_label.setText(f"{remaining}s")
        
    def update_view(self, vm: EntryDetailsViewModel):
        self.set_code("")

class HistoryCard(CardSection):
    """
    Card displaying password history.
    """
    history_requested = Signal(int)
    
    def __init__(self, parent=None):
        super().__init__("Password History", parent)
        colors = ThemeManager.colors()
        self.load_btn = PillButton("Load History")
        self.load_btn.clicked.connect(self._on_load_clicked)
        self.content_layout.addWidget(self.load_btn)
        
        self.history_layout = QVBoxLayout()
        self.content_layout.addLayout(self.history_layout)
        
        self.current_entry_id = None
        self.is_loaded = False

    def _on_load_clicked(self):
        if self.current_entry_id is not None:
            self.history_requested.emit(self.current_entry_id)
            self.load_btn.setEnabled(False)
            self.load_btn.setText("Loading...")

    def update_view(self, vm: EntryDetailsViewModel):
        if self.current_entry_id != vm.id:
            self.current_entry_id = vm.id
            self.is_loaded = False
            self.load_btn.setEnabled(True)
            self.load_btn.setVisible(True)
            self.load_btn.setText("Load History")
            self._clear_history_layout()

    def set_history_data(self, history: list):
        colors = ThemeManager.colors()
        self.is_loaded = True
        self.load_btn.setVisible(False)
        self._clear_history_layout()
        
        if not history:
            lbl = CaptionLabel("No previous passwords.")
            lbl.setStyleSheet(f"color: {colors.text_secondary}; border: none; background: transparent;")
            self.history_layout.addWidget(lbl)
            return
            
        for record in history:
            label = BodyLabel(f"•••••••• (Changed: {record.created_at})")
            label.setStyleSheet(f"color: {colors.text_primary}; border: none; background: transparent;")
            self.history_layout.addWidget(label)

    def _clear_history_layout(self):
        while self.history_layout.count():
            item = self.history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

# Backward compatibility aliases
HeaderSection = HeaderCard
CredentialsSection = CredentialsCard
MetadataSection = MetadataCard
NotesSection = NotesCard
SecuritySection = SecurityCard
HistorySection = HistoryCard
TotpSection = TotpCard
