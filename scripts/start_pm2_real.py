import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

# Start All Services
CMD = "cd /root/honolulu && pm2 start ecosystem.config.js && pm2 save"

def run_ssh_command(command):
    print(f"Executing: {command}")
    pid, fd = pty.fork()
    if pid == 0:
        cmd_list = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', command]
        os.execvp('ssh', cmd_list)
    else:
        output = []
        password_sent = False
        timer_start = time.time()
        while True:
            # 타임아웃 30초
            if time.time() - timer_start > 30:
                break
            try:
                data = os.read(fd, 1024)
                if not data:
                    break
                chunk = data.decode(errors='ignore')
                sys.stdout.write(chunk)
                sys.stdout.flush()
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
    run_ssh_command(CMD)
