
import os
import paramiko
import subprocess
import time

# Syncs local images to server, then runs optimizer
HOST = "49.50.139.88"
USER = "root"
PASSWORD_FILE = "/Users/yunhyeok/honolulu/.ssh_pass"
LOCAL_IMG_DIR = "public/images/real"
REMOTE_IMG_DIR = "/root/honolulu/public/images/real"

def main():
    password = open(PASSWORD_FILE).read().strip()
    
    # 1. Archive local images
    print("📦 Archiving local images...")
    tar_name = "images_archive.tar.gz"
    # Ensure we are in project root
    subprocess.check_call(f"tar -czf {tar_name} -C {LOCAL_IMG_DIR} .", shell=True)
    
    # 2. Upload
    print("📤 Uploading images archive...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HOST, username=USER, password=password)
    
    sftp = ssh.open_sftp()
    sftp.put(tar_name, f"/root/{tar_name}")
    sftp.put("scripts/server_optimizer_v2.py", "/root/server_optimizer_v2.py")
    sftp.close()
    
    # Cleanup local tar
    os.remove(tar_name)
    
    # 3. Restore on Server
    print("AR Restoring images on server...")
    # Clean directory first? Yes, to remove any garbage
    cmd_clean = f"rm -rf {REMOTE_IMG_DIR}/*"
    ssh.exec_command(cmd_clean)
    
    # Extract
    cmd_extract = f"mkdir -p {REMOTE_IMG_DIR} && tar -xzf /root/{tar_name} -C {REMOTE_IMG_DIR} && rm /root/{tar_name}"
    stdin, stdout, stderr = ssh.exec_command(cmd_extract)
    status = stdout.channel.recv_exit_status()
    if status != 0:
        print(f"Extraction failed: {stderr.read().decode()}")
        return
        
    print("✅ Images restored to original quality.")
    
    # 4. Run Optimizer V2
    print("⚙️  Running Improved Optimizer (Correct Rotation)...")
    # Run in background or foreground? Foreground to ensure it sets up initial batch?
    # Or background so we don't hang? 
    # Let's run in background but wait for a few seconds to see it start
    
    # We'll rely on it finishing eventually.
    cmd_opt = "nohup python3 /root/server_optimizer_v2.py > /root/opt_log.txt 2>&1 &"
    ssh.exec_command(cmd_opt)
    
    print("🚀 Optimization started in background. Monitor /root/opt_log.txt on server.")
    ssh.close()

if __name__ == "__main__":
    main()
