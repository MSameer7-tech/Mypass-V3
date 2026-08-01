from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from PySide6.QtCore import Qt

from ui.widgets.base import BaseFrame
from ui.widgets.inputs import PasswordField, TextField
from ui.widgets.buttons import PrimaryButton
from ui.widgets.typography import HeadlineLabel, BodyLabel

class CreateVaultView(BaseFrame):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.setObjectName("CreateVaultView")
        self.viewmodel = viewmodel
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(24)
        
        container = QWidget()
        container.setFixedWidth(420)
        c_layout = QVBoxLayout(container)
        c_layout.setSpacing(16)
        
        self.title = HeadlineLabel("Create Your Vault")
        self.title.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(self.title)
        
        self.subtitle = BodyLabel("Set a strong master password. This is the only way to unlock your vault.")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setWordWrap(True)
        c_layout.addWidget(self.subtitle)
        
        self.password_input = PasswordField("Master Password")
        c_layout.addWidget(self.password_input)
        
        self.confirm_input = PasswordField("Confirm Master Password")
        c_layout.addWidget(self.confirm_input)
        
        self.hint_input = TextField("Password Hint (Optional)")
        c_layout.addWidget(self.hint_input)
        
        # Error Label
        self.error_label = BodyLabel("")
        self.error_label.setStyleSheet("color: var(--color-danger);")
        self.error_label.hide()
        c_layout.addWidget(self.error_label)
        
        self.create_btn = PrimaryButton("Create Vault")
        c_layout.addWidget(self.create_btn)
        
        layout.addWidget(container)
        
        self._connect_signals()
        
    def _connect_signals(self):
        self.create_btn.clicked.connect(self._on_submit)
        self.password_input.returnPressed.connect(lambda: self.confirm_input.setFocus())
        self.confirm_input.returnPressed.connect(lambda: self.hint_input.setFocus())
        self.hint_input.returnPressed.connect(self._on_submit)
        
        self.viewmodel.creation_failed.connect(self._show_error)
        
    def _on_submit(self):
        pwd = self.password_input.text()
        confirm = self.confirm_input.text()
        hint = self.hint_input.text()
        
        self.error_label.hide()
        self.viewmodel.create_vault(pwd, confirm, hint)
        
    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()
        
    def showEvent(self, event):
        super().showEvent(event)
        self.password_input.setFocus()
