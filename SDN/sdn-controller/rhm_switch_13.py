from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller import event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import icmp
from ryu.lib.packet import arp
from ryu.lib.packet import ipv4
from ryu.lib import hub
from random import randint, seed
from time import time

# Main Application
class RandomHostMutation_Switch(app_manager.RyuApp):

    # APP 初始化
    def __init__(self, *_args, **_kwargs):
        '''
            << Constructor >> :
                1. 用來初始化成員變數。
        '''
        # 繼承 RyuApp 類別並初始化 RyuApp 之初始設置
        super(RandomHostMutation_Switch, self).__init__(*_args, **_kwargs)
        self.mac_to_port = {}
    
    # Switch 功能處理器
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        '''
            << Switch 功能處理器 >> : 
                1. 處理由 switch 發送到 controller 的 switch feature 事件。
                2. switch 發送協商訊息。
                3. 我們儲存 switch 訊息到 datapath 成員變數。
                4. 新增 miss flow entry table 到 switch 中。
        '''
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
                                          
        print("==============================")
        print("|    Table-miss Flow Entry   |")
        print("==============================")
        print("datapath => ", datapath)
        print("priority => ", 0)
        print("match => ", match)
        print("actions => ", actions)
        print("------------------------------")
        print("..")
        print("..")

        self.add_flow(datapath, 0, match, actions)

    # OpenFlow 流表生產器
    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        '''
            << 流表生產器 >> :
                1. 新增流表規則至 Switch。
        '''
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it
        inst = [parser.OFPInstructions(ofproto.OFPIT_APPLY_ACTIONS,
                                       actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        datapath.send_msg(mod)

    # 封包輸入處理器
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        '''
            << 封包輸入處理器 >> :
                1. 透過更換傳入封包中的來源、目的IP地址來實現RHM演算法。
                2. 處理傳入的封包。
        '''
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        print("------------------------------------------")
        print("Add switch_", dpid, " to mac_to_port table")
        print("------------------------------------------")
        print("..")
        print("..")

        #self.logger.info("packet in %s %s %s %s", dpid, src, dst, in_port)
        print("==================================")
        print("|        Packet iIn Event        |")
        print("==================================")
        print("dpid => ", dpid)
        print("src => ", src)
        print("dst => ", dst)
        print("in_port => ", in_port)
        print("-------------------------------------")
        print("..")
        print("..")

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = in_port

        print("==================================")
        print("|        mac_to_port Table       |")
        print("==================================")

        print(self.mac_to_port)
        print("-----------------------------------------")
        print("..")
        print("..")

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                print("======================")
                print("|    Add Flow Entry  |")
                print("======================")
                print(datapath)
                print(1)
                print(match)
                print(actions)
                print(msg.buffer_id)
                print("------------------------")
                print("..")
                print("..")
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                print("======================")
                print("|    Add Flow Entry  |")
                print("======================")
                print(datapath)
                print(1)
                print(match)
                print(actions)
                print("------------------------")
                print("..")
                print("..")
                self.add_flow(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
