from flask_restx import Namespace, Resource
from flask import request
import requests
from mylib.utils.load_api import load_raw_from_api 
from mylib.utils.load_api import CDU_BASE

update_ns = Namespace('', description='update service')

UpdateService_data = {
    "@odata.id": "/redfish/v1/UpdateService",
    "@odata.type": "#UpdateService.v1_14_0.UpdateService",
    
    "Id": "UpdateService",
    "Name": "Update cdu",
    
    "ServiceEnabled": True,
    "FirmwareInventory": {
        "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory"
    },
    "Actions": {
        "#UpdateService.SimpleUpdate": {
            "target": "/redfish/v1/UpdateService/Actions/UpdateCdu.SimpleUpdate",
            "@Redfish.ActionInfo": "/redfish/v1/UpdateService/SimpleUpdateActionInfo"
        }
    },
}

FirmwareInventory_data = {
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory",
    "@odata.type": "#SoftwareInventoryCollection.SoftwareInventoryCollection",
    "Name": "Firmware Inventory",

    "Members@odata.count": 2, # 未串
    "Members": [{
        "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/WebInterface",
        # "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PLC",
        # "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PC"
    }],
}

WebInterface_data = {
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/WebInterface" ,
    "@odata.type": "#SoftwareInventory.v1_3_0.SoftwareInventory",
    "Id": "WebInterface",
    "Name": "Web Interface firmware",
    "Manufacturer": "supermicro",
    # 更新日
    "ReleaseDate": "2025-02-21T06:02:08Z", # 未串
    # 是否可更新
    "Updateable": True,    
    "Version": "1502",
    "SoftwareId": "WEB-INTERFACE",
    "Oem": {
        "supermicro": {
            "@odata.type": "#SMC.WebInterface.v1_0_0.WebInterface",
            "Redfish": "1.0.0",
        }
    }
}


# FirmwareInventoryPC_data = {
#     "@odata.type": "#PC.v0100.PC",
#     "Id": "PC",
#     "Name": "PC version",
#     "Version": "0100",
#     "SoftwareId": "PC-Version",
#     "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PC"     
# }

# FirmwareInventoryPLC_data = {
#     "@odata.type": "#PLC.PLC",
#     "Id": "PLC",
#     "Name": "PLC version",
#     "Version": "0107",
#     "SoftwareId": "PLC-Version",
#     "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PLC"     
# }

@update_ns.route("/UpdateService")
class UpdateService(Resource):
    def get(self):

        return UpdateService_data  

@update_ns.route("/UpdateService/FirmwareInventory")
class FirmwareInventory(Resource):
    def get(self):

        return FirmwareInventory_data  

@update_ns.route("/UpdateService/FirmwareInventory/WebInterface")
class FirmwareInventoryWebInterface(Resource):
    def get(self):
        WebInterface_data["Version"] = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/display/version")["fw_info"]["WebUI"]
        WebInterface_data["Oem"]["supermicro"]["Redfish"] = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/display/version")["fw_info"]["Redfish"]
        return WebInterface_data  

from werkzeug.datastructures import FileStorage
upload_parser = update_ns.parser()
upload_parser.add_argument(
    'File',
    location='files',
    type=FileStorage,
    required=True,
    help='Firmware zip file'
)

# 要確認
@update_ns.route("/UpdateService/SimpleUpdateActionInfo")
class SimpleUpdateActionInfo(Resource):
    def get(self):
        return {
          "@odata.context": "/redfish/v1/$metadata#ActionInfo.ActionInfo",
          "@odata.id": "/redfish/v1/UpdateService/SimpleUpdateActionInfo",
          "@odata.type": "#ActionInfo.v1_4_0.ActionInfo",
          "Id": "SimpleUpdateActionInfo",
          "Name": "SimpleUpdate ActionInfo",
          "Parameters": [
            {"Name":"ImageURI",        "Required":True,  "DataType":"String"},
            {"Name":"TransferProtocol","Required":False, "DataType":"String","AllowableValues":["HTTP","HTTPS","FTP"]},
            {"Name":"Targets",         "Required":False, "DataType":"StringArray"},
            {"Name":"UserName",        "Required":False, "DataType":"String"},
            {"Name":"Password",        "Required":False, "DataType":"String"}
          ]
        }, 200


@update_ns.route("/UpdateService/Actions/UpdateCdu.SimpleUpdate")
class ActionsUpdateCduSimpleUpdatee(Resource):
    @update_ns.expect(upload_parser) 
    @update_ns.doc(consumes=['multipart/form-data'])       
    def post(self):
        
        ORIGIN_UPLOAD_API =f"{CDU_BASE}/api/v1/update_firmware"
        file = request.files.get("File")

        if not file:
            return {"error": "No file uploaded"}, 400
        
        files = {"file": (file.filename, file.stream, file.mimetype)}
        # print("files:", files)
        try:
            r = requests.post(ORIGIN_UPLOAD_API, files=files, timeout=(10, None))
            r.raise_for_status()
        except requests.HTTPError:
            return r.json() if r.headers.get("Content-Type","").startswith("application/json") else {"error": r.text}, r.status_code
        except requests.RequestException as e:
            return {"error": "upload failed", "details": str(e)}, 502
        
        return "upload success", 200
        
    
# @update_ns.route("/UpdateService/FirmwareInventory/PC")
# class FirmwareInventoryPC(Resource):
#     def get(self):

#         return FirmwareInventoryPC_data   

# @update_ns.route("/UpdateService/FirmwareInventory/PLC")
# class FirmwareInventoryPLC(Resource):
#     def get(self):

#         return FirmwareInventoryPLC_data   