import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Commands to restore services
CMD = """
echo "Cleaning up confused processes..."
pm2 delete antigravity || true
# honolulu and portfolio are kept.

echo "Restoring Trydit Backend (8000)..."
cd /var/www/triedit-dev/backend
pm2 start "venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000" --name trydit-backend

echo "Restoring AuditFlow Backend (8002)..."
pm2 start "venv/bin/uvicorn main:app --host 0.0.0.0 --port 8002" --name audit-backend

echo "Restoring Trydit Frontend (3000)..."
cd /var/www/triedit-dev/frontend
# Explicitly use next binary to pass args
pm2 start ./node_modules/.bin/next --name trydit-frontend -- start -p 3000

echo "Restoring AuditFlow Frontend (3002)..."
pm2 start ./node_modules/.bin/next --name audit-frontend -- start -p 3002

pm2 save
pm2 list
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
