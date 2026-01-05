import os
import subprocess
import glob

# Configuration
MEDIA_DIR = '/root/honolulu/public/images/real'

# Script to generate poster images for all videos
# 1. Find all mp4 files
# 2. Check if a corresponding jpg poster exists
# 3. If not, generate one using ffmpeg (first frame)

def generate_posters():
    print("--- 🎬 Generating Video Posters ---")
    
    # Check if directory exists
    if not os.path.exists(MEDIA_DIR):
        print(f"Error: Directory {MEDIA_DIR} not found.")
        return

    # Find videos
    mp4_files = glob.glob(os.path.join(MEDIA_DIR, "*.mp4"))
    print(f"Found {len(mp4_files)} video files.")

    count = 0
    for mp4_path in mp4_files:
        # Construct poster path: video.mp4 -> video_poster.jpg
        base_name = os.path.splitext(mp4_path)[0]
        poster_path = f"{base_name}_poster.jpg"

        if not os.path.exists(poster_path):
            print(f"Generating poster for: {os.path.basename(mp4_path)}")
            try:
                # ffmpeg command: extract 1 frame at 00:00:01 (to avoid black start frames if any)
                # -ss 00:00:00.1 : Seek to 0.1s
                # -vframes 1 : Capture 1 frame
                # -q:v 2 : High jpeg quality
                cmd = [
                    'ffmpeg', '-y', 
                    '-i', mp4_path, 
                    '-ss', '00:00:00.1', 
                    '-vframes', '1', 
                    '-q:v', '2', 
                    poster_path
                ]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                count += 1
            except subprocess.CalledProcessError as e:
                print(f"Failed to generate poster for {mp4_path}: {e}")
        else:
            # Poster already exists
            pass
            
    print(f"--- ✅ Generated {count} new posters. ---")

if __name__ == "__main__":
    # Ensure ffmpeg is installed
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("Installing FFmpeg...")
        subprocess.run(['apt-get', 'update'], stdout=subprocess.DEVNULL)
        subprocess.run(['apt-get', 'install', '-y', 'ffmpeg'], stdout=subprocess.DEVNULL)
        
    generate_posters()
