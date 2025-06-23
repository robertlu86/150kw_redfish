'''
@see https://redfish.dmtf.org/schemas/v1/Pump.v1_2_0.json
'''
import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pydantic import (
    BaseModel,
    ConfigDict,
    Field, 
    computed_field,
    model_validator,
    #validator, # deprecated
    field_validator,
)
from typing_extensions import Self
from enum import Enum
from mylib.models.rf_base_model import RfResourceBaseModel
# from mylib.models.rf_software_inventory_model import RfAdditionalVersions
# from mylib.models.rf_actions_model import RfActions
# from mylib.models.rf_certificates_model import RfCertificates
# from mylib.models.rf_command_shell_model import RfCommandShell
# from mylib.models.rf_dedicated_network_ports_model import RfDedicatedNetworkPorts
# from mylib.models.rf_ethernet_interfaces_model import RfEthernetInterfaces
# from mylib.models.rf_graphical_console_model import RfGraphicalConsole
# from mylib.models.rf_host_interfaces_model import RfHostInterfaces
# from mylib.models.rf_links_model import RfLinks
# from mylib.models.rf_location_model import RfLocation
# from mylib.models.rf_log_services_model import RfLogServices
# from mylib.models.rf_manager_diagnostic_data_model import RfManagerDiagnosticData
# from mylib.models.rf_measurements_model import RfMeasurements
# from mylib.models.rf_network_protocol_model import RfNetworkProtocol
# from mylib.models.rf_serial_console_model import RfSerialConsole
# from mylib.models.rf_serial_interfaces_model import RfSerialInterfaces
# from mylib.models.rf_service_identification_model import RfServiceIdentification
# from mylib.models.rf_shared_network_ports_model import RfSharedNetworkPorts
from mylib.models.rf_status_model import RfStatusModel
# from mylib.models.rf_virtual_media_model import RfVirtualMedia
# from mylib.models.rf_usb_ports_model import RfUSBPorts
from mylib.utils.system_info import get_system_uuid
from load_env import hardware_info, redfish_info
from mylib.utils.load_api import load_raw_from_api ,CDU_BASE





class RfResetToDefaultsType(Enum):
    """
    @see https://redfish.dmtf.org/schemas/v1/Manager.v1_21_0.json#/definitions/ResetToDefaultsType
    """
    ResetAll = "ResetAll"
    PreserveNetwork = "PreserveNetwork"
    PreserveNetworkAndUsers = "PreserveNetworkAndUsers"

class RfResetModel(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Manager.v1_21_0.json#/definitions/Reset
    """
    target: str = Field(default=None)
    title: str = Field(default=None)

class RfResetToDefaultsModel(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Manager.v1_21_0.json#/definitions/ResetToDefaults
    """
    target: str = Field(default=None)
    title: str = Field(default=None)
    
   


class RfManagerModel(RfResourceBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Manager.v1_21_0.json
    @note properties 55 items
    """
    class _actions(BaseModel):
        Reset: Optional[RfResetModel] = Field(default=None)
        ResetToDefaults: Optional[RfResetToDefaultsModel] = Field(default=None)
        # Oem: Optional[RfOemActions] = Field(default=None)
    
    
    Odata_context: Optional[str] = Field(default=None, alias="@odata.context")
    Description: Optional[str] = Field(default=None)
    Odata_etag: Optional[str] = Field(default=None, alias="@odata.etag")
    # "@odata.id": {1 item},
    # "@odata.type": {1 item},
    
    Manufacturer: Optional[str] = Field(default=None)
    Model: Optional[str] = Field(default=None)
    PartNumber: Optional[str] = Field(default=None)
    SerialNumber: Optional[str] = Field(default=None)
    PowerState: Optional[str] = Field(default=None)
    UUID: Optional[str] = Field(default=None)
    Version: Optional[str] = Field(default=None)
    FirmwareVersion: Optional[str] = Field(default=None)
    # AdditionalFirmwareVersions: Optional[RfAdditionalVersions] = Field(default=None)
    AutoDSTEnabled: Optional[bool] = Field(default=None)
    # Certificates: Optional[RfCertificates] = Field(default=None)
    # CommandShell: Optional[RfCommandShell] = Field(default=None)
    DateTime: Optional[str] = Field(default=None)
    TimeZoneName: Optional[str] = Field(default=None)
    DateTimeLocalOffset: Optional[str] = Field(default=None)
    DateTimeSource: Optional[str] = Field(default=None)
    DaylightSavingTime: Optional[str] = Field(default=None)
    LastResetTime: Optional[str] = Field(default=None)
    # DedicatedNetworkPorts: Optional[RfDedicatedNetworkPorts] = Field(default=None)

    # GraphicalConsole: Optional[RfGraphicalConsole] = Field(default=None)
    HostInterfaces: Optional[Dict[str, Any]] = Field(default=None)
    EthernetInterfaces: Optional[Dict[str, Any]] = Field(default=None)
    LogServices: Optional[Dict[str, Any]] = Field(default=None)
    NetworkProtocol: Optional[Dict[str, Any]] = Field(default=None)
    
    Links: Optional[Dict[str, Any]] = Field(default=None)
    # Location: Optional[RfLocation] = Field(default=None)
    LocationIndicatorActive: Optional[bool] = Field(default=None)
    # ManagerDiagnosticData: Optional[RfManagerDiagnosticData] = Field(default=None)
    ManagerType: Optional[str] = Field(default=None)
    # Measurements: Optional[RfMeasurements] = Field(default=None)
    OEMSecurityMode: Optional[str] = Field(default=None)
    # Redundancy: Optional[RfRedundancy] = Field(default=None)
    # Redundancy@odata.count: Optional[int] = Field(default=None)
    # RemoteAccountService: Optional[RfRemoteAccountService] = Field(default=None)
    RemoteRedfishServiceUri: Optional[str] = Field(default=None)
    SecurityMode: Optional[str] = Field(default=None)
    # SecurityPolicy: Optional[RfSecurityPolicy] = Field(default=None)
    # SerialConsole: Optional[RfSerialConsole] = Field(default=None)
    # SerialInterfaces: Optional[RfSerialInterfaces] = Field(default=None)
    ServiceEntryPointUUID: Optional[str] = Field(default=None)
    ServiceIdentification: Optional[str] = Field(default=None)
    # SharedNetworkPorts: Optional[RfSharedNetworkPorts] = Field(default=None)
    SparePartNumber: Optional[str] = Field(default=None)
    Status: Optional[RfStatusModel] = Field(default=None)
    # USBPorts: Optional[RfUSBPorts] = Field(default=None)
    # VirtualMedia: Optional[RfVirtualMedia] = Field(default=None)
    WriteableProperties: Optional[List[str]] = Field(default=None, alias="@Redfish.WriteableProperties")
    Actions: Optional[_actions] = Field(default=None)
    Oem: Optional[Dict[str, Any]] = Field(default=None)
    

    model_config = ConfigDict(
        extra='allow',
        # arbitrary_types_allowed=True
    )

    def __init__(self, cdu_id: str, **kwargs):
        super().__init__(**kwargs)
        self.odata_id = f"/redfish/v1/Managers/{cdu_id}"
        self.odata_type = "#Manager.v1_21_0.Manager"
        self.Odata_context = "/redfish/v1/$metadata#Manager.v1_21_0.Manager"
        
        self.Id = cdu_id
        self.Name = "CDU Network Interface Module"
        self.Description = "Cooling Distribution Unit Management Module"
        
        self.Manufacturer = hardware_info.get("CDU", {}).get("Manufacturer")
        self.PartNumber = hardware_info.get("CDU", {}).get("PartNumber")
        self.Model = hardware_info.get("CDU", {}).get("Model")
        self.FirmwareVersion = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/display/version")["version"]["WebUI"]
        self.SerialNumber = hardware_info.get("CDU", {}).get("SerialNumber") + load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/display/version")["fw_info"]["SN"]
        self.UUID = get_system_uuid()
        
        # status
        heath = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/mc")["cdu_status"]
        self.Status = RfStatusModel(State="Enabled", Health=heath)

        # other
        self.ServiceIdentification = redfish_info.get("Managers/cdu", {}).get("ServiceIdentification")
        self.LogServices = {"@odata.id": f"/redfish/v1/Managers/{cdu_id}/LogServices"}
        self.NetworkProtocol = {"@odata.id": f"/redfish/v1/Managers/{cdu_id}/NetworkProtocol"}
        self.EthernetInterfaces = {"@odata.id": f"/redfish/v1/Managers/{cdu_id}/EthernetInterfaces"}
        self.HostInterfaces = {"@odata.id": f"/redfish/v1/Managers/{cdu_id}/HostInterfaces"}
        self.Links = {"Oem": {}}
        Reset = {
            "target": "/redfish/v1/Managers/CDU/Actions/Manager.Reset",
            "ResetType@Redfish.AllowableValues": [
                "ForceRestart",
                "GracefulRestart"
            ]}
        ResetToDefaults = {
            "target": "/redfish/v1/Managers/CDU/Actions/Manager.ResetToDefaults",
            "ResetType@Redfish.AllowableValues": [
                "ResetAll"
            ]
        }
        self.Actions = self._actions(Reset=RfResetModel(**Reset), ResetToDefaults=RfResetToDefaultsModel(**ResetToDefaults))