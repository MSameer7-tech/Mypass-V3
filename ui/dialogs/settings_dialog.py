from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QComboBox, QCheckBox, QLabel, QTabWidget
from PySide6.QtCore import QSettings
from ui.dialogs.base_dialog import BaseDialog
from ui.widgets.typography import HeadlineLabel, BodyLabel

class SettingsDialog(BaseDialog):
    def __init__(self, parent=None):
        super().__init__("Settings", parent)
        self.setMinimumWidth(400)
        self.settings = QSettings("MyPass", "MyPassApp")
        
        self.save_btn.setText("Apply")
        self.save_btn.clicked.disconnect()
        self.save_btn.clicked.connect(self._apply_settings)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #333; border-radius: 4px; background: transparent; }
            QTabBar::tab { background: #2A2A2A; color: #AAA; padding: 8px 16px; border: 1px solid #333; }
            QTabBar::tab:selected { background: #333; color: #FFF; font-weight: bold; }
        """)
        
        self.tabs.addTab(self._create_general_tab(), "General")
        self.tabs.addTab(self._create_security_tab(), "Security")
        self.tabs.addTab(self._create_about_tab(), "About")
        
        self.add_content(self.tabs)
        self._load_settings()
        
    def _create_general_tab(self):
        w = QWidget()
        layout = QFormLayout(w)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        
        layout.addRow("Theme", self.theme_combo)
        return w
        
    def _create_security_tab(self):
        w = QWidget()
        layout = QFormLayout(w)
        
        self.autolock_combo = QComboBox()
        self.autolock_combo.addItems(["1 minute", "5 minutes", "10 minutes", "30 minutes", "Never"])
        layout.addRow("Auto-lock timer", self.autolock_combo)
        
        from ui.services.biometrics import create_biometric_service
        self.bio = create_biometric_service()
        
        self.bio_check = QCheckBox("Unlock using Touch ID / Windows Hello")
        if not self.bio.is_available():
            self.bio_check.setEnabled(False)
            self.bio_check.setText("Biometrics not available on this device")
            
        layout.addRow("Biometrics", self.bio_check)
        
        return w
        
    def _create_about_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        
        title = HeadlineLabel("MyPass")
        layout.addWidget(title)
        
        layout.addWidget(BodyLabel("Version: 1.0.0 (Release Candidate)"))
        layout.addWidget(BodyLabel("License: MIT"))
        
        from utils.helpers import build_data_path
        from utils.constants import DATA_DIR_NAME
        data_dir = build_data_path(DATA_DIR_NAME, "")
        
        dir_lbl = BodyLabel(f"Data Directory: {data_dir}")
        dir_lbl.setWordWrap(True)
        layout.addWidget(dir_lbl)
        
        layout.addStretch()
        return w
    
    def _load_settings(self):
        """Load persisted settings into the UI controls."""
        theme = self.settings.value("settings/theme", "Dark")
        self.theme_combo.setCurrentText(theme)
        
        autolock = self.settings.value("settings/autolock", "5 minutes")
        self.autolock_combo.setCurrentText(autolock)
        
        bio_enabled = self.settings.value("settings/biometrics_enabled", False, type=bool)
        if self.bio_check.isEnabled():
            self.bio_check.setChecked(bio_enabled)
    
    def _apply_settings(self):
        """Persist settings to QSettings."""
        self.settings.setValue("settings/theme", self.theme_combo.currentText())
        self.settings.setValue("settings/autolock", self.autolock_combo.currentText())
        self.settings.setValue("settings/biometrics_enabled", self.bio_check.isChecked())
        self.settings.sync()
        self.accept()
