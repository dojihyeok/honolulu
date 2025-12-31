import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Install FFmpeg and Find Videos
CMD = """
echo "=== Installing FFmpeg ==="
apt-get update && apt-get install -y ffmpeg

echo "=== Finding Video Files ==="
find /root/honolulu -name "*.mp4" -exec ls -lh {} \; | sort -k 5 -h
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
            if time.time() - timer_start > 120: break # Install takes time
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
