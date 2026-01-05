import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Optimization Script to be run on server
# 1. Install ffmpeg if missing
# 2. Iterate all jpg/png in /root/honolulu/public/images/real -> Resize to max 1920px width/height
# 3. Iterate all mp4 -> Convert to 720p CRF 28
SERVER_SCRIPT = """
set -e

# 1. Install FFmpeg and ImageMagick if needed
if ! command -v ffmpeg &> /dev/null; then
    echo "Installing FFmpeg..."
    apt-get update && apt-get install -y ffmpeg
fi

if ! command -v mogrify &> /dev/null; then
    echo "Installing ImageMagick..."
    apt-get update && apt-get install -y imagemagick
fi

cd /root/honolulu/public/images/real

echo "--- Optimizing Images (Max 1920px, 80% quality) ---"
# Use mogrify for in-place batch processing. 
# Only process huge files (larger than 500kb) to save time/quality on already small ones? 
# Or just enforcing max dimension is safer.
find . -iname "*.jpg" -o -iname "*.png" -o -iname "*.jpeg" | xargs -P 4 -I {} mogrify -resize "1920x1920>" -quality 80 {}

echo "--- Optimizing Videos (720p, CRF 28) ---"
# We need to process via temp file then overwrite
find . -name "*.mp4" | while read file; do
    # Check if already optimized (skip if filename contains _opt, specific logic needed? 
    # Or just check file size/bitrate? simpler to just re-encode safely to tmp)
    
    echo "Processing $file..."
    ffmpeg -y -i "$file" -vf "scale='min(1280,iw)':-2" -vcodec libx264 -crf 28 -preset fast -acodec aac -b:a 128k "${file}.tmp.mp4" < /dev/null
    
    if [ -f "${file}.tmp.mp4" ]; then
        mv "${file}.tmp.mp4" "$file"
        echo "Done: $file"
    else
        echo "Failed to convert $file"
    fi
done

echo "--- Optimization Complete ---"
"""

def optimize_media():
    print("Starting server-side media optimization...")
    pid, fd = pty.fork()
    if pid == 0:
        # Pass the script as a single command string properly quoted? 
        # Easier to upload a script file and run it.
        # But here we stream it via stdin or just complex command.
        # Let's save to local file 'optimize.sh', upload, then run.
        os._exit(0) # Should be handled by main
    return

def run_optimization():
    # 1. Create local Shell script
    with open('optimize_server.sh', 'w') as f:
        f.write(SERVER_SCRIPT)
    
    # 2. Upload
    print("Uploading optimization script...")
    scp_cmd = ['scp', '-i', KEY, '-o', 'StrictHostKeyChecking=no', 'optimize_server.sh', f'{USER}@{HOST}:/root/optimize_server.sh']
    if os.system(' '.join(scp_cmd)) != 0:
        print("SCP failed. Assuming permission issue or manual pass needed.")
        # Try pty version of scp if needed, but let's try direct first since we successfully did before?
        # Actually previous tools used pty for scp. I should stick to that pattern if non-interactive scp fails.
    
    # Let's use the pty pattern for SCP again to be safe with password
    upload_status = run_interactive_command(['scp', '-i', KEY, '-o', 'StrictHostKeyChecking=no', 'optimize_server.sh', f'{USER}@{HOST}:/root/optimize_server.sh'])
    
    if upload_status != 0:
        print("Upload failed.")
        return

    # 3. Run
    print("Executing optimization script on server (This will take a while)...")
    cmd = "chmod +x /root/optimize_server.sh && /root/optimize_server.sh"
    run_interactive_command(['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', cmd])
    
    # Cleanup
    if os.path.exists('optimize_server.sh'):
        os.remove('optimize_server.sh')

def run_interactive_command(cmd_args):
    import pty
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
    run_optimization()
