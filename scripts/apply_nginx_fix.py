
import os
import subprocess

def apply_nginx():
    # 1. Upload the combined config
    subprocess.run([
        'scp', '-i', './deploy_key.pem', '-o', 'StrictHostKeyChecking=no',
        'honolulu_nginx_combined.conf', 'root@49.50.139.88:/etc/nginx/sites-available/combined_services'
    ], check=True)
    
    # 2. Remote commands: Link and Reload
    # Warning: removing all enabled sites might be risky if we fail, but it clears conflicts.
    cmd = """
    rm -f /etc/nginx/sites-enabled/*
    ln -sf /etc/nginx/sites-available/combined_services /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
    """
    
    subprocess.run([
        'ssh', '-i', './deploy_key.pem', '-o', 'StrictHostKeyChecking=no',
        'root@49.50.139.88', cmd
    ], check=True)

if __name__ == "__main__":
    apply_nginx()
