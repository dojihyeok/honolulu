
import os
import time
import paramiko
import subprocess
import sys
import threading

# Configuration
HOST = "49.50.139.88"
USER = "root"
KEY_PATH = "/Users/yunhyeok/triedit-dev.pem"
APP_DIR = "/root/honolulu"
PORT = 3005
USER_HOST = f"{USER}@{HOST}"

def run_local(command):
    print(f"[LOCAL] {command}")
    subprocess.check_call(command, shell=True)

def run_ssh_command(command):
    print(f"[REMOTE] {command}")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=open('/Users/yunhyeok/honolulu/.ssh_pass').read().strip())
    
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    
    ssh.close()
    
    if exit_status != 0:
        print(f"Error executing command: {command}")
        print(f"Stderr: {err}")
        # Don't always raise, let caller decide, but for this script we usually want to know
    return out

def cleanup_port(port):
    print(f"Cleaning up port {port}...")
    # Try to find PID using the port and kill it forcefully
    kill_cmd = f"fuser -k {port}/tcp || true"
    run_ssh_command(kill_cmd)
    
    # Double check with lsof just in case fuser missed it or isn't installed (though it usually is)
    # lsof -t -i:3005 | xargs kill -9
    kill_cmd_2 = f"lsof -t -i:{port} | xargs -r kill -9 || true"
    run_ssh_command(kill_cmd_2)
    
    time.sleep(2) # Give OS time to release the socket

def main():
    print("🚀 Starting Robust Deployment...")

    # 1. Prepare Local Build/Archive (skipping heavy media)
    archive_name = "deploy_package.tar.gz"
    print("📦 Creating production archive...")
    # Exclude heavy folders and git
    excludes = "--exclude='node_modules' --exclude='.next' --exclude='.git' --exclude='public/images/real' --exclude='*.tar.gz'"
    run_local(f"COPYFILE_DISABLE=1 tar {excludes} -czf {archive_name} .")

    # 2. Upload Archive
    print("📤 Uploading archive...")
    # SCP with sshpass
    password = open('/Users/yunhyeok/honolulu/.ssh_pass').read().strip()
    os.system(f"sshpass -p '{password}' scp {archive_name} {USER_HOST}:{APP_DIR}/{archive_name}")
    run_local(f"rm {archive_name}") # Cleanup local

    # 3. Remote: Cleanup & Setup
    print("🧹 Cleaning remote environment...")
    
    # Stop PM2 first to prevent auto-restart war
    run_ssh_command("pm2 delete honolulu || true")
    
    # KILL THE PORT - This is the "User Request" fix.
    cleanup_port(PORT)
    
    # Extract
    print("haz Extracting files...")
    run_ssh_command(f"cd {APP_DIR} && tar -xzf {archive_name} && rm {archive_name}")

    # Install Dependencies (fast since node_modules usually persists, but good to ensure)
    print("📦 Installing dependencies...")
    run_ssh_command(f"cd {APP_DIR} && npm install --production --no-audit")

    # Build
    print("🏗️ Building Next.js app...")
    # Note: We build ON SERVER to ensure architecture compatibility
    build_out = run_ssh_command(f"cd {APP_DIR} && npm run build")
    if "Error" in build_out and "Module not found" in build_out:
         print("Build failed!")
         sys.exit(1)

    # 4. Start Application
    print("🚀 Starting with PM2...")
    # Explicitly ensure port 3005 in ecosystem is respected or passed via env if needed, 
    # but we updated ecosystem.config.js previously to 3005.
    
    # One last cleanup just to be paranoid before binding
    cleanup_port(PORT)
    
    start_cmd = f"cd {APP_DIR} && pm2 start ecosystem.config.js"
    run_ssh_command(start_cmd)
    
    # Save PM2 list so it survives reboots (optional but good practice)
    run_ssh_command("pm2 save")

    # 5. Verification
    print("🔍 Verifying deployment...")
    for i in range(12): # Try for 60 seconds
        print(f"   Attempt {i+1}...")
        time.sleep(5)
        # Check if local curl works
        check_cmd = f"curl -s http://127.0.0.1:{PORT} | grep '<!DOCTYPE html>'"
        out = run_ssh_command(check_cmd)
        if out:
            print(f"✅ Deployment Verification SUCCESS! Port {PORT} is serving content.")
            break
    else:
        print(f"❌ Verification FAILED. Port {PORT} might not be responding.")
        # Fetch logs
        print("   Fetching recent logs...")
        logs = run_ssh_command(f"tail -n 20 /root/.pm2/logs/honolulu-error.log")
        print(logs)

if __name__ == "__main__":
    main()
