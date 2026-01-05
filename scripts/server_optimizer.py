
import os
import subprocess
import glob
from PIL import Image

MEDIA_DIR = '/root/honolulu/public/images/real'
MAX_WIDTH = 1200
JPEG_QUALITY = 70
VIDEO_CRF = 28
VIDEO_SCALE = "1280:-2" # 720p

def install_deps():
    print("Installing dependencies...")
    subprocess.run(['apt-get', 'update'], check=True)
    subprocess.run(['apt-get', 'install', '-y', 'ffmpeg', 'python3-pip'], check=True)
    subprocess.run(['pip3', 'install', 'Pillow'], check=True)

def optimize_image(filepath):
    try:
        with Image.open(filepath) as img:
            # Check if resize needed
            width, height = img.size
            if width > MAX_WIDTH:
                ratio = MAX_WIDTH / width
                new_height = int(height * ratio)
                img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
                print(f"Resized image: {filepath} ({width}x{height} -> {MAX_WIDTH}x{new_height})")
            
            # Save carefully - if it's strictly optimization, we overwrite
            # Note: exif updates might be lost, but for web speed this is intentional
            # We must preserve orientation if possible, but Pillow handles it if we are careful.
            # Actually, standardizing orientation is better for web.
            
            # Handle orientation
            try:
                exif = img._getexif()
                if exif:
                    from PIL import ExifTags
                    orientation = next((k for k, v in ExifTags.TAGS.items() if v == 'Orientation'), None)
                    if orientation and orientation in exif:
                        val = exif[orientation]
                        if val == 3: img = img.rotate(180, expand=True)
                        elif val == 6: img = img.rotate(270, expand=True)
                        elif val == 8: img = img.rotate(90, expand=True)
            except Exception:
                pass

            img.save(filepath, quality=JPEG_QUALITY, optimize=True)
            print(f"Optimized image: {filepath}")
    except Exception as e:
        print(f"Failed to optimize image {filepath}: {e}")

def optimize_video(filepath):
    temp_path = filepath + ".temp.mp4"
    # ffmpeg -i input -vf scale=1280:-2 -vcodec libx264 -crf 28 -preset medium -acodec copy output
    cmd = [
        'ffmpeg', '-y', '-i', filepath,
        '-vf', f'scale={VIDEO_SCALE}', 
        '-vcodec', 'libx264', 
        '-crf', str(VIDEO_CRF), 
        '-preset', 'fast',
        '-acodec', 'aac', # Re-encode audio to aac to be safe, or copy if sure
        temp_path
    ]
    
    try:
        print(f"Optimizing video: {filepath}")
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.replace(temp_path, filepath)
        print(f"Finished video: {filepath}")
    except subprocess.CalledProcessError:
        print(f"FFmpeg failed for {filepath}")
        if os.path.exists(temp_path):
            os.remove(temp_path)

def main():
    if not os.path.exists(MEDIA_DIR):
        print(f"Directory not found: {MEDIA_DIR}")
        return

    # Check if we should install deps (simple check if ffmpeg exists)
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        install_deps()

    files = glob.glob(os.path.join(MEDIA_DIR, '*'))
    for f in files:
        if f.lower().endswith(('.jpg', '.jpeg', '.png')):
            # Check size, if huge, optimize
            if os.path.getsize(f) > 500 * 1024: # Only optimize if > 500KB to save time
                optimize_image(f)
        elif f.lower().endswith(('.mp4', '.mov')):
             # Check size, if huge, optimize
             # Assuming arbitrary threshold or just do all
             if os.path.getsize(f) > 5 * 1024 * 1024: # > 5MB
                optimize_video(f)

if __name__ == "__main__":
    main()
