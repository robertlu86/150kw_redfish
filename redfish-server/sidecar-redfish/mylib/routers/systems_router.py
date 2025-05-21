import os
from flask import current_app, request, jsonify, make_response, send_file, Response
from flask_restx import Namespace, Resource

system_ns = Namespace('', description='Systems Collection')

ststem_data = {
    "@odata.context": "/redfish/v1/$metadata#ComputerSystemCollection.ComputerSystemCollection",
    "@odata.id": "/redfish/v1/Systems",
    "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
    "Name": "Computer System Collection",
    "Members@odata.count": 1,
    "Members": [
        {"@odata.id": "/redfish/v1/Systems/1"}
    ],
    "Oem": {}
}

@system_ns.route("/Systems")
class Systems(Resource):
    def get(self):
        return ststem_data
    
@system_ns.route("/Systems/<string:system_id>")    
class System(Resource):
    def get(self, system_id):
        ststem_id_data = {
            "@odata.context": "/redfish/v1/$metadata#ComputerSystem.ComputerSystem",
            "@odata.id": f"/redfish/v1/Systems/{system_id}",
            "@odata.type": "#ComputerSystem.v1_24_0.ComputerSystem",
            
            "Id": str(system_id),
            "Name": "Catfish System",
            "Description": "Catfish System",   
            
            # 服務
            "Bios": {"@odata.id": f"/redfish/v1/Systems/{system_id}/Bios"},
            "Memory": {"@odata.id": f"/redfish/v1/Systems/{system_id}/Memory"},
            "Processors": {"@odata.id": f"/redfish/v1/Systems/{system_id}/Processors"},
            "SecureBoot": {"@odata.id": f"/redfish/v1/Systems/{system_id}/SecureBoot"},
            "Storage": {"@odata.id": f"/redfish/v1/Systems/{system_id}/Storage"},

            "Oem": {}
        }
        return ststem_id_data


# =================================================
# Bios
# =================================================
@system_ns.route(f"/Systems/<string:system_id>/Bios")    
class Bios(Resource):
    def get(self, system_id):
        ststem_id_bios_data = {
            "@odata.context": "/redfish/v1/$metadata#Bios.Bios",
            "@odata.id": f"/redfish/v1/Systems/{system_id}/Bios",
            "@odata.type": "#Bios.v1_2_3.Bios",
                
            "Id": str(system_id),
            "Name": "Catfish System",
            "Description": "Catfish System",   
                
            "Oem": {}
        }
        return ststem_id_bios_data
# =================================================
# SecureBoot
# =================================================
@system_ns.route(f"/Systems/<string:system_id>/SecureBoot")    
class SecureBoot(Resource):
    def get(self, system_id):
        ststem_id_SecureBoot_data = {
            "@odata.context": "/redfish/v1/$metadata#SecureBoot.SecureBoot",
            "@odata.id": f"/redfish/v1/Systems/{system_id}/SecureBoot",
            "@odata.type": "#SecureBoot.v1_1_2.SecureBoot",
                
            "Id": str(system_id),
            "Name": "Catfish System",
            "Description": "Catfish System",   
            
            "SecureBootDatabases": {"@odata.id": f"/redfish/v1/Systems/{system_id}/SecureBoot/SecureBootDatabases"},
                
            "Oem": {}
        }
        return ststem_id_SecureBoot_data

@system_ns.route(f"/Systems/<string:system_id>/SecureBoot/SecureBootDatabases")    
class SecureBootDatabases(Resource):
    def get(self, system_id):
        ststem_id_SecureBootDatabases_data = {
            "@odata.context": "/redfish/v1/$metadata#SecureBootDatabaseCollection.SecureBootDatabaseCollection",
            "@odata.id": f"/redfish/v1/Systems/{system_id}/SecureBoot/SecureBootDatabases",
            "@odata.type": "#SecureBootDatabaseCollection.SecureBootDatabaseCollection",
            "Name": "Secure Boot Database Collection",
            "Members@odata.count": 4,
            "Members": [
                { "@odata.id": f"/redfish/v1/Systems/{system_id}/SecureBoot/SecureBootDatabases/1" },
                { "@odata.id": f"/redfish/v1/Systems/{system_id}/SecureBoot/SecureBootDatabases/2" },
                { "@odata.id": f"/redfish/v1/Systems/{system_id}/SecureBoot/SecureBootDatabases/3" },
                { "@odata.id": f"/redfish/v1/Systems/{system_id}/SecureBoot/SecureBootDatabases/4" }
            ]
        }    
        return ststem_id_SecureBootDatabases_data
    
@system_ns.route(f"/Systems/<string:system_id>/SecureBoot/SecureBootDatabases/<string:database_id>")
class SecureBootDatabase(Resource):
    def get(self, system_id, database_id):
        ststem_id_SecureBootDatabase_data = {
            "@odata.context": "/redfish/v1/$metadata#SecureBootDatabase.SecureBootDatabase",
            "@odata.id": f"/redfish/v1/Systems/{system_id}/SecureBoot/SecureBootDatabases/{database_id}",
            "@odata.type": "#SecureBootDatabase.v1_0_3.SecureBootDatabase",
            
            "Id": str(database_id),
            "DatabaseId": str(database_id),
            "Name": "Catfish System",
            "Description": "Catfish System",   
                
            "Oem": {}
        }
        return ststem_id_SecureBootDatabase_data
    
# =================================================
# Memory
# =================================================    
@system_ns.route(f"/Systems/<string:system_id>/Memory")    
class Memory(Resource):
    def get(self, system_id):
        ststem_id_Memory_data = {
            "@odata.context": "/redfish/v1/$metadata#MemoryCollection.MemoryCollection",
            "@odata.id": f"/redfish/v1/Systems/{system_id}/Memory",
            "@odata.type": "#MemoryCollection.MemoryCollection",
                
            "Name": "Catfish System",
            "Description": "Catfish System",   
                
            "Members@odata.count": 1,
            "Members": [
                {"@odata.id": f"/redfish/v1/Systems/{system_id}/Memory/1"}
            ],
                
            "Oem": {}
        }
        return ststem_id_Memory_data    
    
@system_ns.route(f"/Systems/<string:system_id>/Memory/<string:memory_id>")    
class memory_id(Resource):  
    def get(self, system_id, memory_id):
        ststem_id_memory_id_data = {
            "@odata.context": "/redfish/v1/$metadata#Memory.Memory",
            "@odata.id": f"/redfish/v1/Systems/{system_id}/Memory/{memory_id}",
            "@odata.type": "#Memory.v1_20_0.Memory",
                
            "Id": str(memory_id),
            "Name": "Catfish System",
            "Description": "Catfish System",   
                
            "Oem": {}
        }
        return ststem_id_memory_id_data
    
# =================================================
# Processors
# =================================================
@system_ns.route(f"/Systems/<string:system_id>/Processors")    
class Processors(Resource):
    def get(self, system_id):
        ststem_id_Processors_data = {
            "@odata.context": "/redfish/v1/$metadata#ProcessorCollection.ProcessorCollection",
            "@odata.id": f"/redfish/v1/Systems/{system_id}/Processors",
            "@odata.type": "#ProcessorCollection.ProcessorCollection",
                
            "Name": "Catfish System",
            "Description": "Catfish System",   
                
            "Members@odata.count": 1,
            "Members": [
                {"@odata.id": f"/redfish/v1/Systems/{system_id}/Processors/1"}
            ],
                
            "Oem": {}
        }
        return ststem_id_Processors_data   

@system_ns.route(f"/Systems/<string:system_id>/Processors/<string:processor_id>")    
class processor_id(Resource):
    def get(self, system_id, processor_id):
        ststem_id_processor_id_data = {
            "@odata.context": "/redfish/v1/$metadata#Processor.Processor",
            "@odata.id": f"/redfish/v1/Systems/{system_id}/Processors/{processor_id}",
            "@odata.type": "#Processor.v1_20_1.Processor",
                
            "Id": str(processor_id),
            "Name": "Catfish System",
            "Description": "Catfish System",   
                
            "Oem": {}
        }
        return ststem_id_processor_id_data
# =================================================
# Storage
# =================================================
@system_ns.route(f"/Systems/<string:system_id>/Storage")    
class Storage(Resource):
    def get(self, system_id):
        ststem_id_Storage_data = {
            "@odata.context": "/redfish/v1/$metadata#StorageCollection.StorageCollection",
            "@odata.id": f"/redfish/v1/Systems/{system_id}/Storage",
            "@odata.type": "#StorageCollection.StorageCollection",
                
            "Name": "Catfish System",
            "Description": "Catfish System",   
                
            "Members@odata.count": 1,
            "Members": [
                {"@odata.id": f"/redfish/v1/Systems/{system_id}/Storage/1"}
            ],
                
            "Oem": {}
        }
        return ststem_id_Storage_data
    
@system_ns.route(f"/Systems/<string:system_id>/Storage/<string:storage_id>")    
class storage_id(Resource):
    def get(self, system_id, storage_id):
        ststem_id_storage_id_data = {
            "@odata.context": "/redfish/v1/$metadata#Storage.Storage",
            "@odata.id": f"/redfish/v1/Systems/{system_id}/Storage/{storage_id}",
            "@odata.type": "#Storage.v1_18_0.Storage",
                
            "Id": str(storage_id),
            "Name": "Catfish System",
            "Description": "Catfish System",   
                
            "Oem": {}
        }
        return ststem_id_storage_id_data

# =================================================
# Port
# =================================================   
# @system_ns.route(f"/Systems/<string:system_id>/Port")    
# class Port(Resource):
#     def get(self, system_id):
#         ststem_id_Ports_data = {
#             "@odata.context": "/redfish/v1/$metadata#PortCollection.PortCollection",
#             "@odata.id": f"/redfish/v1/Systems/{system_id}/Port",
#             "@odata.type": "#PortCollection.PortCollection",
                
#             "Name": "Catfish System",
#             "Description": "Catfish System",   
                
                
#             "Oem": {}
#         }
#         return ststem_id_Ports_data
    