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


class RfEventSeverity(str, Enum):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogEntry.v1_18_0.json#/definitions/EventSeverity
    """
    OK = "OK"
    Warning = "Warning"
    Critical = "Critical"

class RfLogEntryType(str, Enum):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogEntry.v1_18_0.json#/definitions/LogEntryType
    """
    Event = "Event" # "A Redfish-defined message."
    SEL = "SEL"     # "A legacy IPMI System Event Log (SEL) entry."
    Oem = "Oem"     # "An entry in an OEM-defined format."
    CXL = "CXL"     # "A CXL log entry."

class RfLogEntryModel(RfResourceBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/LogEntry.v1_18_0.json
    @note properties 48 items
    """
    # "@odata.context": {1 item},
    # "@odata.etag": {1 item},
    # "@odata.id": {1 item},
    # "@odata.type": {1 item},
    # "Actions": {4 items},
    # "AdditionalDataSizeBytes": {6 items},
    # "AdditionalDataURI": {6 items},
    # "CPER": {4 items},
    # "CXLEntryType": {5 items},
    Created: Optional[str] = Field(default=None)
    # "Description": {2 items},
    # "DiagnosticData": {5 items},
    # "DiagnosticDataType": {5 items},
    # "EntryCode": {4 items},
    # "EntryType": {4 items},
    # "EventGroupId": {5 items},
    # "EventId": {5 items},
    # "EventTimestamp": {6 items},
    EventType: RfLogEntryType = Field(default=None)
    # "FirstOverflowTimestamp": {6 items},
    # "GeneratorId": {6 items},
    # "Id": {2 items},
    # "LastOverflowTimestamp": {6 items},
    # "Links": {3 items},
    Message: str = Field(default=None)
    # "MessageArgs": {5 items},
    MessageId: str = Field(default=None, description="The `MessageId`, event data, or OEM-specific information. This property decodes from the entry type. If the entry type is `Event`, this property contains a Redfish Specification-defined `MessageId`. If the entry type is `SEL`, this property contains the Event Data. Otherwise, this property contains OEM-specific information.")
    # "Modified": {6 items},
    # "Name": {2 items},
    # "OEMDiagnosticDataType": {5 items},
    # "Oem": {3 items},
    # "OemLogEntryCode": {5 items},
    # "OemRecordFormat": {4 items},
    # "OemSensorType": {5 items},
    # "Originator": {5 items},
    # "OriginatorType": {5 items},
    # "OverflowErrorCount": {5 items},
    # "Persistency": {5 items},
    # "Resolution": {5 items},
    # "ResolutionSteps": {5 items},
    # "Resolved": {5 items},
    # "SensorNumber": {4 items},
    # "SensorType": {4 items},
    # "ServiceProviderNotified": {5 items},
    Severity: RfEventSeverity = Field(default=None)
    # "SpecificEventExistsInGroup": {5 items},
    # "UserAuthenticationSource": {5 items},
    # "Username": {5 items}
