"""Custom topology example

Two directly connected switches plus a host for each switch:

              --- host6     --- host4        --- host2
              |             |                |
   host8 --- topSwitch --- middleSwitch --- downSwitch --- host1
              |             |                |
              --- host7     --- host5        --- host3

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo

class RhmTopo( Topo ):
    "Simple topology example."

    def __init__(self):
        "Create custom topo."

        # Initialize topology
        Topo.__init__(self)

        # Add hosts and switches
        Host1 = self.addHost( 'h1' )
        Host2 = self.addHost( 'h2' )
        Host3 = self.addHost( 'h3' )
        Host4 = self.addHost( 'h4' )
        Host5 = self.addHost( 'h5' )
        Host6 = self.addHost( 'h6' )
        Host7 = self.addHost( 'h7' )
        Host8 = self.addHost( 'h8' )
        downSwitch = self.addSwitch( 's1' )
        middleSwitch = self.addSwitch( 's2' )
        topSwitch = self.addSwitch( 's3' )

        # Add links
        self.addLink( Host8, topSwitch )
        self.addLink( Host7, topSwitch )
        self.addLink( Host6, topSwitch )
        self.addLink( topSwitch, middleSwitch )
        self.addLink( Host5, middleSwitch )
        self.addLink( Host4, middleSwitch )
        self.addLink( middleSwitch, downSwitch )
        self.addLink( downSwitch, Host3 )
        self.addLink( downSwitch, Host2 )
        self.addLink( downSwitch, Host1 )

topos = { 'mytopo': ( lambda: RhmTopo() ) }