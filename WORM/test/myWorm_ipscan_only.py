import socket
import paramiko
import nmap
import sys
import os
from nmap.nmap import PortScannerError

def getHostsOnTheSameNetwork():
        # Scanning for hosts on the same network
        # and return the list of discovered
        # IP addresses.
        try:
            portScanner = nmap.PortScanner()
            portScanner.scan( '10.0.0.0/24', arguments = '-T4 -p 22 --open', sudo=True, timeout=10.0)
        except PortScannerError as scan_timeout:
            print("\n Scan Error - " + str(scan_timeout), "\n")
            sys.exit()
        return portScanner

result = getHostsOnTheSameNetwork()

print("\n * Command Line : " + str(result.command_line()))
print("\n * All Host : " + str(result.all_hosts()), "\n")