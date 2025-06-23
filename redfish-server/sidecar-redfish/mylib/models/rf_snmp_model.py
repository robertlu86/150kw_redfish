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

class rf_SNMP(BaseModel):
    '''
    NetworkProtocol Snmp 的 model
    "ProtocolEnabled": true, //必填：啟用 SNMP，不能省略
    "Port": 161,                     // 必填：使用 通常161
    
    // 以下都是 Optional，只在需要時才放：
    "EnableSNMPv1": false,           // 是否啟用 v1；如果不需要，就不放
    "EnableSNMPv2c": true,           // 啟用 v2c
    "EnableSNMPv3": false,           // 不啟用 v3

    // 社群字串 (v1/v2c)：
    "CommunityStrings": [
        {
        "Name": "public",
        "AccessMode": "ReadOnly"
        },
        {
        "Name": "private",
        "AccessMode": "ReadWrite"
        }
    ],
    // 如果想隱藏上面社群字串，避免使用 GET 看到明碼，可設定：
    "HideCommunityStrings": true,

    // SNMP v3 如果想用驗證／加密，才需要接下來這幾個：
    "EngineId": "80001F8880E9630000001234567890AB",  // SNMPv3 引擎ID
    "AuthenticationProtocol": "SHA",                 // SNMPv3 驗證協定
    "EncryptionProtocol": "AES",                     // SNMPv3 加密協定

    // 可選：針對所有 community 的預設存取模式（如果不想在 CommunityStrings 裡逐一寫，也能用此欄位覆蓋）：
    "CommunityAccessMode": "ReadOnly"
    '''
    ProtocolEnabled: Optional[bool] = Field(default=True, example=True, description="Indicates if SNMP protocol is enabled.")
    Port: Optional[int] = Field(default=True, example=161, description="The port number for SNMP protocol.")
    TrapPort: Optional[int] = Field(default=None, example=162, description="The port number for SNMP traps, if applicable.")
    # 是否啟用 SNMPv1, SNMPv2c, SNMPv3
    EnableSNMPv1: Optional[bool] = Field(default=None, description="Indicates if SNMPv1 is enabled.")
    EnableSNMPv2c: Optional[bool] = Field(default=None, description="Indicates if SNMPv2c is enabled.")
    EnableSNMPv3: Optional[bool] = Field(default=None, description="Indicates if SNMPv3 is enabled.")
    # 社群字串 (v1/v2c)
    CommunityStrings: Optional[List[Dict[str, Any]]] = Field(default=None, description="List of SNMP community strings, each with its own properties.")
    HideCommunityStrings: Optional[bool] = Field(default=None, description="Indicates if community strings should be hidden from GET requests.")
    # SNMP v3 相關設定
    EngineId: Optional[str] = Field(default=None, description="SNMPv3 Engine ID.")
    AuthenticationProtocol: Optional[str] = Field(default=None, description="SNMPv3 authentication protocol.")
    EncryptionProtocol: Optional[str] = Field(default=None, description="SNMPv3 encryption protocol.")
    # 預設存取模式
    CommunityAccessMode: Optional[str] = Field(default=None, description="Default access mode for all community strings.")
    Oem: Optional[Dict[str, Any]] = Field(default=None, description="OEM specific properties.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ProtocolEnabled = kwargs.get("ProtocolEnabled", False)
        self.Port = kwargs.get("Port", 9000)




class RfSnmpModel(RfResourceBaseModel):
    class _SnmpServers(BaseModel):
        '''
        SNMP server configuration details.
        Example:
            {
                "TrapIp": "127.0.0.1",
                "TrapPort": 162,
                "Community": "public",
                "TrapFormat": "v2c",
                "Enabled": true
            }
        '''
        TrapIP: Optional[str] = Field(default="127.0.0.1", description="The IP address of the SNMP trap server.")
        TrapPort: Optional[int] = Field(default=162, description="The port number for the SNMP trap server.")
        Community: Optional[str] = Field(default="public", description="The community string for the SNMP trap server.")
        TrapFormat: Optional[str] = Field(default="v2c", description="The trap format for the SNMP trap server.")
        Enabled: Optional[bool] = Field(default=True, description="Indicates if the SNMP trap server is enabled.")
    '''
    snmp_servers_data = {
        "@odata.id": "/redfish/v1/Managers/CDU/NetworkProtocol/Oem/Supermicro/SNMPServers",
        "@odata.type": "#Supermicro.SMCManagerNetworkProtocolSnmp",
        "SnmpServers": {
            "TrapIp": "127.0.0.1",
            "TrapPort": 162,
            "Community": RfManagersService().NetworkProtocol_service()["SNMP"]["CommunityStrings"][0]["Name"],
            "TrapFormat": "v2c",
            "Enabled": RfManagersService().NetworkProtocol_service()["SNMP"]["ProtocolEnabled"]
        }    
    '''
    odata_id: Optional[str] = Field(default="/redfish/v1/Managers/CDU/NetworkProtocol/Oem/Supermicro/SNMPServers", alias="@odata.id")
    odata_type: Optional[str] = Field(default="#Supermicro.SMCManagerNetworkProtocolSnmp",alias="@odata.type",)
    SnmpServers: Optional[_SnmpServers] = Field(default=True, description="SNMP server configuration details.")
    
    model_config = ConfigDict(
        extra='allow',
    )

    def __init__(self, 
        TrapIP: Optional[str] = None,
        TrapPort: Optional[int]  = None,
        Community: Optional[str] = None,
        TrapFormat: Optional[str]= None,
        Enabled: Optional[bool]  = None, 
        **kwargs
    ):
        super().__init__(**kwargs)
        self.SnmpServers = self._SnmpServers(
            TrapIP    = TrapIP    if TrapIP    is not None else self._SnmpServers.__fields__['TrapIP'].default,
            TrapPort  = TrapPort  if TrapPort  is not None else self._SnmpServers.__fields__['TrapPort'].default,
            Community = Community if Community is not None else self._SnmpServers.__fields__['Community'].default,
            TrapFormat= TrapFormat if TrapFormat is not None else self._SnmpServers.__fields__['TrapFormat'].default,
            Enabled   = Enabled   if Enabled   is not None else self._SnmpServers.__fields__['Enabled'].default,
        )

    
