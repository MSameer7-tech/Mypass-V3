from PySide6.QtCore import QSize, Qt
from ui.widgets.base import BaseButton
from ui.resources.styles.widget_names import WidgetNames
from ui.app.resources import Resources
from ui.resources.icons import Icons
from ui.resources.styles.metrics import Metrics
from ui.widgets.typography import apply_typography
from ui.resources.styles.typography import Typography
from ui.resources.styles.themes import ThemeManager

class PrimaryButton(BaseButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setObjectName(WidgetNames.PRIMARY_BUTTON)
        apply_typography(self, Typography.ButtonLabel)

class SecondaryButton(BaseButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setObjectName(WidgetNames.SECONDARY_BUTTON)
        apply_typography(self, Typography.ButtonLabel)

class ToolbarIconButton(BaseButton):
    """
    44x44 toolbar action icon button with 20px icon.
    """
    def __init__(self, icon_identifier: str, parent=None):
        super().__init__("", parent)
        self.setObjectName(WidgetNames.ICON_BUTTON)
        self.setFixedSize(Metrics.ICON_BUTTON_SIZE, Metrics.ICON_BUTTON_SIZE)
        self.setIconSize(QSize(Metrics.ICON_20, Metrics.ICON_20))
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(Resources.icon(icon_identifier))
        self._apply_style()

    def _apply_style(self):
        colors = ThemeManager.colors()
        self.setStyleSheet(f"""
            QPushButton#{WidgetNames.ICON_BUTTON} {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 8px;
            }}
            QPushButton#{WidgetNames.ICON_BUTTON}:hover {{
                background-color: {colors.surface_elevated};
                border-color: {colors.border};
            }}
            QPushButton#{WidgetNames.ICON_BUTTON}:pressed {{
                background-color: {colors.border};
            }}
        """)

# Backwards compatibility alias
IconButton = ToolbarIconButton


class InlineIconButton(BaseButton):
    """
    28x28 compact inline icon button with 16px icon.
    """
    def __init__(self, icon_identifier: str, parent=None):
        super().__init__("", parent)
        self.setObjectName("InlineIconButton")
        self.setFixedSize(28, 28)
        self.setIconSize(QSize(Metrics.ICON_16, Metrics.ICON_16))
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(Resources.icon(icon_identifier))
        self._apply_style()

    def _apply_style(self):
        colors = ThemeManager.colors()
        self.setStyleSheet(f"""
            QPushButton#InlineIconButton {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: 6px;
            }}
            QPushButton#InlineIconButton:hover {{
                background-color: {colors.surface_elevated};
                border-color: {colors.text_tertiary};
            }}
            QPushButton#InlineIconButton:pressed {{
                background-color: {colors.border};
            }}
        """)


class GhostIconButton(BaseButton):
    """
    Borderless ghost icon button with subtle hover background.
    """
    def __init__(self, icon_identifier: str, size: int = 24, icon_size: int = 16, parent=None):
        super().__init__("", parent)
        self.setObjectName("GhostIconButton")
        self.setFixedSize(size, size)
        self.setIconSize(QSize(icon_size, icon_size))
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(Resources.icon(icon_identifier))
        self._apply_style()

    def _apply_style(self):
        colors = ThemeManager.colors()
        self.setStyleSheet(f"""
            QPushButton#GhostIconButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
            }}
            QPushButton#GhostIconButton:hover {{
                background-color: {colors.surface_elevated};
            }}
            QPushButton#GhostIconButton:pressed {{
                background-color: {colors.border};
            }}
        """)


class CircleIconButton(BaseButton):
    """
    Circular icon button for floating controls or avatars.
    """
    def __init__(self, icon_identifier: str, size: int = 32, icon_size: int = 18, parent=None):
        super().__init__("", parent)
        self.setObjectName("CircleIconButton")
        self.setFixedSize(size, size)
        self.setIconSize(QSize(icon_size, icon_size))
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(Resources.icon(icon_identifier))
        self._apply_style(size)

    def _apply_style(self, size: int):
        colors = ThemeManager.colors()
        self.setStyleSheet(f"""
            QPushButton#CircleIconButton {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: {size // 2}px;
            }}
            QPushButton#CircleIconButton:hover {{
                background-color: {colors.surface_elevated};
                border-color: {colors.text_tertiary};
            }}
            QPushButton#CircleIconButton:pressed {{
                background-color: {colors.border};
            }}
        """)


class PillButton(BaseButton):
    """
    Compact 26px pill button for inline card actions (Copy, Show, etc.)
    Can optionally include a leading semantic icon.
    """
    def __init__(self, text="", icon_identifier: str = None, parent=None):
        super().__init__(text, parent)
        self.setObjectName(WidgetNames.PILL_BUTTON)
        apply_typography(self, Typography.Caption)
        self.setFixedHeight(26)
        self.setCursor(Qt.PointingHandCursor)
        if icon_identifier:
            self.setIcon(Resources.icon(icon_identifier))
            self.setIconSize(QSize(Metrics.ICON_16, Metrics.ICON_16))
        self._apply_style()

    def _apply_style(self):
        colors = ThemeManager.colors()
        self.setStyleSheet(f"""
            QPushButton#{WidgetNames.PILL_BUTTON} {{
                background-color: {colors.surface};
                border: 1px solid {colors.border};
                border-radius: 13px;
                padding: 0 14px;
                color: {colors.text_primary};
            }}
            QPushButton#{WidgetNames.PILL_BUTTON}:hover {{
                background-color: {colors.surface_elevated};
                border-color: {colors.text_tertiary};
            }}
            QPushButton#{WidgetNames.PILL_BUTTON}:pressed {{
                background-color: {colors.border};
            }}
        """)
