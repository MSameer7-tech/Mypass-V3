import io
import os
import cairosvg
import customtkinter as ctk
from PIL import Image

from .themes import LightTheme, DarkTheme

class IconLoader:
    _cache: dict[str, ctk.CTkImage] = {}
    _base_dir: str = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "icons")

    @classmethod
    def load(cls, name: str, size: int = 24) -> ctk.CTkImage | None:
        """
        Loads an SVG icon from assets/icons/, colorizes it for both Light and Dark themes,
        caches it, and returns a CTkImage.
        """
        cache_key = f"{name}_{size}"
        if cache_key in cls._cache:
            return cls._cache[cache_key]

        svg_path = os.path.join(cls._base_dir, f"{name}.svg")
        if not os.path.exists(svg_path):
            print(f"Warning: Icon '{name}' not found at {svg_path}")
            return None

        with open(svg_path, "r", encoding="utf-8") as f:
            svg_data = f.read()

        # Generate Light Theme Image (used when ctk mode is "light")
        light_svg = svg_data.replace('stroke="currentColor"', f'stroke="{LightTheme.text_primary}"')
        light_png = cairosvg.svg2png(bytestring=light_svg.encode("utf-8"), output_width=size, output_height=size)
        light_img = Image.open(io.BytesIO(light_png))

        # Generate Dark Theme Image (used when ctk mode is "dark")
        dark_svg = svg_data.replace('stroke="currentColor"', f'stroke="{DarkTheme.text_primary}"')
        dark_png = cairosvg.svg2png(bytestring=dark_svg.encode("utf-8"), output_width=size, output_height=size)
        dark_img = Image.open(io.BytesIO(dark_png))

        ctk_img = ctk.CTkImage(light_image=light_img, dark_image=dark_img, size=(size, size))
        cls._cache[cache_key] = ctk_img
        return ctk_img
