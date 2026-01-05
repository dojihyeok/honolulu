import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

def run_ssh_command(command):
    print(f"Running: {command}")
    pid, fd = pty.fork()
    if pid == 0:
        cmd_list = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', command]
        os.execvp('ssh', cmd_list)
    else:
        output = []
        password_sent = False
        start_time = time.time()
        while True:
            if time.time() - start_time > 15: break
            try:
                data = os.read(fd, 4096)
                if not data: break
                chunk = data.decode(errors='ignore')
                sys.stdout.write(chunk)
                output.append(chunk)
                if not password_sent and ("password:" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError: break
        _, status = os.waitpid(pid, 0)
        return "".join(output)

print("Checking for 'v0.02' in localhost:3003 response...")
content = run_ssh_command("curl -s http://127.0.0.1:3003 | grep 'v0.02' || echo 'VERSION_NOT_FOUND'")

if "v0.02" in content:
    print("\nSUCCESS: Found 'v0.02' in server response.")
else:
    print("\nFAILURE: 'v0.02' NOT found in server response.")
