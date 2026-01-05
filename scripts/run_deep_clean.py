import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Deep Clean & Restart Script
# 1. Stop all PM2 processes related to honolulu
# 2. Kill any lingering node processes on ports 3000-3006
# 3. Verify ports are free
# 4. Start Honolulu explicitly on port 3003
# 5. Reload Nginx
SERVER_CLEAN_SCRIPT = """
set -e

echo "--- 1. Stopping & Deleting PM2 process ---"
pm2 delete honolulu || echo "Honolulu not in PM2, skipping delete"

echo "--- 2. Killing lingering processes on ports 3000-3006 ---"
# Kill anything listening on these ports
fuser -k 3000/tcp || true
fuser -k 3001/tcp || true
fuser -k 3002/tcp || true
fuser -k 3003/tcp || true
fuser -k 3004/tcp || true
fuser -k 3005/tcp || true
fuser -k 3006/tcp || true

echo "--- 3. Verifying ports are free ---"
netstat -tulpn | grep ':300' || echo "Ports verified clean (no output expected above for 300[0-6])"

echo "--- 4. Starting Honolulu on Port 3003 ---"
cd /root/honolulu
# Ensure we are using the latest code
# (Assuming upload happened previously, but let's reinstall to be safe?)
# npm install --legacy-peer-deps

echo "Building..."
npm run build

echo "Starting via PM2..."
# Explicitly pass PORT=3003 to next start
pm2 start npm --name "honolulu" -- start -- -p 3003
pm2 save

echo "--- 5. Nginx Configuration Check ---"
# Ensure nginx points to 3003
NGINX_CONF="/etc/nginx/sites-available/honolulu"
if [ ! -f "$NGINX_CONF" ]; then
    NGINX_CONF="/etc/nginx/sites-available/honolulu.dojiung.com"
fi

if [ -f "$NGINX_CONF" ]; then
    echo "Updating Nginx config to 3003..."
    sed -i 's/localhost:[0-9]*/localhost:3003/g' "$NGINX_CONF"
    nginx -t
    systemctl reload nginx
    echo "Nginx reloaded."
else
    echo "Warning: Nginx config file not found at expected paths. Please check manually."
fi

echo "--- DEEP CLEAN DEPLOY COMPLETE ---"
"""

def run_deep_clean():
    # 1. Write script locally
    with open('deep_clean.sh', 'w') as f:
        f.write(SERVER_CLEAN_SCRIPT)
    
    # 2. Upload
    print("Uploading deep clean script...")
    run_interactive_command(['scp', '-i', KEY, '-o', 'StrictHostKeyChecking=no', 'deep_clean.sh', f'{USER}@{HOST}:/root/deep_clean.sh'])

    # 3. Run
    print("Executing Deep Clean on server...")
    cmd = "chmod +x /root/deep_clean.sh && /root/deep_clean.sh"
    run_interactive_command(['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', cmd])
    
    if os.path.exists('deep_clean.sh'):
        os.remove('deep_clean.sh')

def run_interactive_command(cmd_args):
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp(cmd_args[0], cmd_args)
    else:
        password_sent = False
        while True:
            try:
                data = os.read(fd, 1024)
                if not data:
                    break
                chunk = data.decode(errors='ignore')
                sys.stdout.write(chunk)
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError:
                break
        _, status = os.waitpid(pid, 0)
        return status

if __name__ == "__main__":
    run_deep_clean()
