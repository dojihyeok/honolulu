from PIL import Image
import os

image_path = "/Users/yunhyeok/honolulu/public/images/real/20251219_101100.jpg"

if os.path.exists(image_path):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            print(f"Width: {width}, Height: {height}")
            if width > height:
                print("Result: Landscape (가로)")
            elif height > width:
                print("Result: Portrait (세로)")
            else:
                print("Result: Square (정사각형)")
    except Exception as e:
        print(f"Error opening image: {e}")
else:
    print(f"File not found: {image_path}")
