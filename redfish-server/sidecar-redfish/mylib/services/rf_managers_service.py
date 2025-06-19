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

class RfManagersService(BaseService):
    # =================通用工具===================
    def save_networkprotocol(self, servie: str, setting):
        SettingModel().save_key_value(f"Managers.{servie}.ProtocolEnabled", setting["ProtocolEnabled"])
        SettingModel().save_key_value(f"Managers.{servie}.Port", setting["Port"])
    
    def get_networkprotocol(self, servie: str, setting):
        SettingModel().get_by_key(f"Managers.{servie}.ProtocolEnabled", setting["ProtocolEnabled"])
        SettingModel().get_by_key(f"Managers.{servie}.Port", setting["Port"])        
    # ================NetworkProtocol================
    def NetworkProtocol_service(self) -> dict:
        m = RfNetworkProtocolModel()
        m.HostName = "TBD"
        m.FQDN = None
        return m.to_dict()
    
    def NetworkProtocol_service_patch(self, body):
        snmp_setting ={
            "ProtocolEnabled": body["SNMP"]["ProtocolEnabled"],
            "Port": 9001
        } 
        
        m = RfNetworkProtocolModel()
        self.save_networkprotocol("SNMP", snmp_setting)
        return m.to_dict(), 200
    
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