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
                data = os.read(fd, 1024)
                if not data: break
                chunk = data.decode(errors='ignore')
                sys.stdout.write(chunk)
                output.append(chunk)
                if not password_sent and ("password:" in chunk.lower() or "passphrase" in chunk.lower()):
                    time.sleep(0.5)
                    os.write(fd, (PASS + '\n').encode())
                    password_sent = True
            except OSError: break
        _, status = os.waitpid(pid, 0)
        return "".join(output)

print("=== KILLING ALL CONFLICTING PROCESSES ===")
# 1. Stop PM2 process
run_ssh_command("pm2 stop honolulu || true")
run_ssh_command("pm2 delete honolulu || true")

# 2. Kill zombie processes on 3003 AND 3007
kill_cmd = """
for P in 3003 3007; do
    PID=$(lsof -t -i:$P)
    if [ -n "$PID" ]; then
        echo "Found zombie process $PID on $P. Killing..."
        kill -9 $PID
    else
        echo "Port $P is clean."
    fi
done
"""
run_ssh_command(kill_cmd)

# 3. Double Check
run_ssh_command("lsof -i :3003")
run_ssh_command("lsof -i :3007")

print("\n=== RESTARTING HONOLULU ON PORT 3003 ===")
# 4. Start Fresh on 3003 (as configured in LOCAL ecosystem file which we uploaded)
# Note: we assume ecosystem.config.js is already updated to port 3003 from previous steps,
# but let's verify ecosystem.config.js content on remote just to be sure
print("Checking remove ecosystem config port...")
run_ssh_command("grep PORT /root/honolulu/ecosystem.config.js")

run_ssh_command("cd /root/honolulu && pm2 start ecosystem.config.js && pm2 save")

print("\n=== STATUS CHECK ===")
run_ssh_command("pm2 list")
run_ssh_command("curl -I http://127.0.0.1:3003")
