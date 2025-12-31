import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Check package names and logs
CMD = """
echo "=== /root/antigravity package.json ==="
cat /root/antigravity/package.json | grep -E '"name"|"scripts"' -A 5

echo "=== /root/Antigravity package.json ==="
cat /root/Antigravity/package.json | grep -E '"name"|"scripts"' -A 5

echo "=== /root/portfolio package.json ==="
cat /root/portfolio/package.json | grep -E '"name"|"scripts"' -A 5

echo "=== Checking Audit Logs for Path ==="
head -n 10 /root/.pm2/logs/audit-backend-out.log
head -n 10 /root/.pm2/logs/audit-backend-error.log

echo "=== Searching other locations ==="
ls -F /var/www/
ls -F /home/
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
