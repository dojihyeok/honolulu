import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Check progress:
# 1. Count processed files (modified in last 10 mins)
# 2. Check running processes (ffmpeg/mogrify)
CMD_CHECK_PROGRESS = """
echo "--- Process Check ---"
pgrep -a ffmpeg || echo "No ffmpeg running"
pgrep -a mogrify || echo "No mogrify running"

echo "\n--- Recent File Updates (Last 10 mins) ---"
find /root/honolulu/public/images/real -mmin -10 | wc -l 
echo "files updated."

echo "\n--- Total Files to Process ---"
# Count jpg/png/mp4
find /root/honolulu/public/images/real -name "*.jpg" -o -name "*.png" -o -name "*.mp4" | wc -l
"""

def check_progress():
    pid, fd = pty.fork()
    if pid == 0:
        cmd_list = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', CMD_CHECK_PROGRESS]
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
    check_progress()
