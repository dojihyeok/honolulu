import pty
import os
import sys
import time
import re

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'
LOCAL_FILE = 'honolulu_nginx.conf'
REMOTE_DEST = '/etc/nginx/sites-available/default' # Assuming default or specialized file. The prompt implies overwriting the config.
# Actually, typically it's sites-available/honolulu or similar. Let's check where it is currently used. 
# The user wants "honolulu_nginx.conf" to be active. 
# Safe bet: upload to /etc/nginx/sites-available/honolulu.dojiung.com and link it, OR just overwrite /etc/nginx/sites-available/default if that's what they use.
# Given previous context, I'll aim for a specific file config. But wait, I shouldn't break other things.
# I'll upload to /etc/nginx/conf.d/honolulu.conf or /etc/nginx/sites-available/honolulu
# Let's try to list /etc/nginx/sites-enabled first to be safe? 
# No, let's just make a script that does it precisely.

# I will upload to a temp location then sudo move it? No, root user login.
# I will upload to /etc/nginx/sites-available/honolulu 
# And then link to /etc/nginx/sites-enabled/honolulu
# And reload.

CMD_RELOAD = """
ln -sf /etc/nginx/sites-available/honolulu /etc/nginx/sites-enabled/honolulu
nginx -t
systemctl reload nginx
"""

def upload_file():
    print(f"Uploading {LOCAL_FILE} to /etc/nginx/sites-available/honolulu...")
    # scp directly to the destination since we are root
    scp_cmd = ['scp', '-i', KEY, '-o', 'StrictHostKeyChecking=no', LOCAL_FILE, f'{USER}@{HOST}:/etc/nginx/sites-available/honolulu']
    
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp('scp', scp_cmd)
    else:
        output = []
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

def run_ssh_command(command):
    print("Reloading Nginx...")
    pid, fd = pty.fork()
    if pid == 0:
        cmd_list = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', command]
        os.execvp('ssh', cmd_list)
    else:
        output = []
        password_sent = False
        while True:
            try:
                data = os.read(fd, 1024)
                if not data:
                    break
                chunk = data.decode(errors='ignore')
                sys.stdout.write(chunk)
                output.append(chunk)
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError:
                break
        _, status = os.waitpid(pid, 0)
        return "".join(output)

if upload_file() == 0:
    print("\nNginx config uploaded.")
    print(run_ssh_command(CMD_RELOAD))
else:
    print("Upload failed.")
