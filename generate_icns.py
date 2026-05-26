import os
import shutil
import subprocess
from PIL import Image

def generate_icns():
    source_img = "assets/logo.png"
    if not os.path.exists(source_img):
        print(f"Source image {source_img} not found.")
        return

    iconset_dir = "assets/icon.iconset"
    if os.path.exists(iconset_dir):
        shutil.rmtree(iconset_dir)
    os.makedirs(iconset_dir)

    sizes = [16, 32, 128, 256, 512]
    
    img = Image.open(source_img)
    
    for size in sizes:
        # standard resolution
        resized = img.resize((size, size), Image.Resampling.LANCZOS)
        resized.save(os.path.join(iconset_dir, f"icon_{size}x{size}.png"))
        
        # high resolution (@2x)
        resized_2x = img.resize((size*2, size*2), Image.Resampling.LANCZOS)
        resized_2x.save(os.path.join(iconset_dir, f"icon_{size}x{size}@2x.png"))

    # run iconutil
    print("Running iconutil...")
    result = subprocess.run(["iconutil", "-c", "icns", iconset_dir, "-o", "assets/icon.icns"])
    
    if result.returncode == 0:
        print("Successfully generated assets/icon.icns")
        shutil.rmtree(iconset_dir)
    else:
        print("Failed to generate icns")

if __name__ == "__main__":
    generate_icns()
