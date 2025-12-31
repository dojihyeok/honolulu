import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Debug and switch port
CMD = """
echo "=== Checking Symlinks ==="
ls -ld /root/Antigravity
ls -ld /root/portfolio

echo "=== Checking next.config.* in /root/Antigravity ==="
ls /root/Antigravity/next.config.* || echo "No config"
cat /root/Antigravity/next.config.* 2>/dev/null

echo "=== Killing 3000 and 3009 ==="
fuser -k 3000/tcp || true
fuser -k 3009/tcp || true

echo "=== Starting Trydit on Port 3009 (Test) ==="
pm2 delete trydit-frontend || true
cd /root/Antigravity
pm2 start npm --name trydit-frontend-test -- start -- -p 3009

pm2 save
sleep 10
echo "=== Checking Title on Port 3009 ==="
curl -s http://127.0.0.1:3009 | grep -o "<title>[^<]*</title>"
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
            if time.time() - timer_start > 30: break
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
