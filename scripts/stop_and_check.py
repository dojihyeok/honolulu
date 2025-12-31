import pty
import os
import sys
import time
import re

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Stop, Check, Start
CMD = """
echo "Stopping honolulu..."
pm2 stop honolulu
sleep 2
PID=$(lsof -t -i:3004)
if [ -z "$PID" ]; then
    echo "Port 3004 is free."
else
    echo "Port 3004 is STUCK by PID $PID. Killing..."
    kill -9 $PID
fi
echo "Starting honolulu..."
pm2 start honolulu
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
            if time.time() - timer_start > 20: # Longer timeout for stop/start
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
