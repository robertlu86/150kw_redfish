import os
from flask import current_app, request, jsonify, make_response, send_file, Response
from flask_restx import Namespace, Resource

root_ns = Namespace('', description='Redfish V1')

root_data={
    "@odata.id": "/redfish/v1/",
    "@odata.type": "#ServiceRoot.v1_17_0.ServiceRoot",
    "Id": "RootService",
    "Name": "Redfish Service",
    "RedfishVersion": "1.14.0",
    "Vendor": "Supermicro",
    "ServiceIdentification": "ServiceRoot",
    "UUID": "00000000-0000-0000-0000-e45f013e98f8",
    "Product": "TBD",
    "ProtocolFeaturesSupported": {
        "FilterQuery": False,
        "SelectQuery": False,
        "ExcerptQuery": False,
        "OnlyMemberQuery": False,
        "ExpandQuery": {
            "Links": False,
            "NoLinks": False,
            "ExpandAll": False,
            "Levels": False,
            "MaxLevels": 3
        }
    },
    # 支援的服務
    "ThermalEquipment": {"@odata.id": "/redfish/v1/ThermalEquipment"},
    "Managers": {"@odata.id": "/redfish/v1/Managers"},
    "Chassis": {"@odata.id": "/redfish/v1/Chassis"},
    "SessionService": {"@odata.id": "/redfish/v1/SessionService"},
    "AccountService": {"@odata.id": "/redfish/v1/AccountService"},
    "TelemetryService": {"@odata.id": "/redfish/v1/TelemetryService"},
    "UpdateService": {"@odata.id": "/redfish/v1/UpdateService"},
    # 要新增
    "EventService": {"@odata.id": "/redfish/v1/EventService"},
    "CertificateService": {"@odata.id": "/redfish/v1/CertificateService"},
    "Systems": {"@odata.id": "/redfish/v1/Systems"},
    "ComponentIntegrity": {"@odata.id": "/redfish/v1/ComponentIntegrity"},
    # "Registry": {"@odata.id": "/redfish/v1/Registry"},
    # "Product": {"@odata.id": "/redfish/v1/Product"},
    "Links": {
        "Sessions": {
            "@odata.id": "/redfish/v1/SessionService/Sessions"
        }
    },
    # 廠商擴充自訂屬性
    "Oem": {}
}

odata_data = {
  "@odata.context": "/redfish/v1/$metadata",
  "value": [
    { "@odata.id": "/redfish/v1/AccountService" },
    { "@odata.id": "/redfish/v1/Chassis" },
    { "@odata.id": "/redfish/v1/Managers" },
    { "@odata.id": "/redfish/v1/SessionService" },
    { "@odata.id": "/redfish/v1/TelemetryService" },
    { "@odata.id": "/redfish/v1/ThermalEquipment" },
    { "@odata.id": "/redfish/v1/UpdateService" },
    # 要新增
    { "@odata.id": "/redfish/v1/CertificateService"},
    {"@odata.id": "/redfish/v1/EventService"},
    {"@odata.id": "/redfish/v1/Systems"},
    {"@odata.id": "/redfish/v1/ComponentIntegrity"},
    # {"@odata.id": "/redfish/v1/Registry"}, # 未新增 metadata
    # {"@odata.id": "/redfish/v1/Product"}, # 未新增 metadata
  ]    
}

@root_ns.route("/")
class Root(Resource):
    # @requires_auth
    def get(self):
        odata_ver = request.headers.get('OData-Version')
        if odata_ver is not None and odata_ver != '4.0':
            return Response(status=412)
        
        resp = make_response(jsonify(root_data), 200)
        resp.headers['Allow'] = 'OPTIONS, GET, HEAD'
        resp.headers['Cache-Control'] = 'no-cache'
        return resp
 
@root_ns.route('/odata')
class odata(Resource):
    def get(self):
        return odata_data
        
@root_ns.route('/$metadata')
class metadata(Resource):
    def get(self):
        xml_path = os.path.join(current_app.root_path, 'metadata.xml')
        if not os.path.exists(xml_path):
            return {"error": "metadata.xml not found"}, 500
        # 用 send_file 直接回 XML
        return send_file(xml_path, mimetype='application/xml; charset=utf-8')