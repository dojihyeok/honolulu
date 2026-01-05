import pty
import os
import sys
import time
import re

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Command to check file sizes of top 10 largest mp4 files and some jpgs
CMD_CHECK = """
echo "--- Checking Video Sizes (Top 10 Largest) ---"
find /root/honolulu/public/images/real -name "*.mp4" -exec ls -lh {} + | sort -k 5 -rh | head -n 10

echo "\n--- Checking Image Sizes (Sample 10) ---"
find /root/honolulu/public/images/real -name "*.jpg" -exec ls -lh {} + | head -n 10

echo "\n--- Checking Resolution of a Video (requires ffmpeg installed) ---"
if command -v ffmpeg &> /dev/null; then
    find /root/honolulu/public/images/real -name "*.mp4" | head -n 1 | xargs -I {} ffmpeg -i {} 2>&1 | grep Stream | grep Video
else
    echo "ffmpeg not installed or not found."
fi
"""

def check_server_media():
    pid, fd = pty.fork()
    if pid == 0:
        cmd_list = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', CMD_CHECK]
        os.execvp('ssh', cmd_list)
    else:
        output = []
        password_sent = False
        while True:
            try:
                data = os.read(fd, 1024)
                if not data:
                    break
                chunk = data.decode(errors='ignore')
                sys.stdout.write(chunk)
                output.append(chunk)
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError:
                break
        _, status = os.waitpid(pid, 0)
        return "".join(output)

if __name__ == "__main__":
    check_server_media()
