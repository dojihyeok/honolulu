import pty
import os
import sys
import time

HOST = '49.50.139.88'
USER = 'root'
PASS = 'R4+r525MP5DiBi'
KEY = './deploy_key.pem'

def run_ssh_command(command):
    #print(f"Running: {command}")
    pid, fd = pty.fork()
    if pid == 0:
        cmd_list = ['ssh', '-i', KEY, '-o', 'StrictHostKeyChecking=no', f'{USER}@{HOST}', command]
        os.execvp('ssh', cmd_list)
    else:
        output = []
        password_sent = False
        start_time = time.time()
        while True:
            if time.time() - start_time > 30: break
            try:
                data = os.read(fd, 4096)
                if not data: break
                chunk = data.decode(errors='ignore')
                # sys.stdout.write(chunk)
                output.append(chunk)
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError: break
        _, status = os.waitpid(pid, 0)
        return "".join(output)

print("Fetching image dimensions from server...")
# Command to get dimensions using 'file' utility which usually outputs layout like:
# ...jpg: JPEG image data ... 4000x3000 ...
raw_output = run_ssh_command("cd /root/honolulu/public/images/real && file *.jpg")

import re

# Parse the output
# Expected format: "filename.jpg: JPEG image data, ..., 4000x3000, ..."
regex = r"([^:]+\.jpg):.+?(\d+)x(\d+)"
matches = re.findall(regex, raw_output)

print(f"Found {len(matches)} images with dimensions.")
print("JSON_START")
import json
data = {}
for m in matches:
    name = m[0].strip()
    w = int(m[1])
    h = int(m[2])
    data[name] = {"w": w, "h": h}
print(json.dumps(data))
print("JSON_END")
