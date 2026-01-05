import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

def run_ssh_command(command):
    print(f"Running: {command}")
    pid, fd = pty.fork()
    if pid == 0:
        cmd_list = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', command]
        os.execvp('ssh', cmd_list)
    else:
        output = []
        password_sent = False
        start_time = time.time()
        while True:
            if time.time() - start_time > 10: break
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

print("=== REMOVING CONFLICTING NGINX CONFIG ===")
# Remove the old symlink
run_ssh_command("rm -f /etc/nginx/sites-enabled/honolulu.dojiung.com")
# Remove the old available file (optional, but cleaner)
run_ssh_command("rm -f /etc/nginx/sites-available/honolulu.dojiung.com")

print("\n=== RELOADING NGINX ===")
run_ssh_command("nginx -t && systemctl restart nginx")

print("\n=== VERIFICATION ===")
run_ssh_command("ls -l /etc/nginx/sites-enabled/ | grep honolulu")
