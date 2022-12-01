# =========================================================
# ||        隨機主機變換演算法 Ryu Switch Controller       ||
# =========================================================

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

# Custom Event for time out
class EventMessage(event.EventBase):
    '''
        << 自訂義事件模板 >> :
            1. 使用提供的消息創建自定義事件
    '''
    def __init__(self, message):
        print("Creating Event . . .")
        super(EventMessage, self).__init__()
        self.msg = message

# Main Application
class RandomHostMutation_Switch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    _EVENTS = [EventMessage] 
    R2V_Mappings={"10.0.0.1":"", "10.0.0.2":"", "10.0.0.3":"", "10.0.0.4":"",
                  "10.0.0.5":"", "10.0.0.6":"", "10.0.0.7":"", "10.0.0.8":""}
    V2R_Mappings={}
    Resources=["10.0.0.9", "10.0.0.10","10.0.0.11","10.0.0.12",
               "10.0.0.13","10.0.0.14","10.0.0.15","10.0.0.16",
               "10.0.0.17","10.0.0.18","10.0.0.19","10.0.0.20",
               "10.0.0.21","10.0.0.22","10.0.0.23","10.0.0.24",
               "10.0.0.25","10.0.0.26","10.0.0.27","10.0.0.28",
               "10.0.0.29","10.0.0.30","10.0.0.31","10.0.0.32",
               "10.0.0.33","10.0.0.34","10.0.0.35","10.0.0.36"]

    def __init__(self, *_args, **_kwargs):
        '''
            << Constructor >> :
                1. 初始化成員變數。
        '''
        super(RandomHostMutation_Switch, self).__init__(*_args, **_kwargs)
        # ARP廣播表
        self.mac_to_port = {}
        self.datapaths = set()
        self.HostAttachments = {}
        self.offset_of_mappings = 0

    def start(self):
        '''
            << 超時事件開始器 >> :
                1. 增加一個新執行緒，該執行緒每30秒調用TimerEventGen超時事件生成函數
                2. 發送超時事件到 controller 之監聽器中
        '''
        super(RandomHostMutation_Switch,self).start()
        self.threads.append(hub.spawn(self.TimerEventGen))
            
    def TimerEventGen(self):
        '''
            << 超時事件生成器 >> :
                1. 每30秒生成超時事件。
                2. 發送超時事件到 controller 之監聽器中
        '''
        while 1:
            # 將超時事件發送給該 RyuApp 的所有觀察者。
            self.send_event_to_observers(EventMessage("TIMEOUT"))
            hub.sleep(30)
    
    def add_flow(self, datapath, priority, match, actions, buffer_id=None, hard_timeout=None):
        '''
            << 流表生產器 >> :
                1. 新增流表規則至 Switch。
        '''
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                       actions)]
        if buffer_id :
            if hard_timeout == None:
                mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                        priority=priority, match=match, instructions=inst)
            else:
                mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                        priority=priority, match=match,
                                        instructions=inst, hard_timeout=hard_timeout)
        else :
            if hard_timeout == None:
                mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                        match=match, instructions=inst)
            else:
                mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                        match=match, instructions=inst, hard_timeout=hard_timeout)
        datapath.send_msg(mod)

    def EmptyTable(self,datapath):
        '''
            << 流表重置器 >> :
                1. 清空Switch中所有的流表。
        '''
        ofProto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()

        flow_mod = parser.OFPFlowMod(datapath,
                                     0, # cookie
                                     0, # cookie_mask
                                     0, # table_id
                                     ofProto.OFPFC_DELETE,
                                     0, # idle_timeout 
                                     0, # hard_timeout 
                                     1, # priority 
                                     ofProto.OFPCML_NO_BUFFER,
                                     ofProto.OFPP_ANY, # out_port 
                                     ofProto.OFPG_ANY, # out_group 
                                     0, # flags
                                     match=match,
                                     instructions=[])
        datapath.send_msg(flow_mod)
    
    # Returns True if IP address is real
    def isRealIPAddress(self,ipAddr):
        if ipAddr in self.R2V_Mappings.keys():
            return True
    
    # Returns True if the IP address is virtual
    def isVirtualIPAddress(self,ipAddr):
        if ipAddr in self.R2V_Mappings.values():
            return True
    
    def isDirectContact(self,datapath,ipAddr):
        '''
            << 直接溝通判斷器 >> :
                1. 如果IP地址host直接連接到給定的switch，則返回真
                2. 如果在 hostAttachments 表中沒有信息，則假定主機是直接連接的
        '''
        if ipAddr in self.HostAttachments.keys():
            if self.HostAttachments[ipAddr]==datapath:
                return True
            else:
                return False
        return True

    # ======================== 交握連接處理 ===========================
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
        # 存取 Switch 實例集合中
        self.datapaths.add(datapath)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

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

    # ======================== Listen to timeout & update the mappings ===========================
    @set_ev_cls(EventMessage)
    def update_resources(self,ev):
        '''
            << ip addr 資源更新器 >> :
                1. 監聽超時事件。
                2. 從resource中更新真實-虛擬 IP 地址映射。
                3. 從所有switch中刪除流表，並向所有switch添加一個默認的 table-miss entry。
        '''
        seed(time()) # base on sys time
        pseudo_ranum = randint(0,len(self.Resources)-1) #randint returns a random integer in the range of 0 and len(Resources)-1
        print ("Random Number : ", pseudo_ranum)

        for keys in self.R2V_Mappings.keys():
            # 從第 (pseudo_ranum) 個索引開始，將虛擬 IP 地址分配給資源池中的每個主機
            self.R2V_Mappings[keys] = self.Resources[pseudo_ranum]
            # pseudo_ranum 被更新為指向下一個索引。如果索引超出資源池，則循環返回指向第 0 個索引  
            pseudo_ranum = (pseudo_ranum + 1) % len(self.Resources)

        self.V2R_Mappings = {v: k for k, v in self.R2V_Mappings.items()}
        print ("**********", self.R2V_Mappings, "***********")
        print ("**********", self.V2R_Mappings, "***********")
        
        for curSwitch in self.datapaths:
            ofProto = curSwitch.ofproto
            parser = curSwitch.ofproto_parser

            # Remove all flow entries
            self.EmptyTable(curSwitch)
            print("==============================")
            print("|    remove-all Flow Entry   |")
            print("==============================")
            print("datapath => ", curSwitch)
            print("------------------------------")
            print("..")
            print("..")

            # Add default flow rule
            match = parser.OFPMatch()
            actions = [parser.OFPActionOutput(ofProto.OFPP_CONTROLLER,
                                              ofProto.OFPCML_NO_BUFFER)]
            print("==============================")
            print("|    Table-miss Flow Entry   |")
            print("==============================")
            print("datapath => ", curSwitch)
            print("priority => ", 0)
            print("match => ", match)
            print("actions => ", actions)
            print("------------------------------")
            print("..")
            print("..")
            self.add_flow(curSwitch, 0, match, actions)

    # ======================== 數據傳送處理(incliding ICMP & ARP) ===========================
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        '''
            << 封包輸入處理器 >> :
                1. 處理傳入的封包。
                2. 透過更換傳入封包中的來源、目的IP地址來實現RHM演算法。
        '''
        actions = []
        pktDrop = False

        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        arp_Obj = pkt.get_protocol(arp.arp)# Extract ARP object from packet
        icmp_Obj = pkt.get_protocol(ipv4.ipv4)# Extract ICMP object packet

        if arp_Obj:
            # Handles ARP packets
            src = arp_Obj.src_ip
            dst = arp_Obj.dst_ip

            if self.isRealIPAddress(src) and src not in self.HostAttachments.keys():
                # 第一次 ARP 數據包進來其 src 地址是real的
                self.HostAttachments[src] = datapath.id

            '''
                || Learning MTD implementation ||
                    1. 如src為real的則無條件轉為virtual的。
                    2. 如果 dst 在我的表中沒有映射更改為 real 和 flood。
                    3. 如果 dst 是virtual的，檢查 dst 是否直接連接，然後將其更改為real的，否則讓它通過不變。
            '''
            if self.isRealIPAddress(src):
                # ARP 封包乙太網路類型編號為 0806
                match = parser.OFPMatch(eth_type=0x0806,in_port=in_port,arp_spa=src,arp_tpa=dst)
                spa = self.R2V_Mappings[src] 
                print("Changing SRC REAL IP " + src + "---> Virtual SRC IP " + spa)
                # 修改數據包中標頭字段為arp_spa的值
                actions.append(parser.OFPActionSetField(arp_spa=spa))
                
            if self.isVirtualIPAddress(dst):
                match = parser.OFPMatch(eth_type=0x0806,in_port=in_port,arp_tpa=dst,arp_spa=src)
                if self.isDirectContact(datapath=datapath.id,ipAddr=self.V2R_Mappings[dst]):
                    keys = self.V2R_Mappings.keys()
                    tpa = self.V2R_Mappings[dst] 
                    print("Changing DST Virtual IP " + dst + "---> REAL DST IP " + tpa)
                    actions.append(parser.OFPActionSetField(arp_tpa=tpa))
            elif self.isRealIPAddress(dst):
                '''Learn MTD From Flood'''
                match=parser.OFPMatch(eth_type=0x0806,in_port=in_port,arp_spa=src,arp_tpa=dst)
                if not self.isDirectContact(datapath=datapath.id,ipAddr=dst):
                    pktDrop = True
                    print("Dropping from",dpid)
            else:
                pktDrop = True
        elif icmp_Obj:
            # Handles ICMP packets
            print("ICMP PACKET FOUND!")
            src = icmp_Obj.src
            dst = icmp_Obj.dst

            if self.isRealIPAddress(src) and src not in self.HostAttachments.keys():
                self.HostAttachments[src] = datapath.id

            if self.isRealIPAddress(src):         
                match = parser.OFPMatch(eth_type=0x0800,in_port=in_port,ipv4_src=src,ipv4_dst=dst)
                ipSrc = self.R2V_Mappings[src]
                print("Changing SRC REAL IP " + src + "---> Virtual SRC IP " + ipSrc)
                actions.append(parser.OFPActionSetField(ipv4_src=ipSrc))

            if self.isVirtualIPAddress(dst):
                #print self.HostAttachments
                match = parser.OFPMatch(eth_type=0x0800,in_port=in_port,ipv4_dst=dst,ipv4_src=src)
                if self.isDirectContact(datapath=datapath.id,ipAddr=self.V2R_Mappings[dst]):
                    ipDst = self.V2R_Mappings[dst] 
                    print("Changing DST Virtual IP " + dst + "---> Real DST IP " + ipDst)
                    actions.append(parser.OFPActionSetField(ipv4_dst=ipDst))
            elif self.isRealIPAddress(dst):
                '''Learn From Flood'''
                match=parser.OFPMatch(eth_type=0x0806,in_port=in_port,arp_spa=src,arp_tpa=dst)
                if not self.isDirectContact(datapath=datapath.id,ipAddr=dst):
                    pktDrop = True
                    print("Dropping from",dpid)
            else:
                pktDrop = True

        '''Extract Ethernet Object from packet''' 
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        src = eth.src
        dst = eth.dst

        self.mac_to_port.setdefault(dpid, {})
        print("------------------------------------------")
        print("Add switch_", dpid, " to mac_to_port table")
        print("------------------------------------------")
        print("..")
        print("..")

        print("=================================")
        print("|        Packet In Event        |")
        print("=================================")
        print("dpid => ", dpid)
        print("src => ", src)
        print("dst => ", dst)
        print("in_port => ", in_port)
        print("-------------------------------------")
        print("..")
        print("..")

        self.mac_to_port[dpid][src] = in_port

        print("==================================")
        print("|        mac_to_port Table       |")
        print("==================================")

        print(self.mac_to_port)
        print("-----------------------------------------")
        print("..")
        print("..")

        '''Learning Mac implemention to avoid flood'''
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        '''Append the outport action to the action set'''
        if not pktDrop:
            actions.append(parser.OFPActionOutput(out_port))

        '''install a flow to avoid packet_in next time'''
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                print("========================")
                print("|    Add Flow Entry    |")
                print("========================")
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
                print("========================")
                print("|    Add Flow Entry    |")
                print("========================")
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
