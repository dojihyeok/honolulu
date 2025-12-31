
import os
import subprocess
import sys
from pathlib import Path
from PIL import Image

def optimize_image(file_path, quality=60, max_width=1080):
    """
    Optimize image: Resize to max_width, save with low quality (60).
    """
    try:
        img = Image.open(file_path)
        
        # Calculate new size
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Save back to same path (or temp then rename)
        # Convert to RGB if RGBA/P to save as JPEG
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            
        img.save(file_path, "JPEG", quality=quality, optimize=True)
        print(f"✅ Optimized Image: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error optimizing image {file_path}: {e}")
        return False

def optimize_video(file_path, crf=28, height=720):
    """
    Optimize video: Resize to 720p, use H.264 CRF 28.
    """
    temp_path = str(file_path) + ".temp.mp4"
    
    # FFmpeg command
    # -vf scale=-2:720 : Scale height to 720, width auto (divisible by 2)
    # -c:v libx264 : Codec
    # -crf 28 : Constant Rate Factor (higher = lower quality, smaller size. 23 is default, 28 is high compression)
    # -preset veryslow : Better compression efficiency
    # -c:a aac -b:a 96k : Audio compression
    # -movflags +faststart : Optimize for web streaming
    
    cmd = [
        "ffmpeg", "-y", "-i", str(file_path),
        "-vf", f"scale=-2:{height}",
        "-c:v", "libx264",
        "-crf", str(crf),
        "-preset", "medium",
        "-c:a", "aac", "-b:a", "96k",
        "-movflags", "+faststart",
        temp_path
    ]
    
    try:
        print(f"🎬 Processing Video: {file_path}...")
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Replace original
        os.replace(temp_path, file_path)
        print(f"✅ Optimized Video: {file_path}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ FFmpeg failed for {file_path}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False

def main():
    target_dir = Path("public/images/real")
    if not target_dir.exists():
        print(f"Directory not found: {target_dir}")
        return

    print("🚀 Starting Aggressive Media Optimization...")
    print("Targets: Images (Max 1080px, Q60), Videos (720p, CRF 28)")

    for file_path in target_dir.glob("*"):
        if file_path.name.lower().endswith(('.jpg', '.jpeg', '.png')):
            # Optimize Image
            optimize_image(file_path)
        elif file_path.name.lower().endswith(('.mp4', '.mov')):
            # Optimize Video
            optimize_video(file_path)
    
    print("✨ All done!")

if __name__ == "__main__":
    main()
