import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Switch Trydit source
CMD = """
echo "=== Stopping Incorrect Trydit Frontend ==="
pm2 delete trydit-frontend || true

echo "=== Starting Correct Trydit Frontend (from /root/antigravity) ==="
cd /root/antigravity
# Check if we need to install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Try to run dev on port 3000
# Note: package.json script might not accept -p, so passing it to next dev directly via -- -p
pm2 start npm --name trydit-frontend -- run dev -- -p 3000

pm2 save
sleep 10

echo "=== Checking Title on Port 3000 ==="
curl -s http://127.0.0.1:3000 | grep -o "<title>[^<]*</title>"
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
            if time.time() - timer_start > 60: break
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
