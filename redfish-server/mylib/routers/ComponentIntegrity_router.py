import os
from flask import current_app, request, jsonify, make_response, send_file, Response
from flask_restx import Namespace, Resource

ComponentIntegrity_ns = Namespace('', description='ComponentIntegrity Collection')

ComponentIntegrity_data = {
    "@odata.id": "/redfish/v1/ComponentIntegrity",
    "@odata.type": "#ComponentIntegrityCollection.ComponentIntegrityCollection",
    "@odata.context": "/redfish/v1/$metadata#ComponentIntegrityCollection.ComponentIntegrityCollection",
    
    "Name": "Component Integrity",
    
    "Members@odata.count": 1,
    "Members": [
        {"@odata.id": "/redfish/v1/ComponentIntegrity/1"}
    ],
            
    "Oem": {}
}


@ComponentIntegrity_ns.route('/ComponentIntegrity')
class ComponentIntegrity(Resource):
    def get(self):
        return ComponentIntegrity_data
    
@ComponentIntegrity_ns.route('/ComponentIntegrity/<int:id>')
class ComponentIntegrityId(Resource):
    def get(self, id):
        ComponentIntegrity_id_data = {
            "@odata.id": f"/redfish/v1/ComponentIntegrity/{id}",
            "@odata.type": "#ComponentIntegrity.v1_3_1.ComponentIntegrity",
            "@odata.context": "/redfish/v1/$metadata#ComponentIntegrity.v1_3_1.ComponentIntegrity",
            
            "Id": "1",
            "Name": "Component Integrity",
            "Description": "Component Integrity",
            
            "ComponentIntegrityType": "TPM",
            "ComponentIntegrityTypeVersion": "TBD",
            "TargetComponentURI": "TBD",

        }
        return ComponentIntegrity_id_data    