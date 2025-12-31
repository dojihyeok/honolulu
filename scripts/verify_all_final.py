import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Final Verification
CMD = """
echo "=== Checking Listeners ==="
lsof -i -P -n | grep LISTEN | grep -E "3000|3002|3003|3006|8000|8002|80|81|82|83"

echo "=== Curling Services ==="
echo "Trydit FE (3000):" && curl -I -m 5 http://127.0.0.1:3000 || echo "FAIL"
echo "AuditFlow FE (3002):" && curl -I -m 5 http://127.0.0.1:3002 || echo "FAIL"
echo "Portfolio (3003):" && curl -I -m 5 http://127.0.0.1:3003 || echo "FAIL"
echo "Honolulu (3006):" && curl -I -m 5 http://127.0.0.1:3006 || echo "FAIL"
echo "Trydit BE (8000):" && curl -I -m 5 http://127.0.0.1:8000/docs || echo "FAIL"
echo "AuditFlow BE (8002):" && curl -I -m 5 http://127.0.0.1:8002/docs || echo "FAIL"
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
            if time.time() - timer_start > 20: break
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
