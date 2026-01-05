import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Command to resurrect services one by one
CMD = """
set -e

echo "=== 1. Starting Honolulu (Port 3003) ==="
if [ -d "/root/honolulu" ]; then
    cd /root/honolulu
    # Ensure dependencies are installed (just in case)
    # npm install --legacy-peer-deps
    # Explicitly start on 3003 using PM2
    pm2 delete honolulu || true
    pm2 start npm --name honolulu -- start -- -p 3003
    echo "Honolulu started."
else
    echo "ERROR: /root/honolulu not found"
fi

echo "=== 2. Starting Trydit (Port 3000) ==="
if [ -d "/root/trydit" ]; then
    cd /root/trydit
    pm2 delete trydit || true
    pm2 start npm --name trydit -- start -- -p 3000
    echo "Trydit started."
elif [ -d "/root/antigravity" ]; then # Fallback
    cd /root/antigravity
    pm2 delete trydit-frontend || true
    pm2 start npm --name trydit-frontend -- start -- -p 3000
    echo "Trydit (antigravity) started."
else
    echo "WARNING: Trydit directory not found"
fi

echo "=== 3. Starting AudiFlow (Port 3001) ==="
if [ -d "/root/audiflow" ]; then
    cd /root/audiflow
    pm2 delete audiflow || true
    pm2 start npm --name audiflow -- start -- -p 3001
    echo "AudiFlow started."
else
    echo "WARNING: /root/audiflow not found"
fi

echo "=== 4. Starting Portfolio (Port 3002) ==="
if [ -d "/root/portfolio" ]; then
    cd /root/portfolio
    pm2 delete portfolio || true
    pm2 start npm --name portfolio -- start -- -p 3002
    echo "Portfolio started."
else
    echo "WARNING: /root/portfolio not found"
fi

echo "=== Saving PM2 List ==="
pm2 save

echo "=== Current PM2 Proceses ==="
pm2 list
"""

def run_ssh_command(command):
    print(f"Executing Remote Commands...")
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
                sys.stdout.write(chunk)
                output.append(chunk)
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError: break
        _, status = os.waitpid(pid, 0)
        return "".join(output)

if __name__ == "__main__":
    run_ssh_command(CMD)
