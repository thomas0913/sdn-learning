import sys
import os
import netifaces
from tools import Tools

# 建立蠕蟲工具實例
WormTools = Tools()

print("")

if len( sys.argv ) < 2 and not os.path.exists( WormTools.HOST_MARKER_FILE ):
    print("Normal mode\n")

if any( arg in ( "-c", "--clean" ) for arg in sys.argv):
    print("[CLEANING MODE . . . \n")
    CLEANING_MODE = True

interface_list = netifaces.interfaces()
#interface_list.remove( WormTools.LOOPBACK_INTERFACE )

print(interface_list)

for interface in interface_list:
    print("Interface: ", interface)


print("\nThis is the end of script ~~~")