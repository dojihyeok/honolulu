import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Check logs and hardcode port
CMD = """
echo "=== Last logs for audit-frontend ==="
pm2 logs audit-frontend --lines 20 --nostream

echo "=== Modifying package.json in frontend_audit ==="
cd /var/www/triedit-dev/frontend_audit
# Use sed to replace "next dev" with "next dev -p 3002"
sed -i 's/"dev": "next dev"/"dev": "next dev -p 3002"/' package.json

echo "Restarting Audit Frontend..."
pm2 restart audit-frontend

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
