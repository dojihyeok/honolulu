import pty
import os
import sys
import time
import re

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'
LOCAL_FILE = 'ecosystem.config.js'
REMOTE_DEST = '/root/honolulu/ecosystem.config.js'

# Upload > Cleanup > Start
CMD = """
pm2 delete honolulu
PID=$(lsof -t -i:3005)
if [ -n "$PID" ]; then
    kill -9 $PID
fi
cd /root/honolulu
pm2 start ecosystem.config.js
pm2 save
"""

def upload_file():
    print(f"Uploading {LOCAL_FILE}...")
    scp_cmd = ['scp', '-i', KEY, '-o', 'StrictHostKeyChecking=no', LOCAL_FILE, f'{USER}@{HOST}:{REMOTE_DEST}']
    
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp('scp', scp_cmd)
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
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError:
                break
        _, status = os.waitpid(pid, 0)
        return status

def run_ssh_command(command):
    pid, fd = pty.fork()
    if pid == 0:
        cmd_list = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', command]
        os.execvp('ssh', cmd_list)
    else:
        output = []
        password_sent = False
        while True:
            if time.time() - timer_start > 15:
                break
            try:
                data = os.read(fd, 1024)
                if not data:
                    break
                chunk = data.decode(errors='ignore')
                output.append(chunk)
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError:
                break
        _, status = os.waitpid(pid, 0)
        return "".join(output)

if upload_file() == 0:
    print("\nConfig uploaded. Starting...")
    timer_start = time.time() # Used in run_ssh_command
    print(run_ssh_command(CMD))
else:
    print("Upload failed.")
