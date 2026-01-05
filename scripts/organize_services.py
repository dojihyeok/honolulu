
import os
import subprocess

ECOSYSTEM_CONFIG = """
module.exports = {
  apps: [
    {
      name: 'trydit',
      cwd: '/root/antigravity',
      script: 'npm',
      args: 'start -- -p 3000',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    },
    {
      name: 'auditflow',
      cwd: '/root/auditflow/frontend',
      script: 'npm',
      args: 'start -- -p 3001',
      env: {
        NODE_ENV: 'production',
        PORT: 3001
      }
    },
    {
      name: 'portfolio',
      cwd: '/root/portfolio',
      script: 'npm',
      args: 'start -- -p 3002',
      env: {
        NODE_ENV: 'production',
        PORT: 3002
      }
    },
    {
      name: 'honolulu',
      cwd: '/root/honolulu',
      script: 'npm',
      args: 'start -- -p 3003',
      env: {
        NODE_ENV: 'production',
        PORT: 3003
      }
    }
  ]
};
"""

def organize():
    # 1. Create local ecosystem file
    with open('ecosystem.config.js', 'w') as f:
        f.write(ECOSYSTEM_CONFIG.strip())

    # 2. Upload config
    subprocess.run([
        'scp', '-i', './deploy_key.pem', '-o', 'StrictHostKeyChecking=no',
        'ecosystem.config.js', 'root@49.50.139.88:/root/ecosystem.config.js'
    ], check=True)

    # 3. Execute remote organization commands
    cmd = """
    # Move AuditFlow to clean path
    if [ -d "/root/auditflow_recovery" ]; then
        rm -rf /root/auditflow 2>/dev/null
        mv /root/auditflow_recovery /root/auditflow
    fi
    
    # Kill any rogue next-servers causing conflicts
    pkill -f 'next-server' || true
    
    # Reset PM2
    pm2 delete all
    
    # Start all from ecosystem
    pm2 start /root/ecosystem.config.js
    
    # Save for reboot
    pm2 save
    pm2 startup | tail -n 1 | bash
    """
    
    subprocess.run([
        'ssh', '-i', './deploy_key.pem', '-o', 'StrictHostKeyChecking=no',
        'root@49.50.139.88', cmd
    ], check=True)

if __name__ == "__main__":
    organize()
