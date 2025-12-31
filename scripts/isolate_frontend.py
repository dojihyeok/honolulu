import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Isolate Audit Frontend
CMD = """
echo "Stopping Audit Frontend..."
pm2 delete audit-frontend || true

echo "Creating isolated directory frontend_audit..."
cd /var/www/triedit-dev
# Copy source but exclude .next and node_modules
rsync -av --exclude '.next' --exclude 'node_modules' frontend/ frontend_audit/

echo "Linking node_modules..."
cd frontend_audit
ln -s ../frontend/node_modules node_modules

echo "Starting Audit Frontend on Port 3002..."
# Force port 3002
pm2 start npm --name audit-frontend --env PORT=3002 -- run dev

pm2 save
sleep 10
echo "Checking Ports..."
lsof -i -P -n | grep LISTEN
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
            if time.time() - timer_start > 60: break # Increased timeout for rsync
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
