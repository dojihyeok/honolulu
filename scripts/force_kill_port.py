import pty
import os
import sys
import time
import re

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Command to:
# 1. Check who owns 3004 (netstat or lsof)
# 2. Kill it
# 3. Verify it's gone
# 4. Restart PM2
# Note: Ubuntu usually has 'ss' or 'netstat'.
CMD = """
PID=$(lsof -t -i:3004)
if [ -z "$PID" ]; then
    echo "No process found on port 3004."
else
    echo "Killing process $PID on port 3004..."
    kill -9 $PID
fi
sleep 1
pm2 restart honolulu
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
            if time.time() - timer_start > 15:
                break
            try:
                data = os.read(fd, 1024)
                if not data:
                    break
                chunk = data.decode(errors='ignore')
                output.append(chunk)
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError:
                break
        _, status = os.waitpid(pid, 0)
        return "".join(output)

print(run_ssh_command(CMD))
