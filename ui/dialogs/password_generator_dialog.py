from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QCheckBox, QLineEdit, QGroupBox
from PySide6.QtCore import Qt, Signal
from services.password_generator import PasswordGeneratorOptions, PasswordStrength

from ui.dialogs.base_dialog import BaseDialog
from ui.widgets.typography import apply_typography
from ui.resources.styles.typography import Typography

class PasswordGeneratorDialog(BaseDialog):
    options_changed = Signal(PasswordGeneratorOptions)
    generate_requested = Signal()
    copy_requested = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__("Generate Password", parent)
        self.setMinimumWidth(400)
        
        # We repurpose footer buttons
        self.save_btn.setText("Copy to Clipboard")
        self.cancel_btn.setText("Close")
        
        # Override the connections
        self.save_btn.disconnect()
        self.cancel_btn.disconnect()
        
        self.save_btn.clicked.connect(lambda: self.copy_requested.emit(self.password_display.text()))
        self.cancel_btn.clicked.connect(self.reject)
        
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Generated Password Display
        self.password_display = QLineEdit()
        self.password_display.setReadOnly(True)
        self.password_display.setStyleSheet("padding: 8px; font-family: monospace; background: #222; border: 1px solid #444; color: white;")
        apply_typography(self.password_display, Typography.Headline)
        layout.addWidget(self.password_display)
        
        # Strength Indicator
        self.strength_label = QLabel("Strength: -")
        self.strength_label.setStyleSheet("color: #AAA;")
        layout.addWidget(self.strength_label)
        
        # Options Group
        self.options_group = QGroupBox("Options")
        self.options_group.setStyleSheet("QGroupBox { border: 1px solid #333; margin-top: 1ex; padding: 8px; color: #AAA; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }")
        self.options_layout = QVBoxLayout(self.options_group)
        
        # Length Slider
        self.length_layout = QHBoxLayout()
        self.length_label = QLabel("Length: 16")
        self.length_slider = QSlider(Qt.Horizontal)
        self.length_slider.setRange(8, 64)
        self.length_slider.setValue(16)
        self.length_slider.valueChanged.connect(self._on_length_changed)
        
        self.length_layout.addWidget(self.length_label)
        self.length_layout.addWidget(self.length_slider)
        self.options_layout.addLayout(self.length_layout)
        
        # Checkboxes
        self.uppercase_cb = QCheckBox("Uppercase (A-Z)")
        self.uppercase_cb.setChecked(True)
        self.lowercase_cb = QCheckBox("Lowercase (a-z)")
        self.lowercase_cb.setChecked(True)
        self.numbers_cb = QCheckBox("Numbers (0-9)")
        self.numbers_cb.setChecked(True)
        self.symbols_cb = QCheckBox("Symbols (!@#)")
        self.symbols_cb.setChecked(True)
        self.exclude_similar_cb = QCheckBox("Exclude Similar (i, l, 1, L, o, 0, O)")
        
        for cb in (self.uppercase_cb, self.lowercase_cb, self.numbers_cb, self.symbols_cb, self.exclude_similar_cb):
            self.options_layout.addWidget(cb)
            cb.toggled.connect(self._emit_options)
            
        layout.addWidget(self.options_group)
        
        # Extra Action
        self.generate_btn = QPushButton("Generate New")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #555;
                color: #CCC;
                padding: 6px 16px;
                border-radius: 6px;
                margin-top: 8px;
            }
            QPushButton:hover { background-color: #333; color: #FFF; }
        """)
        self.generate_btn.clicked.connect(self.generate_requested.emit)
        layout.addWidget(self.generate_btn)
        
        self.add_content(w)
        
    def _on_length_changed(self, value):
        self.length_label.setText(f"Length: {value}")
        self._emit_options()
        
    def _emit_options(self):
        options = PasswordGeneratorOptions(
            length=self.length_slider.value(),
            uppercase=self.uppercase_cb.isChecked(),
            lowercase=self.lowercase_cb.isChecked(),
            numbers=self.numbers_cb.isChecked(),
            symbols=self.symbols_cb.isChecked(),
            exclude_similar=self.exclude_similar_cb.isChecked(),
            avoid_ambiguous=False
        )
        self.options_changed.emit(options)
        
    def set_password(self, password: str, strength: PasswordStrength):
        self.password_display.setText(password)
        self.strength_label.setText(f"Strength: {strength.label}")
