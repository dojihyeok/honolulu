import pty
import os
import sys
import time
import tarfile

# Configuration
HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'
APP_NAME = 'honolulu'
LOCAL_ARCHIVE = 'full_update.tar.gz'
REMOTE_DEST = f'/root/{APP_NAME}'

# 1. Create Archive (Exclude Media + Build Artifacts)
def create_archive():
    print("Creating clean archive...")
    def filter_files(tarinfo):
        # Exclude large media
        if "public/images" in tarinfo.name: return None
        return tarinfo

    with tarfile.open(LOCAL_ARCHIVE, "w:gz") as tar:
        # Top level excludes
        exclude = {'.git', '.next', 'node_modules', '.DS_Store', LOCAL_ARCHIVE, 'deploy_key.pem', 'deploy.py', 'test_ssh.py', '.venv'}
        for item in os.listdir('.'):
            if item in exclude: continue
            tar.add(item, arcname=item, filter=filter_files)
    print("Archive created.")

# 2. Upload
def upload_archive():
    print("Uploading archive...")
    scp_cmd = ['scp', '-i', KEY, '-o', 'StrictHostKeyChecking=no', LOCAL_ARCHIVE, f'{USER}@{HOST}:{REMOTE_DEST}/{LOCAL_ARCHIVE}']
    pid, fd = pty.fork()
    if pid == 0: os.execvp('scp', scp_cmd)
    else:
        password_sent = False
        while True:
            try:
                data = os.read(fd, 1024)
                if not data: break
                chunk = data.decode(errors='ignore')
                sys.stdout.write(chunk)
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError: break
        os.waitpid(pid, 0)

# 3. Clean Build & Restart
def remote_build():
    print("Running Clean Build on Server...")
    full_cmd = f"""
echo "=== Step 1: Kill ALL Node/Next processes ==="
pkill -f node || true
pkill -f next || true
pkill -f pm2 || true

echo "=== Step 2: Kill ANY process on ports other than SSH/Nginx ==="
# Kill anything on 3000-3010 just to be sure
fuser -k 3000/tcp || true
fuser -k 3001/tcp || true
fuser -k 3002/tcp || true
fuser -k 3003/tcp || true
fuser -k 3004/tcp || true
fuser -k 3005/tcp || true
fuser -k 3006/tcp || true

echo "=== Step 3: Resurrect PM2 & Start Only Allowed Services ==="
# 1. Trydit (Port 3000)
if [ -d "/root/trydit" ]; then
    echo "Starting Trydit on 3000..."
    cd /root/trydit && npm install && npm run build && pm2 start npm --name trydit -- start -- -p 3000
elif [ -d "/root/antigravity" ]; then # Fallback path seen in logs
    echo "Starting Trydit (antigravity) on 3000..."
    cd /root/antigravity && npm install && npm run build && pm2 start npm --name trydit -- start -- -p 3000
fi

# 2. AudiFlow (Port 3001) - Check directory existence
if [ -d "/root/audiflow" ]; then
    echo "Starting AudiFlow on 3001..."
    cd /root/audiflow && pm2 start npm --name audiflow -- start -- -p 3001
fi

# 3. Portfolio (Port 3002) - Check directory existence
if [ -d "/root/portfolio" ]; then
    echo "Starting Portfolio on 3002..."
    cd /root/portfolio && pm2 start npm --name portfolio -- start -- -p 3002
fi

# 4. Honolulu (Port 3003) - Our target
if [ -d "/root/honolulu" ]; then
    echo "Starting Honolulu on 3003..."
    cd /root/honolulu && npm install --legacy-peer-deps && npm run build && pm2 start npm --name honolulu -- start -- -p 3003
fi

pm2 save
echo "=== DONE: Only 3000, 3001, 3002, 3003 should be active ==="
"""
    
    ssh_cmd = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', full_cmd]
    pid, fd = pty.fork()
    if pid == 0: os.execvp('ssh', ssh_cmd)
    else:
        password_sent = False
        while True:
            try:
                data = os.read(fd, 1024)
                if not data: break
                chunk = data.decode(errors='ignore')
                sys.stdout.write(chunk)
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError: break
        os.waitpid(pid, 0)

if __name__ == "__main__":
    create_archive()
    upload_archive()
    remote_build()
    if os.path.exists(LOCAL_ARCHIVE): os.remove(LOCAL_ARCHIVE)
