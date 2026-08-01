import secrets
import string
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QTextEdit, QComboBox, QCheckBox, QPushButton, QLabel, QFrame
)
from PySide6.QtCore import Qt
from ui.dialogs.base_dialog import BaseDialog
from ui.viewmodels.entry_details_viewmodel import EntryDetailsViewModel
from ui.resources.styles.themes import ThemeManager
from ui.widgets.typography import CaptionLabel
from ui.widgets.buttons import PillButton, GhostIconButton
from ui.resources.icons import Icons
from ui.app.resources import Resources

class EntryDialog(BaseDialog):
    """
    Dialog for creating a new vault entry or editing an existing one.
    """
    def __init__(self, entry_vm: EntryDetailsViewModel = None, parent=None):
        title = "Edit Entry" if (entry_vm and entry_vm.id) else "New Password"
        super().__init__(title, parent)
        self.entry_vm = entry_vm
        self.setMinimumWidth(460)
        self._init_form()
        self._populate()

    def _init_form(self):
        colors = ThemeManager.colors()
        
        form_layout = QFormLayout()
        form_layout.setSpacing(14)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Style for input fields
        input_style = f"""
            QLineEdit, QTextEdit, QComboBox {{
                background-color: {colors.input_bg};
                border: 1px solid {colors.border};
                border-radius: 6px;
                padding: 8px 10px;
                color: {colors.text_primary};
                font-size: 14px;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
                border: 1px solid {colors.accent};
            }}
            QCheckBox {{
                color: {colors.text_primary};
                font-size: 14px;
                spacing: 8px;
            }}
        """
        self.setStyleSheet(input_style)
        
        # 1. Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("e.g., GitHub, Gmail, Netflix")
        form_layout.addRow(CaptionLabel("Title"), self.title_input)
        
        # 2. Username
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("e.g., sameer@gmail.com")
        form_layout.addRow(CaptionLabel("Username"), self.username_input)
        
        # 3. Password with Reveal and Generate buttons
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        pass_row = QHBoxLayout()
        pass_row.setSpacing(8)
        pass_row.addWidget(self.password_input, 1)
        
        self.toggle_pass_btn = GhostIconButton(Icons.EYE, size=34, icon_size=18)
        self.toggle_pass_btn.clicked.connect(self._toggle_reveal_password)
        pass_row.addWidget(self.toggle_pass_btn)
        
        self.gen_pass_btn = PillButton("Generate", icon_identifier=Icons.SHIELD)
        self.gen_pass_btn.clicked.connect(self._generate_password)
        pass_row.addWidget(self.gen_pass_btn)
        
        form_layout.addRow(CaptionLabel("Password"), pass_row)
        
        # 4. Website URL
        self.website_input = QLineEdit()
        self.website_input.setPlaceholderText("e.g., https://github.com")
        form_layout.addRow(CaptionLabel("Website"), self.website_input)
        
        # 5. Category
        self.category_input = QComboBox()
        self.category_input.addItems([
            "General", "Work", "Personal", "Finance",
            "Social", "Logins", "Secure Notes", "Credit Cards"
        ])
        form_layout.addRow(CaptionLabel("Category"), self.category_input)
        
        # 6. Favorite
        self.favorite_check = QCheckBox("Mark as Favorite ★")
        form_layout.addRow("", self.favorite_check)
        
        # 7. Secure Notes
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Secure notes, recovery codes, etc.")
        self.notes_input.setMinimumHeight(90)
        form_layout.addRow(CaptionLabel("Notes"), self.notes_input)
        
        self.add_layout(form_layout)

    def _toggle_reveal_password(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_pass_btn.setIcon(Resources.icon(Icons.EYE_OFF))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_pass_btn.setIcon(Resources.icon(Icons.EYE))

    def _generate_password(self):
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        pwd = ''.join(secrets.choice(alphabet) for _ in range(16))
        self.password_input.setText(pwd)
        self.password_input.setEchoMode(QLineEdit.Normal)
        self.toggle_pass_btn.setIcon(Resources.icon(Icons.EYE_OFF))

    def _populate(self):
        if not self.entry_vm:
            self.category_input.setCurrentText("General")
            return
            
        self.title_input.setText(getattr(self.entry_vm, "title", "") or "")
        self.username_input.setText(getattr(self.entry_vm, "username", "") or "")
        self.password_input.setText(getattr(self.entry_vm, "password", "") or "")
        self.website_input.setText(getattr(self.entry_vm, "website", "") or "")
        
        cat = getattr(self.entry_vm, "category", "General") or "General"
        idx = self.category_input.findText(cat, Qt.MatchExactly)
        if idx >= 0:
            self.category_input.setCurrentIndex(idx)
        else:
            self.category_input.setCurrentText("General")
            
        self.favorite_check.setChecked(bool(getattr(self.entry_vm, "favorite", False)))
        self.notes_input.setPlainText(getattr(self.entry_vm, "notes", "") or "")

    def get_values(self):
        return {
            "title": self.title_input.text().strip(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text(),
            "website": self.website_input.text().strip(),
            "category": self.category_input.currentText(),
            "favorite": self.favorite_check.isChecked(),
            "notes": self.notes_input.toPlainText().strip(),
        }
