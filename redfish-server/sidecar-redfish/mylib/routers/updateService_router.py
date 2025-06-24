from flask_restx import Namespace, Resource
from flask import request
from datetime import datetime
import requests
import os
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
            "target": "/redfish/v1/UpdateService/Actions/UpdateService.SimpleUpdate",
            "@Redfish.ActionInfo": "/redfish/v1/UpdateService/SimpleUpdateActionInfo"
        }
    },
}

FirmwareInventory_data = {
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory",
    "@odata.type": "#SoftwareInventoryCollection.SoftwareInventoryCollection",
    "Name": "Firmware Inventory",

    "Members@odata.count": 2, # 未串
    "Members": [
        {"@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/WebInterface"},
        {"@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/ControlUnit_1"}
    ],
}

WebInterface_data = {
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/WebInterface" ,
    "@odata.type": "#SoftwareInventory.v1_3_0.SoftwareInventory",
    "Id": "WebInterface",
    "Name": "Web Interface firmware",
    "Manufacturer": "supermicro",
    # 更新日
    "ReleaseDate": "2025-02-21T06:02:08Z",
    # 是否可更新
    "Updateable": True,    
    "Version": "ok",
    "SoftwareId": "WEB-INTERFACE",
    "Oem": {
        # "supermicro": {
        #     "@odata.type": "#SMC.supermicro.Redfish",
        #     "Redfish": "N/A",
        # }
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
        release_date = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/display/version")["version"]["Release_Time"]
        # fmt = os.getenv("DATETIME_FORMAT") 
        # dt = datetime.strptime(release_date, "%Y-%m-%d %H:%M:%S")
        # release_date = dt.strftime(fmt)
        WebInterface_data["ReleaseDate"] = release_date + "T"
        WebInterface_data["Version"] = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/display/version")["fw_info"]["WebUI"]
        # WebInterface_data["Oem"]["supermicro"]["Redfish"] = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/display/version")["version"]["Redfish_Server"]
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

@update_ns.route("/UpdateService/FirmwareInventory/ControlUnit_1")
class FirmwareInventoryControlUnit_1(Resource):
    def get(self):
        controlunit1_data = {
            "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/ControlUnit_1" ,
            "@odata.type": "#SoftwareInventory.v1_3_0.SoftwareInventory",
            "Id": "ControlUnit_1",
            "Name": "PLC version",
            "Manufacturer": "supermicro",
            # 更新日
            # "ReleaseDate": "2025-02-21T06:02:08Z", # TBD
            # 是否可更新
            "Updateable": False,    
            "Version": str(load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/display/version")["version"]["PLC"]),
            "SoftwareId": "PLC-VERSION",
            "Oem": {}
        }
        return controlunit1_data

@update_ns.route("/UpdateService/SimpleUpdateActionInfo")
class SimpleUpdateActionInfo(Resource):
    def get(self):
        return {
          "@odata.context": "/redfish/v1/$metadata#ActionInfo.ActionInfo",
          "@odata.id": "/redfish/v1/UpdateService/SimpleUpdateActionInfo",
          "@odata.type": "#ActionInfo.v1_4_2.ActionInfo",
          "Id": "SimpleUpdateActionInfo",
          "Description": "SimpleUpdate ActionInfo",
          "Name": "SimpleUpdate ActionInfo",
          
          "Parameters": [
            {"Name":"ImageURI",        "Required":True,  "DataType":"String"}, # 必填欄位
            # {"Name":"TransferProtocol","Required":False, "DataType":"String","AllowableValues":["HTTP","HTTPS","FTP"]},
            # {"Name":"Targets",         "Required":False, "DataType":"StringArray"},
            # {"Name":"UserName",        "Required":False, "DataType":"String"},
            # {"Name":"Password",        "Required":False, "DataType":"String"}
          ]
        }, 200


@update_ns.route("/UpdateService/Actions/UpdateService.SimpleUpdate")
class ActionsUpdateCduSimpleUpdate(Resource):
    @update_ns.expect(upload_parser) 
    @update_ns.doc(consumes=['multipart/form-data'])       
    def post(self):
        ORIGIN_UPLOAD_API = f"{CDU_BASE}/api/v1/update_firmware"

        # 檢查是否是 JSON 請求
        if request.is_json:
            try:
                data = request.get_json()
                image_uri = data.get("ImageURI")

                if image_uri:
                    # 下載檔案

                    file_download = requests.get(image_uri, timeout=60)
                    if file_download.status_code != 200:
                        return {"error": f"Download failed: HTTP {file_download.status_code}"}, 400

                    # 下載成功後，準備檔案傳遞給內部 API
                    files = {"file": ("upload.gpg", file_download.content, "application/pgp-encrypted")}
                    r = requests.post(ORIGIN_UPLOAD_API, files=files, timeout=(10, None))
                    return "upload success, it will reboot", 200
                else:
                    return {"error": "Missing ImageURI in JSON"}, 400
            except requests.RequestException as e:
                return {"error": "Download or upload failed", "details": str(e)}, 502
            except Exception as e:
                return {"error": f"Internal Error: {str(e)}"}, 500

        # 檢查是否有檔案上傳
        elif 'ImageFile' in request.files:
            try:
                file = request.files.get("ImageFile")
                if not file:
                     return {"error": "No file uploaded"}, 400
                files = {"file": (file.filename, file.stream, file.mimetype)}
                r = requests.post(ORIGIN_UPLOAD_API, files=files, timeout=(10, None))
                return "upload success, it will reboot", 200
            except requests.HTTPError:
                return r.json() if r.headers.get("Content-Type","").startswith("application/json") else {"error": r.text}, r.status_code
            except requests.RequestException as e:
                return {"error": "upload failed", "details": str(e)}, 502
        
        # 如果既沒有檔案也沒有 ImageURI，返回錯誤
        return {"error": "No file or ImageURI provided"}, 400
        
        
        
    
# @update_ns.route("/UpdateService/FirmwareInventory/PC")
# class FirmwareInventoryPC(Resource):
#     def get(self):

#         return FirmwareInventoryPC_data   

# @update_ns.route("/UpdateService/FirmwareInventory/PLC")
# class FirmwareInventoryPLC(Resource): 
#     def get(self):

#         return FirmwareInventoryPLC_data   