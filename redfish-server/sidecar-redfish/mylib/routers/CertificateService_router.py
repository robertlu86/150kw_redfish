from flask import request
from flask_restx import Namespace, Resource

CertificateService_ns = Namespace('', description='CertificateService Collection')

CertificateService_data = {
    "@odata.id":      "/redfish/v1/CertificateService",
    "@odata.type":    "#CertificateService.v1_0_6.CertificateService",
    "@odata.context": "/redfish/v1/$metadata#CertificateService.CertificateService",
    
    "Id":          "CertificateService",
    "Name":        "Certificate Service",
    "Description": "Service for managing certificates",
    

    "CertificateLocations": {
        "@odata.id": "/redfish/v1/CertificateService/CertificateLocations"
    },
    
    "Actions": {
        "#CertificateService.GenerateCSR": {
            "target": "/redfish/v1/CertificateService/Actions/CertificateService.GenerateCSR",
            "title": "Generate CSR"
        },
        "#CertificateService.ReplaceCertificate": {
            "target": "/redfish/v1/CertificateService/Actions/CertificateService.ReplaceCertificate",
            "title": "Replace an existing certificate"
        }
    },   
    
    "Oem": {
        "Certificates": {
            "@odata.id": "/redfish/v1/CertificateService/Certificates"
        },
    }
}

Certificates_data = {
    "@odata.id": "/redfish/v1/CertificateService/Certificates",
    "@odata.type": "#CertificateCollection.CertificateCollection",
    "@odata.context": "/redfish/v1/$metadata#CertificateCollection.CertificateCollection",
    
    "Name": "Certificate Collection",
    "Members@odata.count": 1,
    "Members": [
        { "@odata.id": "/redfish/v1/CertificateService/Certificates/1" }
    ],
    "@Redfish.SupportedCertificates": ["PEM"]
}


CertificateLocations_data = {
    "@odata.context": "/redfish/v1/$metadata#CertificateLocations.CertificateLocations",
    "@odata.id":      "/redfish/v1/CertificateService/CertificateLocations",
    "@odata.type":    "#CertificateLocations.v1_0_4.CertificateLocations",
    
    "Id": "CertificateLocations",
    "Name": "Certificate Location Collection",
    "Links": {},
    "Members@odata.count": 0,
    "Oem": {}
}


Certificate_data1 = {
    "@odata.id": "/redfish/v1/CertificateService/Certificates/<id>",
    "@odata.type": "#Certificate.v1_9_0.Certificate",
    "@odata.context": "/redfish/v1/$metadata#Certificate.Certificate",
    
    "Id": "<id>",
    "Name": "Default Certificate",
    
    "ValidNotBefore": "2025-01-01T00:00:00Z",
    "ValidNotAfter":  "2035-01-01T00:00:00Z",
    "KeyUsage": [
        "KeyEncipherment",
        "ServerAuthentication"
    ],
    "Oem": {}
}

@CertificateService_ns.route("/CertificateService")
class CertificateService(Resource):
    # # @requires_auth
    @CertificateService_ns.doc("CertificateService")
    def get(self):
        
        return CertificateService_data

@CertificateService_ns.route("/CertificateService/Certificates")
class Certificates(Resource):
    # # @requires_auth
    @CertificateService_ns.doc("Certificates")
    def get(self):
        
        return Certificates_data
    
    
@CertificateService_ns.route("/CertificateService/CertificateLocations")
class CertificateLocations(Resource):
    # # @requires_auth
    @CertificateService_ns.doc("CertificateLocations")
    def get(self):
        
        return CertificateLocations_data
    
@CertificateService_ns.route("/CertificateService/Certificates/<int:id>")
class Certificate(Resource):
    # # @requires_auth
    @CertificateService_ns.doc("Certificate")
    def get(self, id):
        Certificate_data1["@odata.id"] = f"/redfish/v1/CertificateService/Certificates/{id}",
        Certificate_data1["Id"] = str(id)
        
        return Certificate_data1
