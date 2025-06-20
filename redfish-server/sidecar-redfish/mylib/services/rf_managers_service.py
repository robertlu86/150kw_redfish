'''
這是Redfish的managers service
'''
import subprocess, json
import requests
from flask import jsonify
from mylib.services.base_service import BaseService
from mylib.models.rf_networkprotocol_model import RfNetworkProtocolModel
from mylib.models.rf_snmp_model import RfSnmpModel
from mylib.adapters.webapp_api_adapter import WebAppAPIAdapter
from mylib.models.rf_resource_model import RfResetType
from mylib.common.proj_response_message import ProjResponseMessage
from mylib.models.setting_model import SettingModel
from mylib.utils.load_api import load_raw_from_api, CDU_BASE
from mylib.utils.system_info import get_physical_nics
from mylib.models.rf_ethernetinterfaces_model import RfEthernetInterfacesModel, RfEthernetInterfacesIdModel
from mylib.models.rf_status_model import RfStatusModel

class RfManagersService(BaseService):
    # =================通用工具===================
    def save_networkprotocol(self, servie: str, setting):
        SettingModel().save_key_value(f"Managers.{servie}.ProtocolEnabled", setting["ProtocolEnabled"])
        SettingModel().save_key_value(f"Managers.{servie}.Port", setting["Port"])
    
    def get_networkprotocol(self, servie: str):
        # SettingModel().get_by_key(f"Managers.{servie}.ProtocolEnabled")
        # SettingModel().get_by_key(f"Managers.{servie}.Port")  
        return {"ProtocolEnabled": bool(int(SettingModel().get_by_key(f"Managers.{servie}.ProtocolEnabled").value)), "Port": int(SettingModel().get_by_key(f"Managers.{servie}.Port").value)}
            
        
    def get_ethernet_data(self):
        return get_physical_nics()      
    
    def get_ethernet_entry(self, target_name, data):
        entry = next((item for item in data if item['Name'] == target_name), None)
        return entry
    
    def net_info(self, interfaces): # 暫放
        print(f"共 {len(interfaces)} 張實體網卡：")
        for iface in interfaces:
            print(f"\n名稱: {iface['Name']}")
            print(f"  MAC            : {iface['MAC']}")
            print(f"  IPv4           : {iface['IPv4']}")
            print(f"  IPv6           : {iface['IPv6']}")
            print(f"  Speed (Mbps)   : {iface['Speed_Mbps']}")
            print(f"  MTU            : {iface['MTU']}")
            print(f"  Full Duplex    : {iface['FullDuplex']}")
            print(f"  Is Up          : {iface['isUp']}")
    # ================NetworkProtocol================
    def NetworkProtocol_service(self) -> dict:
        m = RfNetworkProtocolModel()
        m.HostName = "TBD"
        m.FQDN = "null"
        m.SNMP = self.get_networkprotocol("SNMP")
        
        return m.to_dict()
    
    def NetworkProtocol_service_patch(self, body):
        ProtocolEnabled = 1 if body["SNMP"]["ProtocolEnabled"] else 0
        snmp_setting ={
            "ProtocolEnabled": ProtocolEnabled,
            "Port": 9000
        } 
        
        self.save_networkprotocol("SNMP", snmp_setting)
        return self.NetworkProtocol_service(), 200
    
    def NetworkProtocol_Snmp_get(self) -> dict:
        '''
        取得 SNMP 設定
        '''
        snmp_data = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/Snmp")
        m = RfSnmpModel(
            TrapIP = snmp_data["trap_ip_address"],
            Community = snmp_data["read_community"]
        )
        

        return m.to_dict()
       
    def NetworkProtocol_Snmp_Post(self, body: dict) -> dict:
        trap_ip_address = body["TrapIP"]
        read_community = body["Community"]
        data = {
            "trap_ip_address": trap_ip_address,
            "read_community":  read_community
        }

        try:
            r = WebAppAPIAdapter().setting_snmp(data)
            return jsonify({ "message": r.text })      
            # return r.json(), r.status_code
        except requests.HTTPError:
            # 如果 CDU 回了 4xx/5xx，直接把它的 status code 和 body 回來
            try:
                err_body = r.json()
            except ValueError:
                err_body = {"error": r.text}
            return err_body, r.status_code

        except requests.RequestException as e:
            # 純粹網路／timeout／連線失敗
            return {
                "error": "Forwarding to the CDU control service failed",
                "details": str(e)
            }, 502  
            
    # ================動態抓取本機網路(內網外網要分)================    
    # def get_ethernetinterfaces(self):
    #     net_data = self.get_ethernet_data()
        
    #     m = RfEthernetInterfacesModel()
    #     m.Members_odata_count = len(net_data)
    #     for i in range(len(net_data)):
    #         s = {
    #             "@odata.id": f"redfish/v1/Managers/CDU/EthernetInterfaces/{net_data[i]['Name']}"
    #         }
            
    #         m.Members.append(s)
        
    #     return m.to_dict(), 200
    
    # def get_ethernetinterfaces_id(self, id: str):
    #     net_data_from_rest = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/network")
    #     print(net_data_from_rest)
    #     print(len(net_data_from_rest))
    #     m = RfEthernetInterfacesIdModel(ethernet_interfaces_id=id)
    #     net_data = self.get_ethernet_data() 
    #     data = self.get_ethernet_entry(id, net_data)
    #     self.net_info(net_data) # 測試使用
    #     if data is None:
    #         return {"message": f"Ethernet interface {id} not found"}, 404
    #     m.LinkStatus = "LinkUp" if data["isUp"] else "LinkDown"
    #     m.InterfaceEnabled = data["isUp"]
    #     m.MACAddress = data["MAC"]
    #     m.SpeedMbps = data["Speed_Mbps"]
    #     m.FullDuplex = data["FullDuplex"]
    #     m.MTUSize = data["MTU"]
        
    #     m.Redfish_WriteableProperties = ["InterfaceEnabled"]
    #     m.HostName = id
    #     m.FQDN = None
    #     # Ipv4
    #     Ipv4 = RfEthernetInterfacesIdModel._ipv4_addresses()
    #     Ipv4.Address = data["IPv4"]
    #     Ipv4.SubnetMask = "255.255.255.0" #TBD
    #     Ipv4.AddressOrigin = "DHCP" #TBD
    #     Ipv4.Gateway = "192.168.3.1" #TBD
        
    #     m.IPv4Addresses = Ipv4 
    #     m.NameServers = ["8.8.8.8" ]#TBD
        
    #     status = {
    #         "State": "Enabled",
    #         "Health": "OK"
    #     }
    #     m.Status = RfStatusModel.from_dict(status)
    #     return m.to_dict(), 200
    

    ##
    #      ___        ______ .___________. __    ______   .__   __.      _______.
    #     /   \      /      ||           ||  |  /  __  \  |  \ |  |     /       |
    #    /  ^  \    |  ,----'`---|  |----`|  | |  |  |  | |   \|  |    |   (----`
    #   /  /_\  \   |  |         |  |     |  | |  |  |  | |  . `  |     \   \
    #  /  _____  \  |  `----.    |  |     |  | |  `--'  | |  |\   | .----)   |
    # /__/     \__\  \______|    |__|     |__|  \______/  |__| \__| |_______/
    ##

    def reset_to_defaults(self, reset_type: str):
        """
        :param reset_type: str
            e.g., "ResetAll"
        @note:
            API will return jsonify(message="Reset all to factory settings Successfully")
        """
        resp = WebAppAPIAdapter().reset_to_defaults(reset_type)
        return jsonify(ProjResponseMessage(code=resp.status_code, message=resp.text).to_dict())
    
    def reset(self, reset_type: str):
        """
        :param reset_type: str
            e.g., "ForceRestart" or "GracefulRestart"
        """
        resp = WebAppAPIAdapter().reset(reset_type)
        return jsonify(ProjResponseMessage(code=resp.status_code, message=resp.text).to_dict())

    def shutdown(self, reset_type: str):
        resp = WebAppAPIAdapter().shutdown(reset_type)
        return jsonify(ProjResponseMessage(code=resp.status_code, message=resp.text).to_dict())