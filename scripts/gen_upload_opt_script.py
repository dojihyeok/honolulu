import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'
LOCAL_VIDEO_DIR = 'public/images/real'
REMOTE_VIDEO_DIR = '/root/honolulu/public/images/real'

# Upload and Compress
CMD = """
# 1. Create Remote Directory
ssh -i ./deploy_key.pem -o StrictHostKeyChecking=no root@49.50.139.88 "mkdir -p /root/honolulu/public/images/real"

# 2. Upload Videos (SCP)
# We upload all mp4 files from local public/images/real to remote
echo "=== Uploading Videos (This may take time) ==="
scp -i ./deploy_key.pem -o StrictHostKeyChecking=no public/images/real/*.mp4 root@49.50.139.88:/root/honolulu/public/images/real/

# 3. Trigger Compression on Server
echo "=== Triggering Server-Side Compression ==="
ssh -i ./deploy_key.pem -o StrictHostKeyChecking=no root@49.50.139.88 "bash -c '
    # Create compression script if not exists (or just run commands)
    cd /root/honolulu/public/images/real
    
    # Check if we have files
    count=\$(ls *.mp4 2>/dev/null | wc -l)
    if [ \"\$count\" -eq 0 ]; then
        echo \"No videos found after upload?\"
        exit 1
    fi
    
    echo \"Found \$count videos. Starting compression...\"
    
    for file in *.mp4; do
        if [[ \"\$file\" == *\"_opt.mp4\" ]]; then
            continue
        fi
        
        echo \"Optimizing \$file...\"
        # Target: 720p, CRF 28 (Good compression), Preset veryfast
        # We write to a temp file then overwrite
        ffmpeg -y -i \"\$file\" -vf \"scale=-2:720\" -c:v libx264 -crf 28 -preset veryfast -c:a aac -b:a 128k \"\${file}_opt.mp4\" < /dev/null
        
        if [ \$? -eq 0 ]; then
            orig_size=\$(du -h \"\$file\" | cut -f1)
            new_size=\$(du -h \"\${file}_opt.mp4\" | cut -f1)
            echo \"Compressed \$file: \$orig_size -> \$new_size\"
            mv \"\${file}_opt.mp4\" \"\$file\"
        else
            echo \"Failed to compress \$file\"
            rm -f \"\${file}_opt.mp4\"
        fi
    done
    
    echo \"All videos optimized.\"
'"
"""

# We run this locally (on the python script runner) which has access to public/images/real
# But wait, run_ssh_command runs ON THE MACHINE executing python? 
# If I use os.system or similar, it runs on the machine where python runs (Mac).
# Yes.
# But I need to handle password for SCP/SSH if keys are not auto-accepted (they are with -i key).
# The user provided a PASSWORD. 'deploy_key.pem' might be encrypted or server forces password.
# 'pty' approach is needed for password handling.

def run_local_with_password(cmd_str):
    # This function wraps the command execution with pty to handle password prompts
    # But since it's a mix of multiple commands, it's tricky.
    # We will write a python script that spawns the shell process and handles password for each interactive prompt.
    pass

# Simplified Approach:
# The main python script will execute these commands one by one using pty.
script_content = """
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
                    os.write(fd, (PASS + '\\n').encode())
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
compress_cmd = \"\"\"
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
\"\"\"
# Escape quotes for remote execution
run_command(f'ssh -i {KEY} -o StrictHostKeyChecking=no {USER}@{HOST} "bash -c \\'{compress_cmd}\\'"')
"""

print(script_content)
