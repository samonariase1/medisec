from PIL import Image

# 1. Open the original image using a raw string 'r' to prevent Windows path escaping
img = Image.open(r"C:\Users\seaz\Downloads\MediSec_Logo.png")  

# 2. Crop to the central shield graphic (removing the text at the bottom)
# Since the image is a 1:1 square canvas, we crop the top ~68% to isolate the shield
width, height = img.size
crop_box = (0, 0, width, int(height * 0.68))
cropped_shield = img.crop(crop_box)

# 3. Square up the cropped canvas (padding with whitespace or centering if needed)
shield_w, shield_h = cropped_shield.size
square_size = max(shield_w, shield_h)
square_img = Image.new("RGBA", (square_size, square_size), (255, 255, 255, 0))

# Center the shield onto the transparent square layout
square_img.paste(cropped_shield, ((square_size - shield_w) // 2, (square_size - shield_h) // 2))

# 4. Standard extension dimensions to generate
target_sizes = [16, 32, 48, 128]

# 5. Loop, resize, and save directly into your workspace
for size in target_sizes:
    resized_icon = square_img.resize((size, size), Image.Resampling.LANCZOS)
    resized_icon.save(f"icon{size}.png", "PNG")
    print(f"Generated: icon{size}.png")
