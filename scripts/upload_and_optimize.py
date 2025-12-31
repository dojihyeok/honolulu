
import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

def run_command(cmd):
    print(f"Running: {cmd}")
    pid, fd = pty.fork()
    if pid == 0:
        # Split command correctly for execvp? No, let's use sh -c
        os.execvp('sh', ['sh', '-c', cmd])
    else:
        password_sent = False
        timer_start = time.time()
        last_data = time.time()
        while True:
            # if time.time() - last_data > 300: break # 5 min timeout for upload
            try:
                data = os.read(fd, 1024)
                if not data: break
                chunk = data.decode(errors='ignore')
                sys.stdout.write(chunk)
                last_data = time.time()
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    # password_sent = True # Don't set to True globally if multiple prompts, but mostly one per ssh
                    # Actually scp might prompt, then ssh might prompt.
                    # Simple hack: Always send password if prompted.
            except OSError: break
        os.waitpid(pid, 0)

# 1. Create Dir
run_command(f'ssh -i {KEY} -o StrictHostKeyChecking=no {USER}@{HOST} "mkdir -p /root/honolulu/public/images/real"')

# 2. Upload (SCP)
# Need to use glob in python or shell? Shell is fine.
run_command(f'scp -i {KEY} -o StrictHostKeyChecking=no public/images/real/*.mp4 {USER}@{HOST}:/root/honolulu/public/images/real/')

# 3. Compress
compress_cmd = """
    cd /root/honolulu/public/images/real
    count=$(ls *.mp4 2>/dev/null | wc -l)
    if [ "$count" -eq 0 ]; then echo "No videos"; exit 0; fi
    echo "Found $count videos. Optimizing..."
    for file in *.mp4; do
        if [[ "$file" == *"_opt.mp4" ]]; then continue; fi
        ffmpeg -y -i "$file" -vf "scale=-2:720" -c:v libx264 -crf 28 -preset veryfast -c:a aac -b:a 128k "${file}_opt.mp4" < /dev/null
        if [ $? -eq 0 ]; then
            mv "${file}_opt.mp4" "$file"
            echo "Compressed $file"
        fi
    done
"""
# Escape quotes for remote execution
run_command(f'ssh -i {KEY} -o StrictHostKeyChecking=no {USER}@{HOST} "bash -c \'{compress_cmd}\'"')

