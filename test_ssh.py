import pty
import os
import sys
import time

def ssh_command(host, user, password, command):
    pid, fd = pty.fork()
    if pid == 0:
        # Child
        os.execvp('ssh', ['ssh', '-o', 'StrictHostKeyChecking=no', f'{user}@{host}', command])
    else:
        # Parent
        time.sleep(1) # Wait for prompt
        # We blindly send password. reliable enough for a test.
        # In a real tool we'd read output and look for 'password:'.
        os.write(fd, (password + '\n').encode())
        
        output = []
        while True:
            try:
                data = os.read(fd, 1024)
                if not data:
                    break
                output.append(data.decode(errors='ignore'))
            except OSError:
                break
        
        # Determine exit status if needed, but output is enough for now
        _, status = os.waitpid(pid, 0)
        return "".join(output)

print(ssh_command('49.50.139.88', 'root', 'R4+r525MP5DiBi', 'ls -F'))
