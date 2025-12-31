import paramiko
import os
import sys

# Configuration
HOST = '49.50.139.88'
USER = 'root'
KEY = './deploy_key.pem'
CMD = 'cat /root/honolulu/src/components/Timeline.tsx'

def inspect_remote():
    k = paramiko.RSAKey.from_private_key_file(KEY)
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(hostname=HOST, username=USER, pkey=k)
    
    print(f"Executing: {CMD}")
    stdin, stdout, stderr = c.exec_command(CMD)
    
    out = stdout.read().decode()
    err = stderr.read().decode()
    
    c.close()
    
    if "className=\"nav-btn" in out:
        print("FAIL: Found 'nav-btn' class in remote file! Code is NOT updated.")
    else:
        print("SUCCESS: 'nav-btn' class NOT found. Code seems updated.")
        
    # Check for inline styles I added
    if "borderRadius: '50%'" in out:
        print("SUCCESS: Found inline styles.")
    else:
        print("FAIL: Inline styles NOT found.")

if __name__ == "__main__":
    inspect_remote()
