import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'
# Try on port 3005. If successful, it will hang. We kill it after 5 sec.
CMD = "cd /root/honolulu && ./node_modules/.bin/next start -p 3005"

def run_ssh_command(command):
    pid, fd = pty.fork()
    if pid == 0:
        cmd_list = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', command]
        os.execvp('ssh', cmd_list)
    else:
        output = []
        password_sent = False
        timer_start = time.time()
        killed = False
        while True:
            # If it runs for > 5 seconds, it's a success. We kill it.
            if time.time() - timer_start > 5 and not killed:
                # How to kill? We can't easily send Ctrl-C to the pty fd cleanly in this simple script without potentially hanging.
                # But if we just close fd?
                # Let's hope reading marks success.
                pass

            if time.time() - timer_start > 8:
                 break

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
                
                if "Ready in" in chunk or "started server" in chunk.lower():
                    output.append("\n[[SUCCESS: Server started]]\n")
                    break # Success!
                    
            except OSError:
                break
        
        # Kill the ssh process to stop the server
        os.kill(pid, 9)
        _, status = os.waitpid(pid, 0)
        return "".join(output)

print(run_ssh_command(CMD))
