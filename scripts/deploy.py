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

def run_ssh_command(command, interactive=False):
    """
    Runs a command on the remote server via SSH using pty to handle the password.
    Returns the output as a string.
    """
    print(f"[{HOST}] Executing: {command}")
    
    # helper to clean output
    def clean_output(raw_output):
        # Remove the echo equivalent of the command we just sent if it appears
        # And standard control characters
        return re.sub(r'\x1b\[[0-9;]*[mGKB]', '', raw_output).replace('\r', '')

    pid, fd = pty.fork()
    if pid == 0:
        # Child: Start ssh
        # -t forces tty allocation which might be needed for some commands or .bashrc sourcing
        # but for simple command execution, sometimes it adds noise.
        # We use strict host key checking = no to avoid prompts
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
                
                # Check for password prompt
                # Note: The prompt might be "root@49.50.139.88's password: " or similar.
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5) # debounce
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
                    
            except OSError:
                break
        
        _, status = os.waitpid(pid, 0)
        
        full_output = "".join(output)
        # Try to strip out the password prompt interaction
        # Find where password was asked (roughly)
        return full_output

def find_app_directory():
    # Try to find the directory
    search_dirs = [
        f"/root/{APP_NAME}",
        f"/var/www/{APP_NAME}",
        f"/home/{APP_NAME}",
        f"~/{APP_NAME}"
    ]
    
    # We'll valid by checking if package.json exists there
    cmd = " || ".join([f"[ -f {d}/package.json ] && echo FOUND_AT::{d}" for d in search_dirs])
    
    out = run_ssh_command(cmd)
    match = re.search(r"FOUND_AT::(\S+)", out)
    if match:
        return match.group(1)
    return None

def deploy():
    print("--- Starting Deployment ---")
    
    # 1. Find Directory
    print("Searching for application directory...")
    print("(This might take a moment and you may see raw SSH output)")
    app_dir = find_app_directory()
    
    if not app_dir:
        print("ERROR: Could not find application directory on server.")
        sys.exit(1)
        
    print(f"Found application at: {app_dir}")
    
    # 2. Commands to run
    # Detect branch first
    detect_branch_cmd = f"cd {app_dir} && git branch --show-current"
    branch_out = run_ssh_command(detect_branch_cmd)
    # Extract branch name (clean output)
    branch = branch_out.strip().split('\n')[-1] # Simple heuristic
    # Fallback if empty or failed
    if not branch or " " in branch: 
        branch = "main"
        print(f"Could not detect branch, defaulting to {branch}")
    else:
        print(f"Detected branch: {branch}")

    commands = [
        f"cd {app_dir} && git status",
        f"cd {app_dir} && git pull origin {branch}",
        f"cd {app_dir} && npm install --legacy-peer-deps", 
        f"cd {app_dir} && npm run build",
        f"cd {app_dir} && pm2 restart {APP_NAME} || pm2 start npm --name \"{APP_NAME}\" -- start"
    ]
    
    for cmd in commands:
        print(f"\n--- Running: {cmd} ---")
        out = run_ssh_command(cmd)
        print(out)
        if "error" in out.lower() and "npm ERR!" in out:
             print("Potential Error detected in output. Stopping.")
             return

    print("\n--- Deployment Complete ---")

if __name__ == "__main__":
    deploy()
