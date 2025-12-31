import pty
import os
import sys
import time

# Configuration
HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'
APP_NAME = 'honolulu'

def run_ssh_command(command):
    print(f"[{HOST}] Executing: {command}")
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
                if not data: break
                chunk = data.decode(errors='ignore')
                output.append(chunk)
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError: break
        os.waitpid(pid, 0)
        return "".join(output)

def restart_pm2():
    app_dir = "/root/honolulu"
    # Restart cleanly
    run_ssh_command(f"pm2 delete {APP_NAME}")
    out = run_ssh_command(f"cd {app_dir} && pm2 start npm --name \"{APP_NAME}\" -- start")
    print(out)
    
if __name__ == "__main__":
    restart_pm2()
