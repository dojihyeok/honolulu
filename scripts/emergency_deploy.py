import pty
import os
import sys
import time
import re

# Configuration
HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'
APP_NAME = 'honolulu'
APP_DIR = '/root/honolulu'

def run_ssh_command(command, print_output=True):
    """
    Runs a command on the remote server via SSH using pty.
    """
    if print_output:
        print(f"\n[{HOST}] Executing: {command}")
    
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
                if print_output:
                    print(chunk, end='') # Stream output to user
                output.append(chunk)
                
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5) 
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
                    
            except OSError:
                break
        
        _, status = os.waitpid(pid, 0)
        return "".join(output)

def main():
    print("!!! STARTING EMERGENCY FIX DEPLOYMENT !!!")
    
    # 1. Kill everything first
    input("Step 1: Cleanup. Press Enter to continue...")
    kill_cmds = [
        f"pm2 delete {APP_NAME} || true",
        f"fuser -k 3006/tcp || true",
        f"lsof -t -i:3006 | xargs kill -9 || true"
    ]
    for cmd in kill_cmds:
        run_ssh_command(f"{cmd}")

    # 2. Clean install
    input("Step 2: Clean Install. Press Enter to continue...")
    run_ssh_command(f"cd {APP_DIR} && rm -rf .next node_modules")
    run_ssh_command(f"cd {APP_DIR} && npm install --legacy-peer-deps")

    # 3. Build with explicit verified output
    input("Step 3: Build. Press Enter to continue...")
    build_out = run_ssh_command(f"cd {APP_DIR} && npm run build")
    
    if "Error:" in build_out or "Err:" in build_out or "Failed" in build_out:
        print("\n\n!! POSSIBLE BUILD ERROR DETECTED !! Please check logs above.")
        proceed = input("Do you want to proceed to start anyway? (y/n): ")
        if proceed.lower() != 'y':
            return

    # 4. Start
    input("Step 4: Start PM2. Press Enter to continue...")
    run_ssh_command(f"cd {APP_DIR} && pm2 start npm --name '{APP_NAME}' -- start")
    
    # 5. Check logs immediately
    print("\nChecking logs for startup success...")
    time.sleep(5)
    run_ssh_command(f"pm2 logs {APP_NAME} --lines 20 --nostream")

if __name__ == "__main__":
    main()
