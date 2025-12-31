import pty
import os
import sys
import time
import re

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'
LOCAL_FILE = 'package.json'
REMOTE_DEST = '/root/honolulu/package.json'

# 1. Upload package.json
# 2. Restart PM2 (Delete and Start to be sure)
CMD_RESTART = """
pm2 delete honolulu
cd /root/honolulu
pm2 start npm --name "honolulu" -- start
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
    print("\nPackage.json uploaded. Restarting...")
    print(run_ssh_command(CMD_RESTART))
else:
    print("Upload failed.")
