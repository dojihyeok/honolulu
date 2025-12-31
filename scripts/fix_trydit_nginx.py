import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Update Nginx and Finalize Trydit
CMD = """
echo "=== Updating Nginx Config ==="
sed -i 's/127.0.0.1:3000/127.0.0.1:3009/g' /etc/nginx/sites-enabled/trydit.dojiung.com || echo "Failed to sed trydit"
sed -i 's/127.0.0.1:3000/127.0.0.1:3009/g' /etc/nginx/sites-enabled/triedit.dojiung.com || echo "Failed to sed triedit"

echo "=== Reloading Nginx ==="
nginx -t && systemctl reload nginx

echo "=== Finalizing PM2 Process ==="
pm2 delete trydit-frontend-test || true
pm2 delete trydit-frontend || true
cd /root/Antigravity
pm2 start npm --name trydit-frontend -- start -- -p 3009
pm2 save

sleep 5
echo "=== Verifying Domain Access ==="
curl -s -H "Host: trydit.dojiung.com" http://127.0.0.1:80 | grep -o "<title>[^<]*</title>"
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
