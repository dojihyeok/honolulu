
import os
import glob
import subprocess
from PIL import Image, ImageOps

MEDIA_DIR = '/root/honolulu/public/images/real'
MAX_WIDTH = 1200
JPEG_QUALITY = 75
VIDEO_CRF = 28
VIDEO_SCALE = "1280:-2"

def optimize_image(filepath):
    try:
        # Check size to avoid re-processing small images (optional, but good)
        # But we want to fix rotation, so we must process even if small?
        # If the image was already processed badly (stripped EXIF without rotation), 
        # we can't fix it unless we restored the original.
        # Assuming we just RESTORED the originals before running this script.
        
        with Image.open(filepath) as img:
            # 1. Apply EXIF rotation (bake orientation into pixels)
            img = ImageOps.exif_transpose(img)
            
            # 2. Resize if needed
            width, height = img.size
            if width > MAX_WIDTH:
                ratio = MAX_WIDTH / width
                new_height = int(height * ratio)
                img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
                print(f"Resized & Rotated: {filepath} ({width}x{height} -> {MAX_WIDTH}x{new_height})")
            else:
                print(f"Rotated (Size OK): {filepath}")

            # 3. Save (strips EXIF by default, which is what we want since we baked it in)
            # Use specific quality
            img.save(filepath, format='JPEG', quality=JPEG_QUALITY, optimize=True)
            
    except Exception as e:
        print(f"Failed to optimize image {filepath}: {e}")

def optimize_video(filepath):
    # Only optimize if not already optimized? 
    # Hard to tell, but we can check filesize or metadata.
    # For now, let's assume we are re-running on fresh files.
    if os.path.getsize(filepath) < 5 * 1024 * 1024:
        # Skip small videos to save time/CPU
        return

    temp_path = filepath + ".temp.mp4"
    cmd = [
        'ffmpeg', '-y', '-i', filepath,
        '-vf', f'scale={VIDEO_SCALE}', 
        '-vcodec', 'libx264', 
        '-crf', str(VIDEO_CRF), 
        '-preset', 'veryfast', # Speed up
        '-acodec', 'aac',
        temp_path
    ]
    
    try:
        print(f"Optimizing video: {filepath}")
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.replace(temp_path, filepath)
    except subprocess.CalledProcessError:
        print(f"FFmpeg failed for {filepath}")
        if os.path.exists(temp_path):
            os.remove(temp_path)

def main():
    if not os.path.exists(MEDIA_DIR):
        print(f"Directory not found: {MEDIA_DIR}")
        return

    files = glob.glob(os.path.join(MEDIA_DIR, '*'))
    print(f"Found {len(files)} files to process...")
    
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            optimize_image(f)
        elif f.lower().endswith(('.mp4', '.mov')):
            optimize_video(f)

if __name__ == "__main__":
    main()
