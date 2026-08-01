from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt

from ui.widgets.base import BaseFrame
from ui.widgets.inputs import PasswordField
from ui.widgets.buttons import PrimaryButton, SecondaryButton
from ui.widgets.typography import HeadlineLabel, BodyLabel

class UnlockView(BaseFrame):
    def __init__(self, viewmodel, parent=None):
        super().__init__(parent)
        self.setObjectName("UnlockView")
        self.viewmodel = viewmodel
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(24)
        
        # Center container
        container = QWidget()
        container.setFixedWidth(400)
        c_layout = QVBoxLayout(container)
        c_layout.setSpacing(16)
        
        self.title = HeadlineLabel("Unlock MyPass")
        self.title.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(self.title)
        
        self.subtitle = BodyLabel("Enter your master password to continue.")
        self.subtitle.setAlignment(Qt.AlignCenter)
        c_layout.addWidget(self.subtitle)
        
        self.password_input = PasswordField("Master Password")
        c_layout.addWidget(self.password_input)
        
        # Error Label
        self.error_label = BodyLabel("")
        self.error_label.setStyleSheet("color: var(--color-danger);")
        self.error_label.hide()
        c_layout.addWidget(self.error_label)
        
        btn_layout = QHBoxLayout()
        self.unlock_btn = PrimaryButton("Unlock")
        
        self.bio_btn = SecondaryButton("Touch ID")
        self.bio_btn.hide() # Hidden by default, shown if available
        
        btn_layout.addWidget(self.bio_btn)
        btn_layout.addWidget(self.unlock_btn)
        c_layout.addLayout(btn_layout)
        
        layout.addWidget(container)
        
        self._connect_signals()
        
    def _connect_signals(self):
        self.unlock_btn.clicked.connect(self._on_submit)
        self.bio_btn.clicked.connect(self.viewmodel.attempt_biometric_unlock)
        self.password_input.returnPressed.connect(self._on_submit)
        
        # Focus management: Esc clears
        self.password_input.keyPressEvent = self._custom_key_press
        
        self.viewmodel.unlock_failed.connect(self._show_error)
        
    def _on_submit(self):
        pwd = self.password_input.text()
        self.error_label.hide()
        self.viewmodel.unlock(pwd)
        
    def _show_error(self, message: str):
        self.error_label.setText(message)
        self.error_label.show()
        # Premium Focus Management: Select all on failure
        self.password_input.selectAll()
        self.password_input.setFocus()
        
    def _custom_key_press(self, event):
        if event.key() == Qt.Key_Escape:
            self.password_input.clear()
        else:
            # Call the original class keyPressEvent, not super() because it's overridden on the instance
            type(self.password_input).keyPressEvent(self.password_input, event)
            
    def showEvent(self, event):
        """Auto-focus when view is shown."""
        super().showEvent(event)
        self.prepare_for_input()
        
    def prepare_for_input(self):
        """Reset the unlock form for a fresh attempt. 
        Called by showEvent and directly by LockOverlay."""
        self.password_input.clear()
        self.error_label.hide()
        self.password_input.setFocus()
        if self.viewmodel.biometrics.is_available():
            self.bio_btn.show()
        else:
            self.bio_btn.hide()
