import pty
import os
import sys
import time

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

print("=== VERIFYING LIVE CONTENT ON PORT 3003 ===")
# We will inspect the main page bundle to see if updated CSS/JS logic is present.
# Since SSR renders HTML, we should see the class names or inline styles if they are baked in.
# We look for the inline style logic we added: 'background: transparent' for mobile dots.
run_ssh_command("curl -s http://127.0.0.1:3003 | grep -o 'background:transparent'")
run_ssh_command("curl -s http://127.0.0.1:3003 | grep -o 'backdrop-filter:none'")

print("\n=== FINAL PM2 STATUS CHECK ===")
run_ssh_command("pm2 list")
