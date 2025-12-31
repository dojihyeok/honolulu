import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'
LOCAL_FILE = 'honolulu_nginx_v2.conf'
REMOTE_FILE = '/etc/nginx/sites-enabled/honolulu.dojiung.com'

# Upload and Reload
CMD_RELOAD = "systemctl reload nginx"

def upload_file():
    print(f"Uploading {LOCAL_FILE} to {REMOTE_FILE}...")
    scp_cmd = ['scp', '-i', KEY, '-o', 'StrictHostKeyChecking=no', LOCAL_FILE, f'{USER}@{HOST}:{REMOTE_FILE}']
    
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
            except OSError: break
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
        timer_start = time.time()
        while True:
            if time.time() - timer_start > 10: break
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

if upload_file() == 0:
    print("Reloading Nginx...")
    print(run_ssh_command(CMD_RELOAD))
else:
    print("Upload failed.")
