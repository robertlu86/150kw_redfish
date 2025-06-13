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
from mylib.models.rf_base_model import RfResourceBaseModel, RfResourceCollectionBaseModel
from mylib.models.rf_status_model import RfStatusModel, RfStatusHealth, RfStatusState


# Service
class RfEventServiceModel(RfResourceBaseModel):
    #  _SSEFilterPropertiesSupported model
    class _SSEFilterPropertiesSupported(BaseModel):
        RegistryPrefix: Optional[bool] = Field(default=None)
        ResourceType: Optional[bool] = Field(default=None) 
    # main model
    Odata_context: Optional[str] = Field(default=None, alias="@odata.context")
    Discription: Optional[str] = Field(default=None)

    # only read
    ExcludeMessageId: Optional[bool] = Field(default=None)
    ExcludeRegistryPrefix: Optional[bool] = Field(default=None)
    IncludeOriginOfConditionSupported: Optional[bool] = Field(default=None)
    SubordinateResourcesSupported: Optional[bool] = Field(default=None)
    EventTypesForSubscription: Optional[List[str]] = Field(default=None)
    ServerSentEventUri: Optional[str] = Field(default=None)
    SSEFilterPropertiesSupported: Optional[_SSEFilterPropertiesSupported] = Field(default=None)
    ResourceTypes: Optional[List[str]] = Field(default=None)
    RegistryPrefixes: Optional[List[str]] = Field(default=None)
    
    # read/write
    ServiceEnabled: Optional[bool] = Field(default=None)
    DeliveryRetryAttempts: Optional[int] = Field(default=None)
    DeliveryRetryIntervalSeconds: Optional[int] = Field(default=None)
    Subscriptions: Optional[Dict[str, Any]] = Field(default=None)

    Status: Optional[RfStatusModel] = Field(default=None)
    # Actions: Optional[Dict[str, Any]] = Field(default=None)
    Oem: Optional[Dict[str, Any]] = Field(default=None)





    model_config = ConfigDict(
        extra='allow',
        # arbitrary_types_allowed=True
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.odata_id = "/redfish/v1/EventService"
        self.odata_type = "#EventService.v1_11_0.EventService"
        self.Odata_context = "/redfish/v1/$metadata#EventService.EventService"

        self.Id = "EventService"
        self.Name = "Event Service"
        self.Description = "This resource represents an event service for a Redfish implementation."
        
        
# Subscriptions
class RfEventSubscriptionsModel(RfResourceCollectionBaseModel):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.odata_id = "/redfish/v1/EventService/Subscriptions"
        self.odata_type = "#EventDestinationCollection.EventDestinationCollection"
        self.odata_context = "/redfish/v1/$metadata#EventDestinationCollection.EventDestinationCollection"
        self.Name = "EventSubscriptions"
        self.Description = "Event Subscriptions Collection"   
        
class RfEventSubscriptionIdModel(RfResourceBaseModel):       
    class _SNMP(BaseModel):
        TrapCommunity: Optional[str] = Field(default=None) 
        AuthenticationProtocol: Optional[str] = Field(default=None)
        AuthenticationKey: Optional[str] = Field(default=None)
        EncryptionKey: Optional[str] = Field(default=None)
        EncryptionProtocol: Optional[str] = Field(default=None)
        
    # only read
    SubscriptionType: Optional[str] = Field(default=None) # "RedfishEvent","SSE","SNMPTrap","SNMPInform","Syslog","OEM"
    DeliveryRetryPolicy: Optional[str] = Field(default=None) 
    Destination: Optional[str] = Field(default=None)
    Protocol: Optional[str] = Field(default=None)
    EventFormatType: Optional[str] = Field(default=None)
    RegistryPrefixes: Optional[List[str]] = Field(default=None)
    ResourceTypes: Optional[List[str]] = Field(default=None)
    
    # read write
    Context: Optional[str] = Field(default=None)
    SNMP: Optional[_SNMP] = Field(default=None)
    
    Status: Optional[RfStatusModel] = Field(default=None)
    Oem: Optional[Dict[str, Any]] = Field(default=None)
    
    model_config = ConfigDict(
        extra='allow',
        # arbitrary_types_allowed=True
    )
    def __init__(self, Subscriptions_id: str, **kwargs):
        super().__init__(**kwargs)
        self.odata_id = f"/redfish/v1/EventService/Subscriptions/{Subscriptions_id}"
        self.odata_type = "#EventDestination.v1_15_1.EventDestination"
        self.odata_context = "/redfish/v1/$metadata#EventDestination.EventDestination"
        
        self.Id = str(Subscriptions_id)
        self.Name = f"Event Subscription {Subscriptions_id}"
        self.Description = "Webhook for critical alerts"   
        
        
        
        
    