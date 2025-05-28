import os
from flask import current_app, request, jsonify, make_response, send_file, Response
from flask_restx import Namespace, Resource

EventService_ns = Namespace('', description='EventService Collection')

EventService_data = {
    "@odata.context": "/redfish/v1/$metadata#EventService.EventService",
    "@odata.id": "/redfish/v1/EventService",
    "@odata.type": "#EventService.v1_11_0.EventService",
    "Id": "EventService",
    "Name": "Event Service",
    "Description": "This resource represents an event service for a Redfish implementation.",
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "ExcludeMessageId": False,
    "ExcludeRegistryPrefix": False,
    "IncludeOriginOfConditionSupported": False,
    "SubordinateResourcesSupported": False,
    "ServiceEnabled": True,
    "DeliveryRetryAttempts": 3,
    "DeliveryRetryIntervalSeconds": 60,
    "EventTypesForSubscription": ["StatusChange"],
    "ServerSentEventUri": "TBD",
    "SSEFilterPropertiesSupported": {
        "RegistryPrefix": True,
        "ResourceType": True
    },
    "ResourceTypes": ["Certificate"],
    "RegistryPrefixes":[
        "Base",
        "EventRegistry"
    ],

    "Subscriptions": {
        "@odata.id": "/redfish/v1/EventService/Subscriptions"
    },
    "Actions": {
        "#EventService.SubmitTestEvent": {
        "target": "/redfish/v1/EventService/Actions/EventService.SubmitTestEvent",
        "title": "SubmitTestEvent"
        }
    },
    "Oem": {}
}

Subscriptions_data = {
    "@odata.context": "/redfish/v1/$metadata#EventDestinationCollection.EventDestinationCollection",
    "@odata.id": "/redfish/v1/EventService/Subscriptions",
    "@odata.type": "#EventDestinationCollection.EventDestinationCollection",
    "Description": "iLO User Event Subscriptions",
    "Name": "EventSubscriptions",
    "Members": [
        {
        "@odata.id": "/redfish/v1/EventService/Subscriptions/1"
        }
    ],
    "Members@odata.count": 1
}



@EventService_ns.route("/EventService")
class EventService(Resource):
    def get(self):
        return EventService_data

@EventService_ns.route("/EventService/Subscriptions")
class Subscriptions(Resource):
    def get(self):
        return Subscriptions_data    
    
@EventService_ns.route("/EventService/Subscriptions/<string:Subscriptions_id>")
class Subscriptions(Resource):
    def get(self, Subscriptions_id):
        Subscriptions_id_data = {
            "@odata.id": f"/redfish/v1/EventService/Subscriptions/{Subscriptions_id}",
            "@odata.type": "#EventDestination.v1_15_1.EventDestination",
            "@odata.context": "/redfish/v1/$metadata#EventDestination.EventDestination",
            
            "Id": str(Subscriptions_id),
            "Name": f"Event Subscription {Subscriptions_id}",
            "Description": "Webhook for critical alerts",

            "SubscriptionType": "RedfishEvent",
            # "EventTypes": ["StatusChange", "ResourceUpdated", "ResourceAdded", "ResourceRemoved", "StatusChange", "ResourceUpdated", "ResourceAdded", "ResourceRemoved"],
            "Context": "TBD",
            "DeliveryRetryPolicy": "RetryForever",
            "Destination": "TBD", 
            "Protocol": "Redfish",
            "EventFormatType": "Event",
            "RegistryPrefixes": [
                "Base",
                "EventRegistry"
            ],
            "ResourceTypes": [
                "Certificate"
            ],
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            },
            
            "Oem": {}
        }
        return Subscriptions_id_data        
