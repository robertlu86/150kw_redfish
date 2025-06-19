from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import (
    BaseModel,
    Field, 
    computed_field,
    model_validator,
    #validator, # deprecated
    field_validator,
)
from mylib.models.rf_base_model import RfResourceBaseModel, RfResourceCollectionBaseModel
from mylib.models.rf_log_entry_model import RfLogEntryCollectionModel
from mylib.models.rf_status_model import RfStatusModel


class RfClearLog(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/ClearLog
    """
    target: Optional[str] = Field(default=None, description="Link to invoke action")
    title: Optional[str] = Field(default=None, description="Friendly action name")

class RfCollectDiagnosticData(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/CollectDiagnosticData
    """
    target: Optional[str] = Field(default=None, description="Link to invoke action")
    title: Optional[str] = Field(default=None, description="Friendly action name")

class RfPushDiagnosticData(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/PushDiagnosticData
    """
    target: Optional[str] = Field(default=None, description="Link to invoke action")
    title: Optional[str] = Field(default=None, description="Friendly action name")


class RfActions(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/Actions
    """
    LogService_ClearLog: Optional[RfClearLog] = Field(default=None, alias="#LogService.ClearLog")
    LogService_CollectDiagnosticData: Optional[RfCollectDiagnosticData] = Field(default=None, alias="#LogService.CollectDiagnosticData")
    LogService_PushDiagnosticData: Optional[RfPushDiagnosticData] = Field(default=None, alias="#LogService.PushDiagnosticData")
    Oem: Optional[Dict[str, Any]] = Field(default=None)

class RfLogEntryTypes(str, Enum):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/LogEntryTypes
    """
    Event    = "Event"    # "The log contains CXL log entries."
    SEL      = "SEL"      # "The log contains Redfish-defined messages."
    Multiple = "Multiple" # "The log contains multiple log entry types and, therefore, the log service cannot guarantee a single entry type."
    OEM      = "OEM"      # "The log contains entries in an OEM-defined format."
    CXL      = "CXL"      # "The log contains legacy IPMI System Event Log (SEL) entries."

class RfOverWritePolicy(str, Enum):
    """
    
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/OverWritePolicy
    
    "description": "The overwrite policy for this service that takes place when the log is full.",
    "longDescription": "This property shall indicate the policy of the log service when the `MaxNumberOfRecords` has been reached.",
    
    """
    Unknown         = "Unknown"         # "The overwrite policy is not known or is undefined."
    WrapsWhenFull   = "WrapsWhenFull"   # "When full, new entries to the log overwrite earlier entries."
    NeverOverWrites = "NeverOverWrites" # "When full, new entries to the log are discarded."


class RfTransferProtocolType(str, Enum):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/TransferProtocolType
    """
    CIFS     = "CIFS"
    FTP      = "FTP"
    SFTP     = "SFTP"
    HTTP     = "HTTP"
    HTTPS    = "HTTPS"
    NFS      = "NFS"
    SCP      = "SCP"
    TFTP     = "TFTP"
    OEM      = "OEM"

class RfAutoClearResolvedEntries(str, Enum):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/AutoClearResolvedEntries
    """
    ClearEventGroup = "ClearEventGroup"
    RetainCauseResolutionEntries = "RetainCauseResolutionEntries"
    UpdateCauseEntry = "UpdateCauseEntry"
    _None = "None" # `None` is preserved word in Python!
    
class RfLogServiceCollectionModel(RfResourceCollectionBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogServiceCollection.json
    """
    # 所有欄位都同 RfResourceCollectionBaseModel 
    pass


class RfLogDiagnosticDataTypes(str, Enum):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/DiagnosticDataTypes
    @description: 
        "Device": "Device diagnostic data.",
        "Manager": "Manager diagnostic data.",
        "OEM": "OEM diagnostic data.",
        "OS": "Operating system (OS) diagnostic data.",
        "PreOS": "Pre-OS diagnostic data."
    """
    Manager = "Manager"
    PreOS = "PreOS"
    OS = "OS"
    OEM = "OEM"
    Device = "Device"


class RfDiagnosticDataDetailsModel(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/DiagnosticDataDetails
    """
    DiagnosticDataType: Optional[RfLogDiagnosticDataTypes] = Field(default=None)
    EstimatedDuration: Optional[str] = Field(default=None)
    EstimatedSizeBytes: Optional[int] = Field(default=None)
    OEMDiagnosticDataType: Optional[str] = Field(default=None)

class RfLogEntryTypes(str, Enum):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/LogEntryTypes
    """
    Event = "Event"
    SEL = "SEL"
    Multiple = "Multiple"
    OEM = "OEM"
    CXL = "CXL"

class RfLogPurpose(str, Enum):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/LogPurpose
    """
    Diagnostic = "Diagnostic"
    Operations = "Operations"
    Security = "Security"
    Telemetry = "Telemetry"
    ExternalEntity = "ExternalEntity"
    OEM = "OEM"


class RfSyslogFacility(str, Enum):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/SyslogFacility
    """
    Kern = "Kern"
    User = "User"
    Mail = "Mail"
    Daemon = "Daemon"
    Auth = "Auth"
    Syslog = "Syslog"
    LPR = "LPR"
    News = "News"
    UUCP = "UUCP"
    Cron = "Cron"
    Authpriv = "Authpriv"
    FTP = "FTP"
    NTP = "NTP"
    Security = "Security"
    Console = "Console"
    SolarisCron = "SolarisCron"
    Local0 = "Local0"
    Local1 = "Local1"
    Local2 = "Local2"
    Local3 = "Local3"
    Local4 = "Local4"
    Local5 = "Local5"
    Local6 = "Local6"
    Local7 = "Local7"

class RfSyslogSeverity(str, Enum):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/SyslogSeverity
    """
    Emergency = "Emergency"
    Alert = "Alert"
    Critical = "Critical"
    Error = "Error"
    Warning = "Warning"
    Notice = "Notice"
    Informational = "Informational"
    Debug = "Debug"
    All = "All"

class RfSyslogFilterModel(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/SyslogFilter
    """
    LogFacilities: Optional[List[RfSyslogFacility]] = Field(default=None)
    LowestSeverity: Optional[RfSyslogSeverity] = Field(default=None)
    
class RfLogServiceModel(RfResourceBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/LogService
    """
    odata_context: Optional[str] = Field(default=None, alias="@odata.context")
    odata_etag: Optional[str] = Field(default=None, alias="@odata.etag")
    # odata_id: str = Field(..., alias="@odata.id")
    # odata_type: str = Field(..., alias="@odata.type")
    Actions: Optional[RfActions] = Field(default=None)
    AutoClearResolvedEntries: Optional[RfAutoClearResolvedEntries] = Field(default=None)
    AutoDSTEnabled: Optional[bool] = Field(default=None, description="An indication of whether the log service is configured for automatic Daylight Saving Time (DST) adjustment.")
    DateTime: Optional[str] = Field(default=None, description="The current date and time with UTC offset of the log service.")
    DateTimeLocalOffset: Optional[str] = Field(default=None, description="The time offset from UTC that the `DateTime` property is in `+HH:MM` format.")
    Description: Optional[str] = Field(default=None)
    DiagnosticDataDetails: Optional[List[RfDiagnosticDataDetailsModel]] = Field(default=None, description="The detailed information for the data collected with the `CollectDiagnosticData` action.")
    Entries: Optional[RfLogEntryCollectionModel] = Field(default=None)
    # Id: str
    LogEntryType: Optional[RfLogEntryTypes] = Field(default=None)
    LogPurposes: Optional[List[RfLogPurpose]] = Field(default=None)
    MaxNumberOfRecords: Optional[int] = Field(default=None)
    # Name: str
    OEMLogPurpose: Optional[str] = Field(default=None)
    Oem: Optional[Dict[str, Any]] = Field(default=None)
    OverWritePolicy: Optional[RfOverWritePolicy] = Field(default=None)
    Overflow: Optional[bool] = Field(default=None, description="Indicates whether the log service has overflowed.")
    Persistency: Optional[bool] = Field(default=None, description="Indicates whether the log service is persistent across a cold reset.")
    ServiceEnabled: Optional[bool] = Field(default=None)
    Status: Optional[RfStatusModel] = Field(default=None)
    SyslogFilters: Optional[List[RfSyslogFilterModel]] = Field(default=None, description="A list of syslog message filters to be logged locally.")
    pass
