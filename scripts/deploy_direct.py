import pty
import os
import sys
import time
import re
import tarfile
import subprocess

# Configuration
HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'
APP_NAME = 'honolulu'
LOCAL_ARCHIVE = 'update_v2.tar.gz'
REMOTE_DEST = f'/root/{APP_NAME}' # Assumed based on previous find_app_directory result

def create_archive():
    print(f"Creating archive {LOCAL_ARCHIVE} (excluding media)...")
    
    def filter_media(tarinfo):
        # Exclude public/images directory and its contents
        if "public/images" in tarinfo.name:
            return None
        return tarinfo

    with tarfile.open(LOCAL_ARCHIVE, "w:gz") as tar:
        # Add files/folders to exclude from top level
        exclude = {'.git', '.next', 'node_modules', '.DS_Store', LOCAL_ARCHIVE, 'deploy_key.pem', 'deploy.py', 'test_ssh.py'}
        
        for item in os.listdir('.'):
            if item in exclude:
                continue
            # apply filter to everything
            tar.add(item, arcname=item, filter=filter_media)
    print("Archive created.")

def run_interactive_command(cmd_args, password):
    """
    Runs a command that might ask for a password using pty.
    """
    print(f"Executing: {' '.join(cmd_args)}")
    
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp(cmd_args[0], cmd_args)
    else:
        output = []
        password_sent = False
        
        while True:
            try:
                data = os.read(fd, 1024)
                if not data:
                    break
                chunk = data.decode(errors='ignore')
                sys.stdout.write(chunk) # Stream to stdout for user visibility
                sys.stdout.flush()
                output.append(chunk)
                
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (password + '\n').encode())
                    password_sent = True
            except OSError:
                break
        
        _, status = os.waitpid(pid, 0)
        return status, "".join(output)

def deploy():
    # 1. Archive
    create_archive()
    
    # 2. Upload
    print(f"Uploading {LOCAL_ARCHIVE} to {HOST}...")
    # scp -o StrictHostKeyChecking=no -i KEY source user@host:/path
    scp_cmd = [
        'scp', '-i', KEY, 
        '-o', 'StrictHostKeyChecking=no',
        LOCAL_ARCHIVE, 
        f'{USER}@{HOST}:{REMOTE_DEST}/{LOCAL_ARCHIVE}'
    ]
    status, _ = run_interactive_command(scp_cmd, PASS)
    if status != 0:
        print("SCP Failed")
        return

    # 3. Extract and Build
    print("Extracting and building on server...")
    remote_cmds = [
        f"cd {REMOTE_DEST}",
        f"tar -xzf {LOCAL_ARCHIVE}",
        "npm install --legacy-peer-deps",
        "npm run build",
        f"pm2 restart {APP_NAME}"
    ]
    
    combined_cmd = " && ".join(remote_cmds)
    ssh_cmd = [
        'ssh', '-i', KEY,
        '-o', 'StrictHostKeyChecking=no',
        f'{USER}@{HOST}',
        combined_cmd
    ]
    
    status, _ = run_interactive_command(ssh_cmd, PASS)
    
    # Cleanup local
    if os.path.exists(LOCAL_ARCHIVE):
        os.remove(LOCAL_ARCHIVE)
        
    print("\n--- Direct Deployment Complete ---")

if __name__ == "__main__":
    deploy()
