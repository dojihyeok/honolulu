import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Check content titles to identify services
CMD = """
echo "=== Title on Port 3000 ==="
curl -s http://127.0.0.1:3000 | grep -o "<title>[^<]*</title>"

echo "=== Title on Port 3002 ==="
curl -s http://127.0.0.1:3002 | grep -o "<title>[^<]*</title>"

echo "=== Title on Port 3003 ==="
curl -s http://127.0.0.1:3003 | grep -o "<title>[^<]*</title>"

echo "=== Title on Port 3006 ==="
curl -s http://127.0.0.1:3006 | grep -o "<title>[^<]*</title>"

echo "=== Checking /root/antigravity/src/app/layout.tsx ==="
grep "title" /root/antigravity/src/app/layout.tsx

echo "=== Checking /root/Antigravity/src/app/layout.tsx ==="
grep "title" /root/Antigravity/src/app/layout.tsx

echo "=== Checking /var/www/triedit-dev/frontend/src/app/layout.tsx ==="
grep "title" /var/www/triedit-dev/frontend/src/app/layout.tsx
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
