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
from mylib.models.rf_base_model import RfResourceBaseModel
from mylib.utils.network_info import get_network_protocol_status
from mylib.models.rf_snmp_model import rf_SNMP
# st = get_network_protocol_status()
class _rf_HTTPS(BaseModel):
    ProtocolEnabled: Optional[bool] = Field(default=True, example=True)
    Port: Optional[int] = Field(default=True)
    Certificates: Optional[Dict[str, Any]] = Field(default=None)

class _rf_DHCP(BaseModel):
    ProtocolEnabled: Optional[bool] = Field(default=True, example=True)
    Port: Optional[int] = Field(default=True)
    
class _rf_SSH(BaseModel):
    ProtocolEnabled: Optional[bool] = Field(default=True, example=True)
    Port: Optional[int] = Field(default=True, example="22")

# class _rf_SNMP(BaseModel):
#     ProtocolEnabled: Optional[bool] = Field(default=True, example=True)
#     Port: Optional[int] = Field(default=True)
#     # EnableSNMPv1: Optional[bool] = Field(default=None)
#     EnableSNMPv2c: Optional[bool] = Field(default=None)
#     EnableSNMPv3: Optional[bool] = Field(default=None)
#     CommunityStrings: Optional[List[Dict[str, Any]]] = Field(default=None)
    
class _rf_NTP(BaseModel):
    ProtocolEnabled: Optional[bool] = Field(default=True, example=True)
    Port: Optional[int] = Field(default=True)
    NTPServers: Optional[List[str]] = Field(default=True)   
    
class RfNetworkProtocolModel(RfResourceBaseModel):
    
    """
    Example:
    {
        "@odata.id": "/redfish/v1/Managers/CDU/NetworkProtocol",
        "@odata.type": "#ManagerNetworkProtocol.v1_8_0.ManagerNetworkProtocol",
        "@odata.context": "/redfish/v1/$metadata#ManagerNetworkProtocol.v1_8_0.ManagerNetworkProtocol",
        "Name": "Manager Network Protocol",
        "Id": "NetworkProtocol",
        "Description": "CDU Management Interface Network Protocol Settings",
        "HostName": "...",
        "FQDN": "...",
        "HTTPS": { "ProtocolEnabled": true, "Port": 443, "Certificates": [...] },
        "DHCP": { "ProtocolEnabled": true, "Port": 68 },
        "SSH": { "ProtocolEnabled": false, "Port": 22 },
        "SNMP": { "ProtocolEnabled": true, "Port": 161 },
        "NTP": { "ProtocolEnabled": true, "Port": 123, "Servers": ["0.pool.ntp.org"] },
        "Oem": { ... },

    }
    """
    odata_id: Optional[str] = Field(default="/redfish/v1/Managers/CDU/NetworkProtocol", alias="@odata.id")
    odata_type: Optional[str] = Field(
        default="#ManagerNetworkProtocol.v1_11_0.ManagerNetworkProtocol",
        alias="@odata.type",
    )
    odata_context: Optional[str] = Field(default="/redfish/v1/$metadata#ManagerNetworkProtocol.v1_11_0.ManagerNetworkProtocol", alias="@odata.context")
    
    Name: Optional[str] = Field(default="Manager Network Protocol")
    Id: Optional[str] = Field(default="NetworkProtocol")
    Description: Optional[str] = Field(default=None, description="")
    
    HostName: Optional[str] = Field(default=None, description="")
    FQDN: Optional[str] = Field(default=None, description="")
    
    HTTPS: Optional[_rf_HTTPS] = None
    DHCP: Optional[_rf_DHCP] = None
    SSH: Optional[_rf_SSH] = None
    SNMP: Optional[rf_SNMP] = None
    NTP: Optional[_rf_NTP] = None
    
    Oem: Optional[Dict[str, Any]] = Field(default=None, description="")
    
    
    model_config = ConfigDict(
        extra='allow',
        populate_by_name=True,
    )
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        st = get_network_protocol_status()
        self.HTTPS = _rf_HTTPS(
            ProtocolEnabled = st["HTTPSProtocolEnabled"],
            Port = st["HTTPSPort"],
            Certificates = {
                "@odata.id": "/redfish/v1/Managers/CDU/NetworkProtocol/HTTPS/Certificates"
            }    
        )
        self.SSH = _rf_SSH(
            ProtocolEnabled = st["SSHEnabled"],
            Port = st["HTTPPort"]
        )
        self.SNMP = rf_SNMP(
            ProtocolEnabled = st["SNMPEnabled"],
            Port = st["SNMPPort"],
            CommunityStrings= [
                {
                    "Name": "public",
                    "AccessMode": "Full"
                },
            ],
        )
        self.NTP = _rf_NTP(
            ProtocolEnabled = st["NTPEnabled"],
            Port = st["NTPPort"],
            NTPServers = st["NTPServers"] # 預設 NTP 伺服器
        )
        self.DHCP = _rf_DHCP(
            ProtocolEnabled = st["DHCPEnabled"],
            Port = st["DHCPPort"] 
        )
        self.Oem = {
            "Supermicro": {
                "Snmp":{
                    "@odata.id": "/redfish/v1/Managers/CDU/NetworkProtocol/Oem/Supermicro/SNMPServers",
                    "@odata.type": "#Supermicro.SMCManagerNetworkProtocolSnmp",              
                }
            }
        }

        
        
