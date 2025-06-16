'''
這是Redfish的event service
'''
import subprocess, json
import requests
from flask import jsonify
from mylib.services.base_service import BaseService
from mylib.models.rf_networkprotocol_model import RfNetworkProtocolModel
from mylib.models.rf_snmp_model import RfSnmpModel
from mylib.adapters.webapp_api_adapter import WebAppAPIAdapter
from mylib.models.rf_resource_model import RfResetType
from mylib.common.proj_response_message import ProjResponseMessage
from mylib.utils.load_api import load_raw_from_api, CDU_BASE
from mylib.models.rf_event_service_model import RfEventServiceModel, RfEventSubscriptionsModel, RfEventSubscriptionIdModel
from mylib.models.rf_status_model import RfStatusModel
from mylib.services.rf_managers_service import RfManagersService

event_setting = {
    "ServiceEnabled": True,
    "DeliveryRetryAttempts": 3,
    "DeliveryRetryIntervalSeconds": 60
}

event_subscriptions = [
    {"@odata.id": "/redfish/v1/EventService/Subscriptions/1"}
]

event_subscriptions_Id = [
   {
    "Context": "1",
    "Destination":"127.0.0.1",
    "TrapCommunity": "public",
   }
]
class RfEventService(BaseService):
    #==========================================
    # EventService
    #==========================================
    def get_event_service(self):
        m = RfEventServiceModel()
        m.ExcludeMessageId = False
        m.ExcludeRegistryPrefix = False
        m.IncludeOriginOfConditionSupported = False
        m.SubordinateResourcesSupported = False
        m.ServiceEnabled = event_setting["ServiceEnabled"]
        m.DeliveryRetryAttempts = event_setting["DeliveryRetryAttempts"] 
        m.DeliveryRetryIntervalSeconds = event_setting["DeliveryRetryIntervalSeconds"]
        m.EventTypesForSubscription = ["Alert"]
        m.ServerSentEventUri = "None"
        SSEFilterPropertiesSupported = {
            "RegistryPrefix": True,
            "ResourceType": True
        }
        m.SSEFilterPropertiesSupported = RfEventServiceModel._SSEFilterPropertiesSupported(**SSEFilterPropertiesSupported)
        m.ResourceTypes = []
        m.RegistryPrefixes=[]
        m.Subscriptions = {
            "@odata.id": "/redfish/v1/EventService/Subscriptions"
        }
        status = {
            "State": "Enabled",
            "Health": "OK"
        }
        m.Status = RfStatusModel(**status)
        
        return m.to_dict(), 200
    
    def patch_event_service(self, body):
        '''
        ServiceEnabled: 是否啟用服務
        DeliveryRetryAttempts: 重試次數
        DeliveryRetryIntervalSeconds: 重試間隔
        '''
        ServiceEnabled = body.get("ServiceEnabled")
        DeliveryRetryAttempts = body.get("DeliveryRetryAttempts")
        DeliveryRetryIntervalSeconds = body.get("DeliveryRetryIntervalSeconds")
        if ServiceEnabled is not None:
            event_setting["ServiceEnabled"] = ServiceEnabled
        if DeliveryRetryAttempts is not None:
            event_setting["DeliveryRetryAttempts"] = DeliveryRetryAttempts
        if DeliveryRetryIntervalSeconds is not None:
            event_setting["DeliveryRetryIntervalSeconds"] = DeliveryRetryIntervalSeconds
            
        return self.get_event_service()
    #==========================================
    # EventSubscriptions
    #==========================================
    def get_subscriptions(self):
        m = RfEventSubscriptionsModel()
        m.Members_odata_count = len(event_subscriptions)
        m.Members = event_subscriptions
        
        return m.to_dict(), 200
    
    # def post_subscriptions(self, body):
    #     return self.get_subscriptions()
    
    #==========================================
    # EventSubscriptionId
    #==========================================
    def get_subscriptions_id(self, subscription_id: str):
        m = RfEventSubscriptionIdModel(Subscriptions_id=subscription_id)
        
        m.SubscriptionType = "SNMPTrap"
        m.Context = event_subscriptions_Id[0]["Context"]
        m.DeliveryRetryPolicy = "RetryForever"
        m.Destination = event_subscriptions_Id[0]["Destination"]
        m.Protocol = "SNMPv2c"
        m.EventFormatType = "Event"
        m.RegistryPrefixes = []
        m.ResourceTypes = []
        status = {
            "State": "Enabled",
            "Health": "OK"
        }
        m.Status = RfStatusModel(**status)
        
        return m.to_dict(), 200
    
    def patch_subscriptions_id(self, subscription_id: str, body):
        
        event_subscriptions_Id[0]["Destination"] = body.get("Destination")
        event_subscriptions_Id[0]["TrapCommunity"] = body.get("TrapCommunity")
        event_subscriptions_Id[0]["Context"] = body.get("Context")
        
        snmp_post = {
            "TrapIP": event_subscriptions_Id[0]["Destination"],
            "Community": event_subscriptions_Id[0]["TrapCommunity"],
        }
        RfManagersService().NetworkProtocol_Snmp_Post(snmp_post)
        
        return self.get_subscriptions_id(subscription_id)