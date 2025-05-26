import os
import platform
from mylib.services.base_service import BaseService

class DebugService(BaseService):
    def __init__(self):
        super().__init__()

    def load_report(self):
        return {
            "listen_ports": self.report_all_listen_ports(),
            "redfish_api": self.try_redfish_api(),
            "restapi": self.try_restapi(),
            "redfish_api_Sensor_Fan1": self.try_redfish_api_Sensor_Fan1(),
            "redfish_api_PrimaryFlowLitersPerMinute": self.try_redfish_api_PrimaryFlowLitersPerMinute(),
            "ls_al_service": self.report_ls_al_service(),
            "ls_al_service_RestAPI": self.report_ls_al_service_RestAPI(),
            "ls_al_service_sidecar_redfish": self.report_ls_al_service_sidecar_redfish(),
        }

    

    def report_all_listen_ports(self):
        if platform.system() == 'Linux':
            return self.exec_command("netstat -ltnp")
        elif platform.system() == 'Darwin':  # macOS
            return self.exec_command("lsof -i -P | grep LISTEN")
        elif platform.system() == 'Windows':
            return self.exec_command("netstat -ltnp")

    def report_ls_al_service(self):
        return self.exec_command("ls -al /home/user/service/")
    
    def report_ls_al_service_RestAPI(self):
        return self.exec_command("ls -al /home/user/service/RestAPI/")
    
    def report_ls_al_service_sidecar_redfish(self):
        return self.exec_command("ls -al /home/user/service/redfish-server/sidecar-redfish")

    def _build_curl_get_command(self, uri):
        return f"curl -k '{uri}' -H 'accept: application/json' -u admin:admin --connect-timeout 5"

    def try_redfish_api(self):
        return self.exec_command(self._build_curl_get_command("https://127.0.0.1:5101/redfish/v1/"))
    
    def try_redfish_api_Sensor_Fan1(self):
        return self.exec_command(self._build_curl_get_command("https://127.0.0.1:5101/redfish/v1/Chassis/1/Sensors/Fan1"))

    def try_redfish_api_PrimaryFlowLitersPerMinute(self):
        return self.exec_command(self._build_curl_get_command("https://127.0.0.1:5101/redfish/v1/Chassis/1/Sensors/PrimaryFlowLitersPerMinute"))

    def try_restapi(self):
        return self.exec_command(self._build_curl_get_command("http://127.0.0.1:5001/api/v1/cdu"))

    
        