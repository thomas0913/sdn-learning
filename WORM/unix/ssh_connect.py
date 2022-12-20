import paramiko

username = "thomas"
password = "408440021"
hostname = "127.0.0.1"
port = 22

try:
    client = paramiko.SSHClient()
except Exception:
    print("Exception ! !")
    raise