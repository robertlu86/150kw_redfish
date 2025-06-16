import os
from flask import current_app, request, jsonify, make_response, send_file, Response
from flask_restx import Namespace, Resource, fields

from mylib.services.rf_event_service import RfEventService

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
    # "Actions": {
    #     "#EventService.SubmitTestEvent": {
    #     "target": "/redfish/v1/EventService/Actions/EventService.SubmitTestEvent",
    #     "title": "SubmitTestEvent"
    #     }
    # },
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
# =============================================
# patch/post model
# =============================================
# EventService patch設置
EventService_patch = EventService_ns.model('EventServicePatch', {
    'ServiceEnabled': fields.Boolean(
        required=True,
        description='ServiceEnabled',
        default=True,
        example=True
    ),
    "DeliveryRetryAttempts": fields.Integer(
        required=True,
        description='DeliveryRetryAttempts',
        default=True,
        example=3
    ),
    "DeliveryRetryIntervalSeconds": fields.Integer(
        required=True,
        description='DeliveryRetryIntervalSeconds',
        default=True,
        example=60
    )
})

# Event Subscription psot設置
EventSubscription_post = EventService_ns.model('EventSubscriptionPost', {
    # essential
    'Destination': fields.String(
        required=True,
        description='URI',
        default=True,
        example="127.0.0.1"
    ),
    "Protocol": fields.String(
        required=True,
        description='Protocol',
        default=True,
        example="SNMPv2c",
        enum = ["SNMPv2c"]
        # enum=["Redfish", "Kafka", "SNMPv1", "SNMPv2c", "SNMPv3", "SMTP", "SyslogTLS", "SyslogTCP", "SyslogUDP", "SyslogRELP", "OEM"]
    ),
    "Context": fields.String(
        required=True,
        description='Context',
        default=True,
        example="1"
    )
    # optional
    # 未來擴充
})
# Event Subscription Id patch設置
EventSubscriptionId_post = EventService_ns.model('EventSubscriptionIdPost', {
    # essential
    'Destination': fields.String(
        required=True,
        description='URI',
        default=True,
        example="127.0.0.1"
    ),
    'TrapCommunity': fields.String(
        required=True,
        description='TrapCommunity',
        default=True,
        example="public"
    ),
    "Context": fields.String(
        required=True,
        description='Context',
        default=True,
        example="1"
    )
    # optional
    # 未來擴充
})

# =============================================
# route
# =============================================
@EventService_ns.route("/EventService")
class EventService(Resource):
    # menthod get/patch
    def get(self):
        # return EventService_data
        return RfEventService().get_event_service()
    
    @EventService_ns.expect(EventService_patch, validate=True)
    def patch(self):
        body = request.get_json(force=True)
        return RfEventService().patch_event_service(body)


@EventService_ns.route("/EventService/Subscriptions")
class Subscriptions(Resource):
    # get/post
    def get(self):
        # return Subscriptions_data    
        return RfEventService().get_subscriptions()
    
    # @EventService_ns.expect(EventSubscription_post, validate=True)
    # def post(self):
    #     body = request.get_json(force=True)
    #     return RfEventService().post_subscriptions(body)

    
@EventService_ns.route("/EventService/Subscriptions/<string:Subscriptions_id>")
class Subscriptions(Resource):
    # get/delete/patch
    def get(self, Subscriptions_id):
        # return Subscriptions_id_data        
        return RfEventService().get_subscriptions_id(Subscriptions_id)
    
    @EventService_ns.expect(EventSubscriptionId_post, validate=True)
    def patch(self, Subscriptions_id):
        body = request.get_json(force=True)
        return RfEventService().patch_subscriptions_id(Subscriptions_id, body)