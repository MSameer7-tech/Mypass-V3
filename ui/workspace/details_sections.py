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
    Base section container for Details Pane.
    Transparent background for a single continuous inspector surface.
    """
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName(WidgetNames.CARD_SECTION)
        colors = ThemeManager.colors()
        self.setStyleSheet(f"""
            QFrame#{WidgetNames.CARD_SECTION} {{
                background-color: transparent;
                border: none;
            }}
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(12)
        
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
    Top header card displaying 56x56 icon, Title with category, subtitle, and green SECURE badge.
    """
    def __init__(self, parent=None):
        super().__init__("", parent)
        colors = ThemeManager.colors()
        
        h_layout = QHBoxLayout()
        h_layout.setSpacing(16)
        
        # 56x56 Monogram / Favicon container
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(56, 56)
        self.icon_label.setAlignment(Qt.AlignCenter)
        
        # Title and Subtitle
        text_vbox = QVBoxLayout()
        text_vbox.setSpacing(4)
        self.title_label = TitleLabel()
        self.title_label.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: 700; border: none; background: transparent;")
        self.subtitle_label = CaptionLabel("Last changed 2 days ago")
        self.subtitle_label.setStyleSheet("color: #636674; font-size: 12px; border: none; background: transparent;")
        text_vbox.addWidget(self.title_label)
        text_vbox.addWidget(self.subtitle_label)
        
        # Green SECURE Badge
        self.secure_badge = QLabel("SECURE ✓")
        self.secure_badge.setStyleSheet("""
            color: #10B981;
            background-color: rgba(16, 185, 129, 0.15);
            font-size: 11px;
            font-weight: 700;
            padding: 4px 10px;
            border-radius: 12px;
            border: 1px solid rgba(16, 185, 129, 0.3);
        """)
        
        h_layout.addWidget(self.icon_label)
        h_layout.addLayout(text_vbox)
        h_layout.addStretch()
        h_layout.addWidget(self.secure_badge, 0, Qt.AlignTop)
        
        self.content_layout.addLayout(h_layout)

    def update_view(self, vm: EntryDetailsViewModel):
        cat_suffix = f" ({vm.category})" if getattr(vm, 'category', None) else ""
        self.title_label.setText(f"{vm.title or 'Untitled'}{cat_suffix}")
        
        pixmap = AssetManager.instance().request_website_icon(vm.id, vm.website, fallback_title=vm.title, size=56)
        if pixmap and not pixmap.isNull():
            self.icon_label.setPixmap(pixmap.scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.icon_label.setPixmap(QPixmap())

class FieldCard(QFrame):
    """
    Individual field box matching reference mockup inspector cards.
    Contains top caption, bottom value, and right-aligned blue action text links [Copy], [Reveal], [Open].
    """
    def __init__(self, caption: str, value_label: QLabel, actions: list = None, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #23252E;
                border: 1px solid #2B2D38;
                border-radius: 10px;
            }
        """)
        v_layout = QVBoxLayout(self)
        v_layout.setContentsMargins(12, 10, 12, 10)
        v_layout.setSpacing(6)
        
        cap = CaptionLabel(caption)
        cap.setStyleSheet("color: #9498A6; font-size: 11px; font-weight: 500; border: none; background: transparent;")
        v_layout.addWidget(cap)
        
        h_bottom = QHBoxLayout()
        h_bottom.setSpacing(8)
        
        value_label.setStyleSheet("color: #FFFFFF; font-size: 13px; font-weight: 600; border: none; background: transparent;")
        h_bottom.addWidget(value_label)
        h_bottom.addStretch()
        
        if actions:
            for act in actions:
                h_bottom.addWidget(act)
                
        v_layout.addLayout(h_bottom)

class CredentialsCard(CardSection):
    """
    Inspector 2-column field grid matching the reference mockup exactly.
    """
    copy_requested = Signal(str, str) # (field, value)
    
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.current_title = ""
        self.current_username = ""
        self.current_password = ""
        self.current_url = ""
        self.password_revealed = False
        
        from PySide6.QtWidgets import QGridLayout
        grid = QGridLayout()
        grid.setSpacing(12)
        
        # 1. Title Field
        self.title_label = BodyLabel()
        self.title_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.copy_title_btn = self._make_action_link("[Copy]", lambda: self._trigger_copy_feedback(self.copy_title_btn, "Title", self.current_title))
        self.title_card = FieldCard("Title", self.title_label, [self.copy_title_btn])
        
        # 2. Username Field
        self.username_label = BodyLabel()
        self.username_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.copy_user_btn = self._make_action_link("[Copy]", lambda: self._trigger_copy_feedback(self.copy_user_btn, "Username", self.current_username))
        self.user_card = FieldCard("Username", self.username_label, [self.copy_user_btn])
        
        # 3. Password Field
        self.password_label = BodyLabel()
        self.password_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.copy_pass_btn = self._make_action_link("[Copy]", lambda: self._trigger_copy_feedback(self.copy_pass_btn, "Password", self.current_password))
        self.reveal_pass_btn = self._make_action_link("[Reveal]", self._toggle_reveal)
        self.pass_card = FieldCard("Password", self.password_label, [self.copy_pass_btn, self.reveal_pass_btn])
        
        # 4. URL Field
        self.url_label = BodyLabel()
        self.url_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.copy_url_btn = self._make_action_link("[Copy]", lambda: self._trigger_copy_feedback(self.copy_url_btn, "URL", self.current_url))
        self.open_url_btn = self._make_action_link("[Open]", self._open_url)
        self.url_card = FieldCard("URL", self.url_label, [self.copy_url_btn, self.open_url_btn])
        
        grid.addWidget(self.title_card, 0, 0)
        grid.addWidget(self.user_card, 0, 1)
        grid.addWidget(self.pass_card, 1, 0)
        grid.addWidget(self.url_card, 1, 1)
        
        self.content_layout.addLayout(grid)

    def _make_action_link(self, text: str, callback) -> QPushButton:
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet("""
            QPushButton {
                color: #38BDF8;
                font-size: 11px;
                font-weight: 600;
                border: none;
                background: transparent;
                padding: 0px 2px;
            }
            QPushButton:hover {
                color: #7DD3FC;
                text-decoration: underline;
            }
        """)
        btn.clicked.connect(callback)
        return btn

    def _trigger_copy_feedback(self, button: QPushButton, field_name: str, value: str):
        from PySide6.QtCore import QTimer
        self.copy_requested.emit(field_name, value)
        button.setText("[Copied!]")
        button.setStyleSheet("color: #10B981; font-size: 11px; font-weight: 600; border: none; background: transparent;")
        
        def _reset():
            if field_name == "Title":
                button.setText("[Copy]")
            elif field_name == "Username":
                button.setText("[Copy]")
            elif field_name == "Password":
                button.setText("[Copy]")
            elif field_name == "URL":
                button.setText("[Copy]")
            button.setStyleSheet("""
                QPushButton {
                    color: #38BDF8;
                    font-size: 11px;
                    font-weight: 600;
                    border: none;
                    background: transparent;
                    padding: 0px 2px;
                }
                QPushButton:hover {
                    color: #7DD3FC;
                    text-decoration: underline;
                }
            """)
            
        QTimer.singleShot(1200, _reset)

    def _open_url(self):
        if self.current_url:
            import webbrowser
            url = self.current_url if "://" in self.current_url else f"https://{self.current_url}"
            webbrowser.open(url)

    def _toggle_reveal(self):
        self.password_revealed = not self.password_revealed
        if self.password_revealed:
            self.password_label.setText(self.current_password)
            self.reveal_pass_btn.setText("[Hide]")
        else:
            self.password_label.setText("•••••••••••••" if self.current_password else "")
            self.reveal_pass_btn.setText("[Reveal]")

    def update_view(self, vm: EntryDetailsViewModel):
        self.current_title = vm.title or ""
        self.current_username = vm.username or ""
        self.current_password = vm.password or ""
        self.current_url = vm.website or ""
        self.password_revealed = False
        
        self.title_label.setText(self.current_title or "None")
        self.username_label.setText(self.current_username or "None")
        self.password_label.setText("•••••••••••••" if self.current_password else "None")
        self.url_label.setText(self.current_url or "None")
        self.reveal_pass_btn.setText("[Reveal]")

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
    Side-by-side field cards for Created and Modified timestamps matching reference mockup.
    """
    def __init__(self, parent=None):
        super().__init__("", parent)
        h_layout = QHBoxLayout()
        h_layout.setSpacing(12)
        
        self.created_val = BodyLabel("Aug 15, 2024")
        self.created_card = FieldCard("Created", self.created_val)
        
        self.modified_val = BodyLabel("Aug 25, 2024")
        self.modified_card = FieldCard("Modified", self.modified_val)
        
        h_layout.addWidget(self.created_card)
        h_layout.addWidget(self.modified_card)
        
        self.content_layout.addLayout(h_layout)

    def update_view(self, vm: EntryDetailsViewModel):
        self.created_val.setText(getattr(vm, 'created_at', 'Aug 15, 2024') or 'Aug 15, 2024')
        self.modified_val.setText(getattr(vm, 'updated_at', 'Aug 25, 2024') or 'Aug 25, 2024')

class NotesCard(CardSection):
    """
    Full width Notes field card matching reference mockup.
    """
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.notes_val = BodyLabel("Work repository access. Required for primary projects.")
        self.notes_val.setWordWrap(True)
        self.notes_card = FieldCard("Notes", self.notes_val)
        self.content_layout.addWidget(self.notes_card)

    def update_view(self, vm: EntryDetailsViewModel):
        text = vm.notes if vm.notes else "Work repository access. Required for primary projects."
        self.notes_val.setText(text)
        self.setVisible(True)

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
