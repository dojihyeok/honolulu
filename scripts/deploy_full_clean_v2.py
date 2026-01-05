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



def run_interactive_command(cmd_args):
    print(f"Executing: {' '.join(cmd_args)}")
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp(cmd_args[0], cmd_args)
    else:
        output = []
        password_sent = False
        timer_start = time.time()
        while True:
            # Increase timeout to 5 minutes for heavy builds
            if time.time() - timer_start > 300: break 
            try:
                data = os.read(fd, 1024)
                if not data: break
                chunk = data.decode(errors='ignore')
                sys.stdout.write(chunk)
                output.append(chunk)
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError: break
        _, status = os.waitpid(pid, 0)
        return status

def deploy():
    create_archive()
    
    # 1. Upload
    print("Uploading...")
    scp_cmd = ['scp', '-i', KEY, '-o', 'StrictHostKeyChecking=no', LOCAL_ARCHIVE, f'{USER}@{HOST}:{REMOTE_DEST}/{LOCAL_ARCHIVE}']
    run_interactive_command(scp_cmd)

    # 2. Kill Everything & Clean Build
    print("Executing Remote Clean & Build...")
    # We use a single string for the remote command to ensure state persistency across steps if needed, 
    # but separate critical steps with && to fail fast or ; to continue.
    
    remote_script = """
    set -x
    echo "--- KILLING OLD PROCESSES ---"
    pm2 delete all || true
    pkill -f node || true
    pkill -f next || true
    
    echo "--- ENSURING PORTS ARE FREE ---"
    fuser -k 3000/tcp || true
    fuser -k 3001/tcp || true
    fuser -k 3002/tcp || true
    fuser -k 3003/tcp || true
    fuser -k 3006/tcp || true

    echo "--- RESTORING SERVICES ---"
    
    # 1. Trydit (3000)
    if [ -d "/root/antigravity" ]; then
        echo "Starting Trydit..."
        cd /root/antigravity && pm2 start npm --name trydit -- start -- -p 3000
    fi

    # 4. Honolulu (3003) - Rebuild First
    echo "Building Honolulu..."
    cd /root/honolulu
    tar -xzf full_cleanup.tar.gz
    npm install --legacy-peer-deps
    npm run build
    pm2 start npm --name honolulu -- start -- -p 3003
    
    pm2 save
    echo "--- DEPLOYMENT FINISHED ---"
    """
    
    ssh_cmd = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', remote_script]
    run_interactive_command(ssh_cmd)
    
    if os.path.exists(LOCAL_ARCHIVE): os.remove(LOCAL_ARCHIVE)

if __name__ == "__main__":
    deploy()
