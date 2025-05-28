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
            "@Redfish.ActionInfo": "/redfish/v1/CertificateService/GenerateCSRActionInfo",
            "title": "Generate CSR"
        },
        "#CertificateService.ReplaceCertificate": {
            "target": "/redfish/v1/CertificateService/Actions/CertificateService.ReplaceCertificate",
            "title": "Replace an existing certificate"
        },
    },   
    
    "Oem": {}
}

CertificateLocations_data = {
    "@odata.context": "/redfish/v1/$metadata#CertificateLocations.CertificateLocations",
    "@odata.id":      "/redfish/v1/CertificateService/CertificateLocations",
    "@odata.type":    "#CertificateLocations.v1_0_4.CertificateLocations",
    
    "Id": "CertificateLocations",
    "Name": "Certificate Location Collection",
    "Links": {
        "Certificates": [
            # { "@odata.id": "/redfish/v1/CertificateService/Certificates/1" },
        ]
    },
    "Members@odata.count": 0,
    "Oem": {}
}

GenerateCSRActionInfo_data = {
    "@odata.id": "/redfish/v1/CertificateService/GenerateCSRActionInfo",
    "@odata.type": "#ActionInfo.v1_4_2.ActionInfo",
    
    "Id": "GenerateCSRActionInfo",
    "Name": "GenerateCSR Action Info",
    "Description": "Defines the parameters required for generating a CSR.",
    
    "Parameters": [
        {
            "Name": "CertificateCollection",
            "Required": True,
            "DataType": "String",
            "AllowableValues": [
                "/redfish/v1/CertificateService/Certificates"
            ]
        },
        {
            "Name": "CommonName",
            "Required": True,
            "DataType": "String"
        },
    ]
}

@CertificateService_ns.route("/CertificateService")
class CertificateService(Resource):
    # # @requires_auth
    @CertificateService_ns.doc("CertificateService")
    def get(self):
        
        return CertificateService_data

@CertificateService_ns.route("/CertificateService/CertificateLocations")
class CertificateLocations(Resource):
    # # @requires_auth
    @CertificateService_ns.doc("CertificateLocations")
    def get(self):
        
        return CertificateLocations_data

@CertificateService_ns.route("/CertificateService/GenerateCSRActionInfo")
class GenerateCSRActionInfo(Resource):
    # # @requires_auth
    @CertificateService_ns.doc("GenerateCSRActionInfo")
    def get(self):
        
        return GenerateCSRActionInfo_data
    

