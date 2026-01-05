import pty
import os
import sys
import time
import re

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

def run_ssh_command(command):
    print(f"Running: {command}")
    pid, fd = pty.fork()
    if pid == 0:
        cmd_list = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', command]
        os.execvp('ssh', cmd_list)
    else:
        output = []
        password_sent = False
        start_time = time.time()
        while True:
            if time.time() - start_time > 10: break
            try:
                data = os.read(fd, 1024)
                if not data: break
                chunk = data.decode(errors='ignore')
                sys.stdout.write(chunk)
                output.append(chunk)
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError: break
        _, status = os.waitpid(pid, 0)
        return "".join(output)

print("=== 1. CHECKING NGINX SITES-ENABLED ===")
run_ssh_command("ls -l /etc/nginx/sites-enabled/")
run_ssh_command("grep -r 'honolulu.dojiung.com' /etc/nginx/sites-enabled/")

print("\n=== 2. CHECKING ACTIVE PORTS ===")
# Check if 3007 is listening
run_ssh_command("lsof -i :3007")
# Check if 3003 is still listening (it should ideally be empty if we moved)
run_ssh_command("lsof -i :3003")

print("\n=== 3. CHECKING PM2 STATUS ===")
run_ssh_command("pm2 list")
