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
LOCAL_ARCHIVE = 'update_v4_hard.tar.gz'
REMOTE_DEST = f'/root/{APP_NAME}'

def create_archive():
    print(f"Creating archive {LOCAL_ARCHIVE} (excluding media)...")
    def filter_media(tarinfo):
        if "public/images" in tarinfo.name: return None
        return tarinfo
    with tarfile.open(LOCAL_ARCHIVE, "w:gz") as tar:
        exclude = {'.git', '.next', 'node_modules', '.DS_Store', LOCAL_ARCHIVE, 'deploy_key.pem', 'deploy.py', 'test_ssh.py'}
        for item in os.listdir('.'):
            if item in exclude: continue
            tar.add(item, arcname=item, filter=filter_media)
    print("Archive created.")

def run_interactive_command(cmd_args):
    print(f"Executing: {' '.join(cmd_args)}")
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp(cmd_args[0], cmd_args)
    else:
        output = []
        password_sent = False
        start_time = time.time()
        while True:
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
    
    # Upload Code
    scp_cmd = ['scp', '-i', KEY, '-o', 'StrictHostKeyChecking=no', LOCAL_ARCHIVE, f'{USER}@{HOST}:{REMOTE_DEST}/{LOCAL_ARCHIVE}']
    run_interactive_command(scp_cmd)
    
    # Upload Nginx Config
    scp_nginx = ['scp', '-i', KEY, '-o', 'StrictHostKeyChecking=no', 'honolulu_nginx.conf', f'{USER}@{HOST}:/etc/nginx/sites-available/honolulu']
    run_interactive_command(scp_nginx)

    # Build & Restart App & Restart Nginx
    remote_cmds = [
        f"cd {REMOTE_DEST}",
        f"tar -xzf {LOCAL_ARCHIVE}",
        "npm install --legacy-peer-deps",
        # HARD RESET: Delete .next cache to ensure fresh build
        "echo 'Removing .next cache for clean build...'",
        "rm -rf .next", 
        "npm run build",
        # Stop old instances if any
        "pm2 delete honolulu || true",
        # Aggressive Port Cleanup (3003, 3005, 3006)
        "for P in 3003 3005 3006; do PID=$(lsof -t -i:$P); [ ! -z \"$PID\" ] && kill -9 $PID; done || true",
        # Start new instance on 3003
        "pm2 start ecosystem.config.js",
        "pm2 save",
        # Reload Nginx
        "nginx -t && systemctl restart nginx"
    ]
    ssh_cmd = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', " && ".join(remote_cmds)]
    run_interactive_command(ssh_cmd)

    if os.path.exists(LOCAL_ARCHIVE): os.remove(LOCAL_ARCHIVE)

if __name__ == "__main__":
    deploy()
