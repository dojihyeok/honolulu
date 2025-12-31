import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Files to upload
FILES = ['package.json', 'ecosystem.config.js']
DEST_DIR = '/root/honolulu'

# Commands
CMD_START = """
pm2 delete honolulu
cd /root/honolulu
pm2 start ecosystem.config.js
pm2 save
"""

def upload_file(local_path):
    remote = f'{USER}@{HOST}:{DEST_DIR}/{local_path}'
    print(f"Uploading {local_path}...")
    scp_cmd = ['scp', '-i', KEY, '-o', 'StrictHostKeyChecking=no', local_path, remote]
    
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp('scp', scp_cmd)
    else:
        password_sent = False
        while True:
            try:
                data = os.read(fd, 1024)
                if not data: break
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
                if not data: break
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

for f in FILES:
    upload_file(f)

print("Restarting on 3006...")
print(run_ssh_command(CMD_START))
