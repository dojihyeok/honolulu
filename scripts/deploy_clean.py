import paramiko
import os
import time

# Server Details
HOSTNAME = "49.50.139.88"
USERNAME = "root"
KEY_FILE = "/Users/yunhyeok/honolulu/deploy_key.pem"
APP_DIR = "/root/honolulu"
APP_NAME = "honolulu"

def run_ssh_command(command):
    k = paramiko.RSAKey.from_private_key_file(KEY_FILE)
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname=HOSTNAME, username=USERNAME, pkey=k)
    print(f"[Remote] Executing: {command}")
    stdin, stdout, stderr = c.exec_command(command)
    
    # Wait for completion
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    c.close()
    
    if out: print(f"[Output]: {out}")
    if err: print(f"[Error]: {err}")
    
    if exit_status != 0:
        raise Exception(f"Command failed with status {exit_status}: {err}")
    return out

def deploy():
    print("--- Starting Clean Deployment ---")
    
    # 1. Check current commit
    print("\n[1/6] Checking current server state...")
    try:
        run_ssh_command(f"cd {APP_DIR} && git log -1 --oneline")
    except:
        pass

    # 2. Stop Process
    print("\n[2/6] Stopping PM2...")
    try:
        run_ssh_command(f"pm2 delete {APP_NAME}")
    except:
        print("Process not running or ignore error")

    # 3. Clean .next folder
    print("\n[3/6] Cleaning .next build folder...")
    run_ssh_command(f"cd {APP_DIR} && rm -rf .next")

    # 4. Update Code
    print("\n[4/6] Pulling latest code...")
    run_ssh_command(f"cd {APP_DIR} && git fetch origin && git reset --hard origin/main")
    run_ssh_command(f"cd {APP_DIR} && git log -1 --oneline")

    # 5. Build
    print("\n[5/6] Install & Build...")
    run_ssh_command(f"cd {APP_DIR} && npm install --legacy-peer-deps")
    run_ssh_command(f"cd {APP_DIR} && npm run build")

    # 6. Start
    print("\n[6/6] Starting PM2...")
    run_ssh_command(f"cd {APP_DIR} && pm2 start npm --name \"{APP_NAME}\" -- start")

    print("\n--- Deployment Complete ---")

if __name__ == "__main__":
    deploy()
