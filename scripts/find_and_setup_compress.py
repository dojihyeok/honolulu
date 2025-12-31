import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Robust Find and Compress
CMD = """
echo "=== Robust Search for MP4 ==="
# Search in /root/honolulu and /var/www (common deploy paths)
find /root -name "*.mp4" 2>/dev/null | head -n 5
find /var/www -name "*.mp4" 2>/dev/null | head -n 5

# Check if we found anything to compress
VIDEOS=$(find /root/honolulu -name "*.mp4" 2>/dev/null)
if [ -z "$VIDEOS" ]; then
    echo "NO_VIDEOS_FOUND"
else
    echo "VIDEOS_FOUND"
    # Create a compression script
    cat << 'EOF' > /root/compress_videos.sh
#!/bin/bash
TARGET_DIR="/root/honolulu/public/images/real"
mkdir -p "$TARGET_DIR"

# Find all mp4s
find /root/honolulu -name "*.mp4" | while read file; do
    echo "Processing $file..."
    # Check if already compressed (by size or name?) - for now just overwrite
    # Use distinct name for temp
    tmp_file="${file}.tmp.mp4"
    
    # Compress: Scale to 720p width (maintain aspect), CRF 28 for high compression, preset veryfast
    ffmpeg -y -i "$file" -vf "scale=-2:720" -vcodec libx264 -crf 28 -preset veryfast -acodec aac -b:a 128k "$tmp_file" < /dev/null
    
    if [ $? -eq 0 ]; then
        mv "$tmp_file" "$file"
        echo "Compressed $file"
    else
        echo "Failed to compress $file"
        rm "$tmp_file"
    fi
done
EOF
    chmod +x /root/compress_videos.sh
    # ./root/compress_videos.sh # Don't run yet, just setup
fi
"""

def run_ssh_command(command):
    pid, fd = pty.fork()
    if pid == 0:
        cmd_list = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', command]
        os.execvp('ssh', cmd_list)
    else:
        output = []
        password_sent = False
        timer_start = time.time()
        while True:
            if time.time() - timer_start > 30: break
            try:
                data = os.read(fd, 1024)
                if not data: break
                chunk = data.decode(errors='ignore')
                output.append(chunk)
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError: break
        os.waitpid(pid, 0)
        return "".join(output)

print(run_ssh_command(CMD))
