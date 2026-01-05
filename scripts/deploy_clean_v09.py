import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Script to Clean Build Cache and Rebuild for v0.09
# 1. Remove .next folder (cache)
# 2. Rebuild
# 3. Restart process
CLEAN_BUILD_SCRIPT = """
set -e

cd /root/honolulu

echo "--- 3. Removing Next.js Cache (.next) ---"
rm -rf .next
echo "Cache removed."

echo "--- 4. Building Fresh ---"
npm run build

echo "--- 5. Restarting Process ---"
pm2 restart honolulu

echo "--- DEPLOY (v0.09) COMPLETE ---"
"""

def deploy_clean_build():
    with open('build_v09.sh', 'w') as f:
        f.write(CLEAN_BUILD_SCRIPT)
    
    print("Uploading clean build script...")
    run_interactive_command(['scp', '-i', KEY, '-o', 'StrictHostKeyChecking=no', 'build_v09.sh', f'{USER}@{HOST}:/root/build_v09.sh'])

    print("Executing Clean Build on server...")
    cmd = "chmod +x /root/build_v09.sh && /root/build_v09.sh"
    run_interactive_command(['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', cmd])
    
    if os.path.exists('build_v09.sh'):
        os.remove('build_v09.sh')

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
    deploy_clean_build()
