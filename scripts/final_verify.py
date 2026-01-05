import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

def run_ssh_command(command):
    #print(f"Running: {command}")
    pid, fd = pty.fork()
    if pid == 0:
        cmd_list = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', command]
        os.execvp('ssh', cmd_list)
    else:
        output = []
        password_sent = False
        start_time = time.time()
        while True:
            if time.time() - start_time > 15: break
            try:
                data = os.read(fd, 4096)
                if not data: break
                chunk = data.decode(errors='ignore')
                sys.stdout.write(chunk)
                output.append(chunk)
                if not password_sent and ("password:" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError: break
        _, status = os.waitpid(pid, 0)
        return "".join(output)

print("=== 1. CHECKING VERSION TAG ===")
# Check for v0.05
version_html = run_ssh_command("curl -s http://127.0.0.1:3003 | grep 'v0.05'")
print(f"Version check output: {version_html}")

print("\n=== 2. CHECKING IMAGE DIMENSIONS ===")
# Check specific images
run_ssh_command("file /root/honolulu/public/images/real/20251219_101102.jpg")
run_ssh_command("file /root/honolulu/public/images/real/20251219_193047.jpg")
