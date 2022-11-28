# ============================================
# ||        基本Ryu Switch Conreoller       ||
# ============================================

# 匯入Ryu基本組件模組 | Ryu app核心管理組件
from ryu.base import app_manager
# 匯入控制器模組 | OpenFlow事件定義組件
from ryu.controller import ofp_event
# 匯入事件處理模組 | Switch 配發模式組件
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
# 匯入事件處理模組 | 事件監聽組件
from ryu.controller.handler import set_ev_cls
# 匯入OpenFlow有線協議模組 | OpenFlow 1.3版本定義解析組件
from ryu.ofproto import ofproto_v1_3
# 匯入流行協議(如TCP/IP)之解析器實現模組 | 封包組件
from ryu.lib.packet import packet
# 匯入流行協議(如TCP/IP)之解析器實現模組 | 乙太網路協定組件
from ryu.lib.packet import ethernet

class RandomHostMutation_Switch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *_args, **_kwargs):
        '''
            << Constructor >> :
                1. 用來初始化成員變數。
        '''
        # 繼承 RyuApp 類別並初始化 RyuApp 之初始設置
        super(RandomHostMutation_Switch, self).__init__(*_args, **_kwargs)
        # 基於ARP協議，紀錄學習實體位址(Mac Address)與端口(port)之對映關係表
        self.mac_to_port = {}
    
    # 引入事件監聽器，
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        '''
            << Switch 功能處理器 >> : 
                1. 處理由 switch 發送到 controller 的 switch feature 事件。
                2. switch 發送協商訊息。
                3. 我們儲存 switch 訊息到 datapath 成員變數。
                4. 新增 miss flow entry table 到 switch 中。
        '''
        # 獲取事件來自發送方switch與接收方controller之間的連接描述 => datapath
        datapath = ev.msg.datapath
        # 獲取Openflow協議實例與解析器
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # 設置match配對為任何來源
        match = parser.OFPMatch()
        # 設置操作動作將所有數據包輸出到controller端口
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

        # 增加優先權為0(最低優先權)之Table-miss Flow Entry
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        '''
            << 流表生產器 >> :
                1. 新增流表規則至 Switch。
        '''
        # 獲取Openflow協議實例與解析器
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # 設置包含操作動做參數且為新增類型的流表指令
        inst = [parser.OFPInstructions(ofproto.OFPIT_APPLY_ACTIONS,
                                       actions)]

        # Controller依照所設置的參數來調整流表
        mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                match=match, instructions=inst)
        # Controller向Switch下達新的流表訊息
        datapath.send_msg(mod)

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
        print("|        Packet In Event        |")
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
