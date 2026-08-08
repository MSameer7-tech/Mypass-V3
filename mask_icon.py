import sys
from PIL import Image, ImageDraw

def mask_image(input_path, output_path, corner_radius):
    im = Image.open(input_path).convert("RGBA")
    
    # Create a mask with rounded corners
    mask = Image.new("L", im.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), im.size], radius=corner_radius, fill=255)
    
    # Apply the mask
    im.putalpha(mask)
    im.save(output_path, "PNG")
    print(f"Saved transparent icon to {output_path}")

if __name__ == "__main__":
    mask_image(sys.argv[1], sys.argv[2], int(sys.argv[3]))
