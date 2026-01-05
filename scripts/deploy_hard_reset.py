import pty
import os
import sys
import time
import tarfile

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'
APP_NAME = 'honolulu'
LOCAL_ARCHIVE = 'update_v3_hard.tar.gz'
REMOTE_DIR = '/root/honolulu'

def create_archive():
    print(f"Creating archive {LOCAL_ARCHIVE} (excluding media)...")
    def filter_media(tarinfo):
        if "public/images" in tarinfo.name or "public/videos" in tarinfo.name:
            return None
        return tarinfo

    with tarfile.open(LOCAL_ARCHIVE, "w:gz") as tar:
        exclude = {'.git', '.next', 'node_modules', '.DS_Store', LOCAL_ARCHIVE, 'deploy_key.pem'}
        for item in os.listdir('.'):
            if item in exclude:
                continue
            tar.add(item, arcname=item, filter=filter_media)
    print("Archive created.")

def run_interactive_command(cmd_args):
    print(f"Executing: {' '.join(cmd_args)}")
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

def deploy():
    # 1. Create Archive
    create_archive()

    # 2. Upload
    print("Uploading archive...")
    scp_cmd = ['scp', '-i', KEY, '-o', 'StrictHostKeyChecking=no', LOCAL_ARCHIVE, f'{USER}@{HOST}:{REMOTE_DIR}/{LOCAL_ARCHIVE}']
    if run_interactive_command(scp_cmd) != 0:
        print("SCP Failed")
        return

    # 3. Aggressive Reset & Rebuild on Server
    print("Executing Hard Reset on Server...")
    cmds = [
        f"cd {REMOTE_DIR}",
        "echo '--- 1. Stopping Processes ---'",
        f"pm2 delete {APP_NAME} || true",
        "fuser -k 3003/tcp || true",  # Kill anything on 3003
        "echo '--- 2. Extracting Code ---'",
        f"tar -xzf {LOCAL_ARCHIVE}",
        "echo '--- 3. Cleaning Cache ---'",
        "rm -rf .next",
        "echo '--- 4. Installing Dependencies ---'",
        "npm install --legacy-peer-deps",
        "echo '--- 5. Building (Fresh) ---'",
        "npm run build",
        "echo '--- 6. Starting Process ---'",
        f"pm2 start npm --name '{APP_NAME}' -- start -- -p 3003",
        "pm2 save",
        "echo '--- 7. Nginx Reload ---'",
        "systemctl reload nginx",
        "echo '--- DONE ---'"
    ]
    
    remote_cmd = " && ".join(cmds)
    ssh_cmd = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', remote_cmd]
    run_interactive_command(ssh_cmd)

    # Cleanup
    if os.path.exists(LOCAL_ARCHIVE):
        os.remove(LOCAL_ARCHIVE)

if __name__ == "__main__":
    deploy()
