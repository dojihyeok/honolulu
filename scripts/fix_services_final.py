import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Fix Portfolio and Audit Lock
CMD = """
echo "=== Fixing Portfolio (Port 3003) ==="
pm2 delete portfolio || true
cd /root/portfolio
# Start on 3003 explicitly
pm2 start npm --name portfolio -- start -- -p 3003

echo "=== Fixing Audit Frontend Lock (Port 3002) ==="
pm2 delete audit-frontend || true
# Kill anything on 3002
fuser -k 3002/tcp || true
# Remove lock
rm -rf /var/www/triedit-dev/frontend_audit/.next/dev/lock
# Start again
cd /var/www/triedit-dev/frontend_audit
pm2 start npm --name audit-frontend --env PORT=3002 -- run dev

pm2 save
sleep 10
echo "=== Checking Ports ==="
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
