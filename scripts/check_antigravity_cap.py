import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Check Antigravity (Capital) and Body Content
CMD = """
echo "=== Body Content on Port 3000 (First 500 chars) ==="
curl -s http://127.0.0.1:3000 | head -c 500

echo "=== Checking /root/Antigravity/src/app/ ==="
ls -F /root/Antigravity/src/app/

echo "=== Checking /root/Antigravity/package.json name ==="
cat /root/Antigravity/package.json | grep "name"

echo "=== Content of /root/Antigravity/src/app/page.tsx ==="
cat /root/Antigravity/src/app/page.tsx || echo "No page.tsx"
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
            if time.time() - timer_start > 15: break
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
