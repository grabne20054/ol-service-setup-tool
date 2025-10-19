import paramiko

class SSHClient:
    
    def __init__(self, hostname: str, username: str, password: str):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.client = None

    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.hostname, username=self.username, password=self.password)
        print(f"Connected to {self.hostname}")

    def execute_command(self, command: str) -> str:
        if not self.client:
            raise Exception("SSH client is not connected")
        
        if not command:
            raise ValueError("Command cannot be empty")
        if "sudo" in command:
            stdin, stdout, stderr = self.client.exec_command(command, get_pty=True)
            stdin.write(self.password + '\n') # Password for sudo != user password (could be)
            stdin.flush()
            output = stdout.read().decode()
            output = output.split(":", 1)[-1].strip()
            return output

        else:
            stdin, stdout, stderr = self.client.exec_command(command, get_pty=True)
        return stdout.read().decode()
    
    def transfer_file(self, local_path: str, remote_path: str):
        if not self.client:
            raise Exception("SSH client is not connected")
        
        sftp = self.client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        print(f"Transferred file to {self.hostname}:{remote_path}")

    def disconnect(self):
        if self.client:
            self.client.close()
            self.client = None