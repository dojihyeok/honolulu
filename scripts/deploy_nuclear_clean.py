import os
import sys
import time
import subprocess
import pty

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'
REMOTE_DIR = '/root/honolulu'
ARCHIVE_NAME = 'honolulu_nuclear.tar.gz'

def run_local(command):
    print(f"[LOCAL] {command}")
    return subprocess.check_output(command, shell=True).decode()

def run_ssh_command(command, use_pty=False):
    print(f"[REMOTE] {command}")
    if use_pty:
        pid, fd = pty.fork()
        if pid == 0:
            cmd_list = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', command]
            os.execvp('ssh', cmd_list)
        else:
            output = []
            password_sent = False
            start_time = time.time()
            while True:
                if time.time() - start_time > 300: break # Long timeout for install/build
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
            return "".join(output)
    else:
        # Non-PTY simpler execution for simple commands if needed, but keeping PTY for consistency with password
        return run_ssh_command(command, use_pty=True)

def upload_file(local_path, remote_path):
    print(f"[UPLOAD] {local_path} -> {remote_path}")
    command = f"scp -i {KEY} -o StrictHostKeyChecking=no {local_path} {USER}@{HOST}:{remote_path}"
    # Using pexpect logic manually via PTY because scp prompts for password
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp('bash', ['bash', '-c', command])
    else:
        password_sent = False
        while True:
            try:
                data = os.read(fd, 1024)
                if not data: break
                chunk = data.decode(errors='ignore')
                sys.stdout.write(chunk)
                if not password_sent and ("password:" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError: break
        os.waitpid(pid, 0)

def main():
    # 1. Create Archive (excluding heavyweight media that is already on server)
    print("Creating archive (skipping heavy media)...")
    # COPYFILE_DISABLE=1 prevents mac extended attributes (._ files) and warnings
    # Exclude public/images/real because we will preserve it on server
    run_local(f"COPYFILE_DISABLE=1 tar --exclude='node_modules' --exclude='.next' --exclude='.git' --exclude='public/images/real' --exclude='{ARCHIVE_NAME}' -czf {ARCHIVE_NAME} .")

    # 2. DELETE REMOTE FOLDER & CLEANUP PROCESSES (BUT PRESERVE MEDIA)
    print("Preparing remote environment (Preserving Media)...")
    cleanup_cmd = (
        "pm2 delete honolulu || true; "
        "lsof -t -i:3005 | xargs kill -9 || true; "
        "lsof -t -i:3007 | xargs kill -9 || true; "
        # Backup Media
        "mkdir -p /root/honolulu_media_temp; "
        "mv /root/honolulu/public/images/real/* /root/honolulu_media_temp/ 2>/dev/null || true; "
        # Nuke App
        "rm -rf /root/honolulu; "
        "mkdir -p /root/honolulu/public/images/real; "
        # Restore Media
        "mv /root/honolulu_media_temp/* /root/honolulu/public/images/real/ 2>/dev/null || true; "
        "rm -rf /root/honolulu_media_temp; "
    )
    run_ssh_command(cleanup_cmd, use_pty=True)

    # 3. UPLOAD
    upload_file(ARCHIVE_NAME, f"/root/honolulu/{ARCHIVE_NAME}")
    upload_file("honolulu_nginx.conf", "/etc/nginx/sites-available/honolulu")

    # 4. EXTRACT & INSTALL & BUILD
    print("Installing and Building remotely...")
    build_cmd = (
        "cd /root/honolulu && "
        f"tar -xzf {ARCHIVE_NAME} && "
        "npm install --legacy-peer-deps && "
        "npm run build"
    )
    run_ssh_command(build_cmd, use_pty=True)

    # 5. START & NGINX RELOAD
    print("Starting service & Reloading Nginx...")
    start_cmd = (
        "cd /root/honolulu && "
        "pm2 start ecosystem.config.js && "
        "pm2 save && "
        "ln -sf /etc/nginx/sites-available/honolulu /etc/nginx/sites-enabled/honolulu && "
        "nginx -t && "
        "systemctl reload nginx"
    )
    run_ssh_command(start_cmd, use_pty=True)
    
    # 6. VERIFY
    print("Verifying...")
    run_ssh_command("curl -I http://127.0.0.1:3005", use_pty=True)

    # Cleanup local archive
    if os.path.exists(ARCHIVE_NAME):
        os.remove(ARCHIVE_NAME)

if __name__ == "__main__":
    main()
