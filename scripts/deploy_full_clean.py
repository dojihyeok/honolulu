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
    cmds = [
        f"cd {REMOTE_DEST}",
        "pm2 delete honolulu || true",  # Stop process (ignore error if not exists)
        "fuser -k 3006/tcp || true",    # Kill any process on 3006 explicitly
        f"tar -xzf {LOCAL_ARCHIVE}",    # Overwrite source
        "rm -rf .next",                 # Nuke old build
        "npm install --legacy-peer-deps",
        "npm run build",                # Fresh build
        "pm2 start ecosystem.config.js",
        "pm2 save"
    ]
    
    full_cmd = " && ".join(cmds)
    
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
