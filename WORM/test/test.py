import socket
import paramiko

def tryCredentials( host, userName, password, sshClient ):
	try:
		sshClient.connect( host, username = userName, password = password )
	except socket.error as sock_err:
		print("Socket Error - " + sock_err)
		return 3
	except paramiko.SSHException as miko_err:
		print("Wrong credentials - " + str( miko_err ))
		return 1
	return 0

host = ''
password = ''