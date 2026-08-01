import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QScrollArea, QFormLayout
)
from PySide6.QtCore import Qt

from ui.app.application import MyPassApplication
from ui.resources.styles.themes import ThemeManager
from ui.resources.styles.enums import ThemeMode, BadgeVariant

from ui.widgets.buttons import PrimaryButton, SecondaryButton, IconButton
from ui.widgets.inputs import TextField, SearchField, PasswordField
from ui.widgets.typography import DisplayText, Title, Headline, Body, Caption, Label, Overline
from ui.widgets.layout import Card, Divider
from ui.widgets.indicators import Badge, EmptyState, LoadingIndicator

class ComponentCatalog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MyPass Qt Component Catalog")
        self.resize(1000, 800)
        self.setObjectName("BaseFrame") # Make sure the root frame is styled
        
        main_layout = QVBoxLayout(self)
        
        # Header Controls
        header = QHBoxLayout()
        header.addWidget(Title("Design System Components"))
        header.addStretch()
        
        self.theme_btn = SecondaryButton("Switch to Light Theme")
        self.theme_btn.clicked.connect(self._toggle_theme)
        header.addWidget(self.theme_btn)
        
        main_layout.addLayout(header)
        main_layout.addWidget(Divider("horizontal"))
        
        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self.tabs.addTab(self._build_buttons_tab(), "Buttons")
        self.tabs.addTab(self._build_inputs_tab(), "Inputs")
        self.tabs.addTab(self._build_typography_tab(), "Typography")
        self.tabs.addTab(self._build_indicators_tab(), "Indicators")
        self.tabs.addTab(self._build_layout_tab(), "Layout")

    def _toggle_theme(self):
        if ThemeManager.current_mode() == ThemeMode.DARK:
            ThemeManager.set_theme(ThemeMode.LIGHT)
            self.theme_btn.setText("Switch to Dark Theme")
        else:
            ThemeManager.set_theme(ThemeMode.DARK)
            self.theme_btn.setText("Switch to Light Theme")

    def _wrap_in_scroll(self, widget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        # Transparent background for scroll area
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; } QWidget#scroll_content { background-color: transparent; }")
        widget.setObjectName("scroll_content")
        return scroll

    def _build_buttons_tab(self):
        w = QWidget()
        layout = QFormLayout(w)
        layout.setSpacing(24)
        
        layout.addRow("Primary Button", PrimaryButton("Save Changes"))
        layout.addRow("Secondary Button", SecondaryButton("Cancel"))
        
        icon_box = QHBoxLayout()
        icon_box.addWidget(IconButton("settings"))
        icon_box.addWidget(IconButton("add"))
        icon_box.addWidget(IconButton("search"))
        icon_box.addStretch()
        layout.addRow("Icon Buttons", icon_box)
        
        return self._wrap_in_scroll(w)

    def _build_inputs_tab(self):
        w = QWidget()
        layout = QFormLayout(w)
        layout.setSpacing(24)
        
        layout.addRow("Text Field", TextField("Enter username..."))
        layout.addRow("Password Field", PasswordField("Master Password"))
        layout.addRow("Search Field", SearchField("Search vault..."))
        
        return self._wrap_in_scroll(w)

    def _build_typography_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(16)
        
        layout.addWidget(Overline("OVERLINE TEXT"))
        layout.addWidget(DisplayText("Display Text"))
        layout.addWidget(Title("Title Text"))
        layout.addWidget(Headline("Headline Text"))
        layout.addWidget(Body("Body Text (Standard)"))
        layout.addWidget(Caption("Caption Text (Smaller, Secondary)"))
        layout.addWidget(Label("Label Text"))
        
        layout.addStretch()
        return self._wrap_in_scroll(w)

    def _build_indicators_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(24)
        
        # Badges
        layout.addWidget(Headline("Badges"))
        badges_layout = QHBoxLayout()
        badges_layout.addWidget(Badge("Success", BadgeVariant.SUCCESS))
        badges_layout.addWidget(Badge("Warning", BadgeVariant.WARNING))
        badges_layout.addWidget(Badge("Error", BadgeVariant.ERROR))
        badges_layout.addWidget(Badge("Info", BadgeVariant.INFO))
        badges_layout.addWidget(Badge("Primary", BadgeVariant.PRIMARY))
        badges_layout.addWidget(Badge("Neutral", BadgeVariant.NEUTRAL))
        badges_layout.addStretch()
        
        badges_container = QWidget()
        badges_container.setLayout(badges_layout)
        layout.addWidget(badges_container)
        
        layout.addWidget(Divider("horizontal"))
        
        # Loading
        layout.addWidget(Headline("Loading Indicator"))
        layout.addWidget(LoadingIndicator())
        
        layout.addWidget(Divider("horizontal"))
        
        # Empty State
        layout.addWidget(Headline("Empty State"))
        empty = EmptyState(
            icon_name="shield",
            title="Vault is Empty",
            description="You don't have any saved credentials yet. Add one to get started.",
            action_button=PrimaryButton("Add Password"),
            secondary_action=SecondaryButton("Import")
        )
        layout.addWidget(empty)
        
        layout.addStretch()
        return self._wrap_in_scroll(w)

    def _build_layout_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setSpacing(24)
        
        card = Card()
        card_layout = QVBoxLayout(card)
        card_layout.addWidget(Headline("Card Title"))
        card_layout.addWidget(Body("This is content inside a card. It has elevated styling and border radius."))
        card_layout.addWidget(Divider("horizontal"))
        
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_box.addWidget(PrimaryButton("Action"))
        card_layout.addLayout(btn_box)
        
        layout.addWidget(card)
        layout.addStretch()
        
        return self._wrap_in_scroll(w)

def main():
    app = MyPassApplication(sys.argv)
    
    # Load and apply QSS
    import os
    qss_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 
        "ui/resources/styles/main.qss"
    ))
    ThemeManager.load_qss_template(qss_path)
    ThemeManager.set_theme(ThemeMode.DARK)
    
    catalog = ComponentCatalog()
    catalog.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
