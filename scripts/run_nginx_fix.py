import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Script to fix Nginx Symlink and Reload
# 1. Remove broken symlink if exists
# 2. Create correct symlink from available/honolulu
# 3. Test and Reload
FIX_NGINX_SCRIPT = """
set -e

echo "--- Fixing Nginx Symlink ---"
cd /etc/nginx/sites-enabled

# Remove old or broken link
if [ -L "honolulu.dojiung.com" ] || [ -f "honolulu.dojiung.com" ]; then
    rm honolulu.dojiung.com
    echo "Removed old honolulu.dojiung.com link"
fi

if [ -L "honolulu" ] || [ -f "honolulu" ]; then
    rm honolulu
    echo "Removed old honolulu link"
fi

# Link correctly
# We previously uploaded config to /etc/nginx/sites-available/honolulu
ln -s /etc/nginx/sites-available/honolulu /etc/nginx/sites-enabled/honolulu.dojiung.com
echo "Created new symlink to honolulu.dojiung.com"

# Verify content
echo "Verifying proxy port..."
grep "proxy_pass" /etc/nginx/sites-available/honolulu

# Reload
nginx -t
systemctl reload nginx
echo "Nginx Reloaded."
"""

def fix_nginx():
    # 1. Write script
    with open('fix_nginx_link.sh', 'w') as f:
        f.write(FIX_NGINX_SCRIPT)
    
    # 2. Upload
    print("Uploading nginx fix script...")
    run_interactive_command(['scp', '-i', KEY, '-o', 'StrictHostKeyChecking=no', 'fix_nginx_link.sh', f'{USER}@{HOST}:/root/fix_nginx_link.sh'])

    # 3. Run
    print("Executing Nginx Fix on server...")
    cmd = "chmod +x /root/fix_nginx_link.sh && /root/fix_nginx_link.sh"
    run_interactive_command(['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', cmd])
    
    if os.path.exists('fix_nginx_link.sh'):
        os.remove('fix_nginx_link.sh')

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
    fix_nginx()
