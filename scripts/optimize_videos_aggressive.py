
import os
import subprocess
import glob

# Media directory on server
MEDIA_DIR = "/root/honolulu/public/images/real"

def optimize_videos_aggressive():
    print(f"Starting AGGRESSIVE video optimization in {MEDIA_DIR}...")
    
    mp4_files = glob.glob(os.path.join(MEDIA_DIR, "*.mp4"))
    
    for mp4_path in mp4_files:
        try:
            # Check size
            if not os.path.exists(mp4_path): continue
            
            size_mb = os.path.getsize(mp4_path) / (1024 * 1024)
            if size_mb < 2.0:
                print(f"Skipping {os.path.basename(mp4_path)} ({size_mb:.2f}MB) - acceptable size")
                continue
                
            print(f"Aggressively optimizing {os.path.basename(mp4_path)} ({size_mb:.2f}MB)...")
            
            temp_path = mp4_path + ".temp.mp4"
            
            # FFmpeg command: scale to 640px width (Mobile Optimized), CRF 30 (Lower Quality but tiny size), maxrate 1Mbps
            cmd = [
                'ffmpeg', '-y', '-i', mp4_path,
                '-vf', "scale='min(640,iw)':-2", 
                '-c:v', 'libx264',
                '-preset', 'veryfast',
                '-crf', '30',
                '-maxrate', '1000k', # Limit to 1Mbps
                '-bufsize', '2000k',
                '-c:a', 'aac', '-b:a', '96k',
                '-movflags', '+faststart',
                temp_path
            ]
            
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                # Check if new file is actually smaller
                new_size = os.path.getsize(temp_path)
                if new_size < os.path.getsize(mp4_path):
                    os.replace(temp_path, mp4_path)
                    new_size_mb = new_size / (1024 * 1024)
                    print(f" -> Done. New size: {new_size_mb:.2f}MB")
                else:
                    print(" -> Optimization didn't reduce size. Keeping original.")
                    os.remove(temp_path)
                    
            except subprocess.CalledProcessError:
                print(f" -> Failed to optimize {mp4_path}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        except Exception as e:
            print(f"Error processing {mp4_path}: {e}")
            continue

if __name__ == "__main__":
    optimize_videos_aggressive()
