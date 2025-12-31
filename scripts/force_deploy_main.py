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

def run_ssh_command(command):
    """
    Runs a command on the remote server via SSH using pty to handle the password.
    Returns the output as a string.
    """
    print(f"[{HOST}] Executing: {command}")
    
    pid, fd = pty.fork()
    if pid == 0:
        # Child: Start ssh
        cmd_list = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', command]
        os.execvp('ssh', cmd_list)
    else:
        # Parent
        output = []
        password_sent = False
        
        while True:
            try:
                data = os.read(fd, 1024)
                if not data:
                    break
                
                chunk = data.decode(errors='ignore')
                output.append(chunk)
                
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5) 
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
                    
            except OSError:
                break
        
        _, status = os.waitpid(pid, 0)
        return "".join(output)

def deploy():
    # Hardcoded app dir based on previous success
    app_dir = "/root/honolulu"
    
    print(f"Targeting App Dir: {app_dir}")
    
    commands = [
        f"cd {app_dir} && git fetch origin",
        f"cd {app_dir} && git reset --hard origin/main", # Force switch to main and overwrite local changes
        f"cd {app_dir} && npm install --legacy-peer-deps",
        f"cd {app_dir} && rm -rf .next", # Clean cache 
        f"cd {app_dir} && npm run build",
        f"cd {app_dir} && pm2 restart {APP_NAME}"
    ]
    
    for cmd in commands:
        print(f"\n--- Running: {cmd} ---")
        out = run_ssh_command(cmd)
        print(out)
        if "error" in out.lower() and "npm ERR!" in out:
             print("Potential Error detected in output. Stopping.")
             return

    print("\n--- Force Deployment Complete ---")

if __name__ == "__main__":
    deploy()
