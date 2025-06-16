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


class RfLogEntryType(str, Enum):
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
    
class RfLogServiceCollectionModel(RfResourceCollectionBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogServiceCollection.json
    """
    # 所有欄位都同 RfResourceCollectionBaseModel 
    pass

class RfLogServiceModel(RfResourceBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogService.v1_8_0.json#/definitions/LogService
    """
    # "@odata.context": {1 item},
    # "@odata.etag": {1 item},
    # "@odata.id": {1 item},
    # "@odata.type": {1 item},
    # "Actions": {3 items},
    # "AutoClearResolvedEntries": {5 items},
    # "AutoDSTEnabled": {5 items},
    # "DateTime": {5 items},
    # "DateTimeLocalOffset": {5 items},
    # "Description": {2 items},
    # "DiagnosticDataDetails": {5 items},
    # "Entries": {4 items},
    # "Id": {2 items},
    # "LogEntryType": {5 items},
    # "LogPurposes": {6 items},
    # "MaxNumberOfRecords": {5 items},
    # "Name": {2 items},
    # "OEMLogPurpose": {5 items},
    # "Oem": {3 items},
    # "OverWritePolicy": {4 items},
    # "Overflow": {5 items},
    # "Persistency": {5 items},
    # "ServiceEnabled": {4 items},
    # "Status": {3 items},
    # "SyslogFilters": {5 items}
    pass
