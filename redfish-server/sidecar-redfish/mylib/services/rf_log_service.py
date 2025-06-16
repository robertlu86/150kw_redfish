'''
這是Redfish的managers service
'''
import os
import datetime
import subprocess, json
from load_env import redfish_info
from http import HTTPStatus
from mylib.services.base_service import BaseService
from mylib.models.rf_networkprotocol_model import RfNetworkProtocolModel
from mylib.models.rf_snmp_model import RfSnmpModel
from mylib.adapters.webapp_api_adapter import WebAppAPIAdapter
from mylib.models.rf_resource_model import RfResetType
from mylib.models.rf_log_service_model import (
    RfLogServiceCollectionModel, 
    RfLogServiceModel, 
    RfLogEntryType, 
    RfOverWritePolicy
)
from mylib.models.rf_status_model import RfStatusModel, RfStatusHealth, RfStatusState
from mylib.utils.DateTimeUtil import DateTimeUtil
from mylib.common.proj_error import ProjError
from mylib.adapters.webapp_json_reader import WebAppJsonReader

class RfLogService(BaseService):
    def fetch_LogServices(self):
        """
        Example:
        {
            "@odata.id": "/redfish/v1/Managers/CDU/LogServices",
            "@odata.type": "#LogServiceCollection.LogServiceCollection",
            "@odata.context": "/redfish/v1/$metadata#LogServiceCollection.LogServiceCollection",

            "Name": "Log Service",
            "Description": "System Event and Error Log Service",
            
            "Members@odata.count": 1,
            "Members": [
                {"@odata.id": "/redfish/v1/Managers/CDU/LogServices/1"}
            ],
            "Oem": {}
        }
        """
        m = RfLogServiceCollectionModel()
        m.odata_id = "/redfish/v1/Managers/CDU/LogServices"
        m.odata_type = "#LogServiceCollection.LogServiceCollection"
        m.odata_context = "/redfish/v1/$metadata#LogServiceCollection.LogServiceCollection"
        m.Name = "Log Service"
        m.Description = "System Event and Error Log Service"

        m.Members = []
        for key, obj in redfish_info["LogServices"].items():
            m.Members.append({
                "@odata.id": f"/redfish/v1/Managers/CDU/LogServices/{key}"
            })
        m.Members_odata_count = len(m.Members)

        return m.to_dict()

    def fetch_LogServices_with_id(self, log_id: str):
        """
        對應URI: /redfish/v1/Managers/CDU/LogServices/{log_id}
        """
        if log_id != "1":
            raise ProjError(HTTPStatus.NOT_FOUND.value, f"LogService {log_id} is not exist!")
        
        log_entries = WebAppJsonReader.read_all_errorlog_entries()

        status = RfStatusModel()
        status.State = RfStatusState.Enabled
        if len(log_entries) >= 500:
            status.Health = RfStatusHealth.OK
        if len(log_entries) == 0:
            status.Health = RfStatusHealth.Critical
        else:
            status.Health = RfStatusHealth.Warning

        # TODO: 專案太趕，先不建rf_log_service_model
        LogServices_id_data = {
            "@odata.id": f"/redfish/v1/Managers/CDU/LogServices/{log_id}",
            "@odata.type": "#LogService.v1_8_0.LogService",
            "@odata.context": "/redfish/v1/$metadata#LogService.v1_8_0.LogService",

            "Id": str(log_id),
            "Name": "System Event Log Service",
            "Description": "System Event and Error Log Service",
            
            "Entries": { "@odata.id": f"/redfish/v1/Managers/CDU/LogServices/{log_id}/Entries" },
            "LogEntryType": RfLogEntryType.OEM,
            "DateTime": DateTimeUtil.format_string(os.getenv("DATETIME_FORMAT", "%Y-%m-%dT%H:%M:%SZ")),
            "DateTimeLocalOffset": DateTimeUtil.parse_timezone(datetime.datetime.now(), ':'), # '+08:00'
            "MaxNumberOfRecords": len(log_entries),
            "OverWritePolicy": RfOverWritePolicy.WrapsWhenFull,
            "ServiceEnabled": True,
            "Status": status.to_dict(),
            
            # Recommended field in interop validator
            # "Actions": {
            #     "#LogService.ClearLog": {
            #         "target": f"/redfish/v1/Managers/CDU/LogServices/{log_id}/Actions/LogService.ClearLog",
            #     }
            # },
            "Oem": {}
        }

        return LogServices_id_data