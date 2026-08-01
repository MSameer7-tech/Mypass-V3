import os
import weakref
from typing import Dict, Any, Type
from PySide6.QtWidgets import QApplication

from ui.resources.styles.colors import DarkColors, LightColors, ColorPalette
from ui.resources.styles.typography import Typography
from ui.resources.styles.spacing import Spacing
from ui.resources.styles.radius import Radius
from ui.resources.styles.elevation import ZLayer
from ui.resources.styles.metrics import Metrics, Opacity
from ui.resources.styles.enums import ThemeMode

class ThemeManager:
    _listeners = weakref.WeakSet()
    _current_mode: ThemeMode = ThemeMode.DARK
    _qss_template: str = ""

    @classmethod
    def load_qss_template(cls, qss_path: str):
        if os.path.exists(qss_path):
            with open(qss_path, "r", encoding="utf-8") as f:
                cls._qss_template = f.read()

    @classmethod
    def register(cls, component):
        """Register a component to receive theme updates if it implements apply_theme()"""
        cls._listeners.add(component)
        if hasattr(component, "apply_theme"):
            try:
                component.apply_theme()
            except Exception:
                pass

    @classmethod
    def set_theme(cls, mode: ThemeMode):
        cls._current_mode = mode
        cls._apply_global_stylesheet()
        cls._notify_theme_changed()

    @classmethod
    def current_mode(cls) -> ThemeMode:
        return cls._current_mode

    @classmethod
    def colors(cls) -> ColorPalette:
        return LightColors if cls._current_mode == ThemeMode.LIGHT else DarkColors

    @classmethod
    def typography(cls) -> Type[Typography]:
        return Typography

    @classmethod
    def spacing(cls) -> Type[Spacing]:
        return Spacing

    @classmethod
    def radius(cls) -> Type[Radius]:
        return Radius

    @classmethod
    def metrics(cls) -> Type[Metrics]:
        return Metrics

    @classmethod
    def elevation(cls) -> Type[ZLayer]:
        return ZLayer

    @classmethod
    def _apply_global_stylesheet(cls):
        app = QApplication.instance()
        if not app or not cls._qss_template:
            return

        c = cls.colors()
        t = cls.typography()
        r = cls.radius()
        m = cls.metrics()
        o = cls.Opacity() if hasattr(cls, 'Opacity') else Opacity # Just use Opacity directly

        # Build token dictionary
        tokens = {
            # Colors
            "background": c.background,
            "surface": c.surface,
            "surface_elevated": c.surface_elevated,
            "border": c.border,
            "text_primary": c.text_primary,
            "text_secondary": c.text_secondary,
            "accent": c.accent,
            "accent_hover": c.accent_hover,
            "success": c.success,
            "warning": c.warning,
            "danger": c.danger,
            "input_bg": c.input_bg,
            
            # Typography
            "font_family": t.Display.family,
            
            "Display_size": str(t.Display.size),
            "Display_weight": t.Display.weight,
            "Title_size": str(t.Title.size),
            "Title_weight": t.Title.weight,
            "Headline_size": str(t.Headline.size),
            "Headline_weight": t.Headline.weight,
            "Body_size": str(t.Body.size),
            "Body_weight": t.Body.weight,
            "Caption_size": str(t.Caption.size),
            "Caption_weight": t.Caption.weight,
            "Overline_size": str(t.Overline.size),
            "Overline_weight": t.Overline.weight,
            
            # Radius
            "radius_small": str(r.SMALL),
            "radius_medium": str(r.MEDIUM),
            "radius_large": str(r.LARGE),
            "radius_xlarge": str(r.XLARGE),
            
            # Metrics
            "button_height": str(m.BUTTON_HEIGHT),
            "input_height": str(m.INPUT_HEIGHT),
            
            # Opacities
            "opacity_disabled": str(Opacity.DISABLED)
        }

        # Interpolate
        qss = cls._qss_template
        for key, value in tokens.items():
            qss = qss.replace(f"{{{{ {key} }}}}", value)
            
        app.setStyleSheet(qss)

    @classmethod
    def _notify_theme_changed(cls):
        for component in list(cls._listeners):
            if hasattr(component, "apply_theme"):
                try:
                    component.apply_theme()
                except Exception:
                    pass
