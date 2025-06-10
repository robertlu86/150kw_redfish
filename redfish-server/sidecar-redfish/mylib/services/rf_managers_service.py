'''
這是Redfish的managers service
'''
import subprocess, json
from mylib.services.base_service import BaseService
from mylib.models.rf_networkprotocol_model import RfNetworkProtocolModel
from mylib.models.rf_snmp_model import RfSnmpModel
from mylib.adapters.webapp_api_adapter import WebAppAPIAdapter
from mylib.models.rf_resource_model import RfResetType

class RfManagersService(BaseService):
    # ================NetworkProtocol================
    def NetworkProtocol_service(self) -> dict:
        m = RfNetworkProtocolModel()
        m.HostName = "TBD"
        m.FQDN = "Null"
        return m.to_dict()
    
    def NetworkProtocol_service_patch(self, ntp):
        m = RfNetworkProtocolModel()
        if "NTPServers" in ntp:
            m.NTP["NTPServers"] = ntp["NTPServers"]
        return "test success"
    
    def NetworkProtocol_Snmp_get(self) -> dict:
        '''
        取得 SNMP 設定
        '''
        m = RfSnmpModel()
        return m.to_dict()
    
    def NetworkProtocol_Snmp_patch(self, body: dict) -> dict:
        """
        更新 SNMPServers 設定，只處理收到的欄位
        """
        np_current = RfNetworkProtocolModel().model_dump(by_alias=True, exclude_none=True)
        snmp_current = np_current.get("SNMP", {})
        trap_ip    = body.get("TrapIP", None)
        default_trap_port = snmp_current.get("Port", 162)
        default_enabled = snmp_current.get("ProtocolEnabled", False)
        # 取得前端是否有傳 TrapPort、TrapFormat、Enabled
        trap_port  = body.get("TrapPort", default_trap_port)
        community  = body.get("Community", None)
        trap_fmt   = body.get("TrapFormat", None)
        enabled    = body.get("Enabled", default_enabled)

        # 用傳進來的值，建立一個新的 RfSnmpModel 實例
        # 如果某個參數是 None，代表要用 Model 裡的 default
        new_model = RfSnmpModel(
            TrapIP    = trap_ip,
            TrapPort  = trap_port,
            Community = community,
            TrapFormat= trap_fmt,
            Enabled   = enabled
        )
        return new_model.model_dump(by_alias=True, exclude_none=True)

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
        resp = WebAppAPIAdapter.reset_to_defaults(reset_type)
        return resp
    
    def reset(self, reset_type: str):
        """
        :param reset_type: str
            e.g., "ForceRestart" or "GracefulRestart"
        """
        resp = WebAppAPIAdapter.reset(reset_type)
        return resp

    def shutdown(self, reset_type: str):
        resp = WebAppAPIAdapter.shutdown(reset_type)
        return resp