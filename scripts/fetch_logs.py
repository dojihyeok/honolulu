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

if __name__ == "__main__":
    # Fetch logs
    print(run_ssh_command(f"pm2 logs {APP_NAME} --lines 100 --nostream"))
