import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Restart Portfolio and Antigravity
# Assuming standard start commands based on folder names or ecosystem files
CMD = """
echo "Restoring Portfolio..."
cd /root/portfolio
if [ -f ecosystem.config.js ]; then
    pm2 start ecosystem.config.js
else
    pm2 start npm --name "portfolio" -- start
fi

echo "Restoring Antigravity..."
cd /root/antigravity
if [ -f ecosystem.config.js ]; then
    pm2 start ecosystem.config.js
else
    # Antigravity likely needs specific start command if no ecosystem
    # Check package.json
    pm2 start npm --name "antigravity" -- start
fi

echo "Checking for Trydit/AudiFlow scripts..."
# Based on ls output: setup_auditflow.sh, setup_triedit.sh exist.
# Checking active PM2 list to see what's up
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
