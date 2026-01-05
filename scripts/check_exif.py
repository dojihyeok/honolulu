from PIL import Image, ExifTags
import os

image_path = "/Users/yunhyeok/honolulu/public/images/real/20251219_101100.jpg"

if os.path.exists(image_path):
    try:
        with Image.open(image_path) as img:
            print(f"Physical Dimensions: {img.width} x {img.height}")
            
            exif = img._getexif()
            if exif:
                orientation_key = None
                for key, val in ExifTags.TAGS.items():
                    if val == 'Orientation':
                        orientation_key = key
                        break
                
                if orientation_key and orientation_key in exif:
                    orientation = exif[orientation_key]
                    print(f"EXIF Orientation Value: {orientation}")
                    
                    if orientation == 6 or orientation == 8:
                        print("Result with EXIF: Portrait (세로 - 회전됨)")
                    elif orientation == 1 or orientation == 3:
                        print("Result with EXIF: Landscape (가로 - 회전 없음 또는 180도)")
                    else:
                        print(f"Result with EXIF: Other orientation ({orientation})")
                else:
                    print("EXIF Orientation tag not found.")
            else:
                print("No EXIF data found.")
                
    except Exception as e:
        print(f"Error opening image: {e}")
else:
    print(f"File not found: {image_path}")
