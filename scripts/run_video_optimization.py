import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Optimized video processing script
# 1. Finds all mp4 files.
# 2. Checks if they are already optimized (e.g., file size < 5MB for short clips, or just re-encode safely).
# 3. Uses a temporary file to encode.
# 4. Logs progress explicitly.

VIDEO_OPT_SCRIPT = """
set -e

# Ensure ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "Installing FFmpeg..."
    apt-get update && apt-get install -y ffmpeg
fi

cd /root/honolulu/public/images/real

echo "--- Starting Video Optimization ---"

# Find all mp4 files
find . -name "*.mp4" | while read file; do
    echo "Processing: $file"
    
    # Get file size in bytes
    size=$(wc -c < "$file")
    
    # Skip if smaller than 5MB (likely already optimized or very short)
    if [ "$size" -lt 5000000 ]; then
        echo "Skipping $file (Small enough: $size bytes)"
        continue
    fi
    
    # Rename original to .bak before processing to be safe? 
    # Or write to .tmp and move.
    
    # Encode: 720p, CRF 28 (Aggressive compression for web), AAC audio
    ffmpeg -y -v error -i "$file" -vf "scale='min(1280,iw)':-2" -vcodec libx264 -crf 28 -preset fast -acodec aac -b:a 128k "${file}.tmp.mp4" < /dev/null
    
    if [ -f "${file}.tmp.mp4" ]; then
        # Retrieve size of new file
        new_size=$(wc -c < "${file}.tmp.mp4")
        
        # Only replace if new file is smaller
        if [ "$new_size" -lt "$size" ]; then
            mv "${file}.tmp.mp4" "$file"
            echo "Optimized: $file ($size -> $new_size bytes)"
        else
            echo "Kept Original: $file (Optimization did not reduce size)"
            rm "${file}.tmp.mp4"
        fi
    else
        echo "Error converting $file"
    fi
done

echo "--- Video Optimization Complete ---"
"""

def optimize_videos_only():
    # 1. Create local script
    with open('optimize_videos.sh', 'w') as f:
        f.write(VIDEO_OPT_SCRIPT)
    
    # 2. Upload
    print("Uploading video optimization script...")
    run_interactive_command(['scp', '-i', KEY, '-o', 'StrictHostKeyChecking=no', 'optimize_videos.sh', f'{USER}@{HOST}:/root/optimize_videos.sh'])

    # 3. Run
    print("Executing video optimization on server...")
    cmd = "chmod +x /root/optimize_videos.sh && /root/optimize_videos.sh"
    run_interactive_command(['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', cmd])
    
    if os.path.exists('optimize_videos.sh'):
        os.remove('optimize_videos.sh')

def run_interactive_command(cmd_args):
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp(cmd_args[0], cmd_args)
    else:
        password_sent = False
        while True:
            try:
                data = os.read(fd, 1024)
                if not data:
                    break
                chunk = data.decode(errors='ignore')
                sys.stdout.write(chunk)
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError:
                break
        _, status = os.waitpid(pid, 0)
        return status

if __name__ == "__main__":
    optimize_videos_only()
