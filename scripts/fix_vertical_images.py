import os
import re
from PIL import Image, ExifTags

# Configuration
DATA_FILE = '/Users/yunhyeok/honolulu/src/data/real.ts'
IMAGE_DIR = '/Users/yunhyeok/honolulu/public'

def get_image_info(relative_path):
    full_path = os.path.join(IMAGE_DIR, relative_path.lstrip('/'))
    if not os.path.exists(full_path):
        return None
    
    try:
        with Image.open(full_path) as img:
            width, height = img.size
            exif = img._getexif()
            orientation = 1
            
            if exif:
                for key, val in ExifTags.TAGS.items():
                    if val == 'Orientation':
                        if key in exif:
                            orientation = exif[key]
                        break
            
            # Orientation 6 (Rotated 90 CW) or 8 (Rotated 270 CW) means it's a vertical photo logically
            # checking if we need to swap dimensions for the metadata
            if orientation in [6, 8]:
                return height, width # Swap for logical display dimensions
            else:
                return width, height
                
    except Exception as e:
        print(f"Error processing {relative_path}: {e}")
        return None

def process_file():
    with open(DATA_FILE, 'r') as f:
        content = f.read()

    # Regex to find image entries. 
    # We look for src, then capture width and height that follow it within the same object structure roughly.
    # Note: This regex assumes width and height appear after src. Based on file view, this seems consistent.
    # Also handles cases where other keys might be in between.
    
    # Strategy: Find all src definitions, check if they are images, then find their closest width/height following them.
    
    new_content = content
    
    # Pattern to match src line and capture filename
    # Then non-greedy match until width and height lines
    # This is a bit risky with regex on full file if structure varies.
    # Let's try a line-by-line state machine approach which is safer for this structure.
    
    lines = content.split('\n')
    output_lines = []
    
    current_image_path = None
    desired_dims = None # (w, h)
    
    modified_count = 0
    
    for line in lines:
        # Check for src
        src_match = re.search(r'"src":\s*"(.*?)"', line)
        if src_match:
            path = src_match.group(1)
            if path.endswith('.jpg') or path.endswith('.png') or path.endswith('.jpeg'):
                current_image_path = path
                desired_dims = get_image_info(path)
                output_lines.append(line)
                continue
        
        # Check for width
        width_match = re.search(r'("width":\s*)(\d+)(.*)', line)
        if width_match and current_image_path and desired_dims:
            prefix, current_w, suffix = width_match.groups()
            needed_w, needed_h = desired_dims
            
            # Only update if significantly different (logic swap) or just blindly enforce "correct" logical dims
            # The user wants "vertical photos resolved". 
            # If finding says it should be High (Portrait), but file says Wide (Landscape) -> Swap.
            
            # Ensure we are applying the width from the PAIR (w, h)
            # But wait, we encounter width line separately from height line.
            # We assume regular structure where they are close.
            
            # Let's just enforce the dimensions we found from the file (with rotation applied)
            if int(current_w) != needed_w:
                line = f'{prefix}{needed_w}{suffix}'
                # print(f"Fixed Width for {current_image_path}: {current_w} -> {needed_w}")
            
            output_lines.append(line)
            continue

        # Check for height
        height_match = re.search(r'("height":\s*)(\d+)(.*)', line)
        if height_match and current_image_path and desired_dims:
            prefix, current_h, suffix = height_match.groups()
            needed_w, needed_h = desired_dims
            
            if int(current_h) != needed_h:
                line = f'{prefix}{needed_h}{suffix}'
                print(f"Updated {current_image_path}: {needed_w}x{needed_h} (was {current_h}h)")
                modified_count += 1
            
            output_lines.append(line)
            # Reset current match context after height (assuming height comes last or we are done with dims)
            # current_image_path = None 
            # desired_dims = None
            continue
            
        # Just append other lines
        output_lines.append(line)

    with open(DATA_FILE, 'w') as f:
        f.write('\n'.join(output_lines))
        
    print(f"Total images updated: {modified_count}")

if __name__ == "__main__":
    process_file()
