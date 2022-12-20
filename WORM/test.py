import os
import netifaces

interface_list = netifaces.interfaces()

def getMyIP( interface ):
	# Retrieve and return the IP of the current system.
	# Get the IP address
	ip_addr = netifaces.ifaddresses( interface )[2][0]['addr']

	# The IP address of the interface
	return ip_addr if not ip_addr == "127.0.0.1" else None

for interface in interface_list:
    print("Interface: ", interface)

    ip_addr = getMyIP( interface )
    print("Ip_addr: ", ip_addr)