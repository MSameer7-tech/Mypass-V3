import os
import requests
import cairosvg

ICONS = ["eye", "eye-off", "copy", "search", "globe", "lock", "mail"]

ASSETS_DIR = "assets"
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

for icon in ICONS:
    url = f"https://raw.githubusercontent.com/feathericons/feather/master/icons/{icon}.svg"
    response = requests.get(url)
    if response.status_code == 200:
        svg_content = response.text
        # Replace currentColor with white or a very light gray for the dark theme
        svg_content = svg_content.replace('currentColor', '#E0E0E0')
        
        # Save SVG temporarily
        svg_path = os.path.join(ASSETS_DIR, f"{icon}.svg")
        with open(svg_path, "w") as f:
            f.write(svg_content)
            
        # Convert to PNG
        png_path = os.path.join(ASSETS_DIR, f"{icon}.png")
        cairosvg.svg2png(url=svg_path, write_to=png_path, output_width=64, output_height=64)
        print(f"Downloaded and converted {icon}.png")
        
        # Cleanup SVG
        os.remove(svg_path)
    else:
        print(f"Failed to download {icon}")

print("Done downloading icons.")
