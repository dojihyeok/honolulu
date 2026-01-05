
import os
import subprocess
import glob

# Media directory on server
MEDIA_DIR = "/root/honolulu/public/images/real"
TARGET_BITRATE = "1500k"  # Target 1.5Mbps

def optimize_videos():
    print(f"Starting video optimization in {MEDIA_DIR}...")
    
    mp4_files = glob.glob(os.path.join(MEDIA_DIR, "*.mp4"))
    
    for mp4_path in mp4_files:
        # Check size
        size_mb = os.path.getsize(mp4_path) / (1024 * 1024)
        if size_mb < 2.0:
            print(f"Skipping {os.path.basename(mp4_path)} ({size_mb:.2f}MB) - already small")
            continue
            
        print(f"Optimizing {os.path.basename(mp4_path)} ({size_mb:.2f}MB)...")
        
        temp_path = mp4_path + ".temp.mp4"
        
        # FFmpeg command: scale to 720p width (maintain aspect), CRF 26 (good balance), maxrate 1.5M
        cmd = [
            'ffmpeg', '-y', '-i', mp4_path,
            '-vf', "scale='min(720,iw)':-2",  # Scale width to 720px max, keep aspect
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '26',
            '-maxrate', TARGET_BITRATE,
            '-bufsize', '3000k',
            '-c:a', 'aac', '-b:a', '128k',
            temp_path
        ]
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            # Replace original
            os.replace(temp_path, mp4_path)
            new_size_mb = os.path.getsize(mp4_path) / (1024 * 1024)
            print(f" -> Done. New size: {new_size_mb:.2f}MB")
        except subprocess.CalledProcessError:
            print(f" -> Failed to optimize {mp4_path}")
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    optimize_videos()
