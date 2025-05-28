import os
import json
import pytest
import sys
import time
from io import BytesIO
test_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(test_root)
from .conftest import print_response_details


endpoint = "/redfish/v1/UpdateService/Actions/UpdateCdu.SimpleUpdate"

updateservice_testcases = [
    {
        "endpoint": f"/redfish/v1/UpdateService",
        "assert_cases": { 
            "@odata.id": f"/redfish/v1/UpdateService",
            "@odata.type": "#UpdateService.v1_14_0.UpdateService",
            "Id": "UpdateService",
            # "FirmwareInventory": {
            #     "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory"
            # },
            # "Actions": {
            #     "#UpdateService.SimpleUpdate": {
            #         "target": "/redfish/v1/UpdateService/Actions/UpdateCdu.SimpleUpdate",
            #         "@Redfish.ActionInfo": "/redfish/v1/UpdateService/SimpleUpdateActionInfo"
            #     }
            # }
        }
    },
    {
        "endpoint": "/redfish/v1/UpdateService/FirmwareInventory",
        "assert_cases": { 
            "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory",
            "@odata.type": "#SoftwareInventoryCollection.SoftwareInventoryCollection",
            "Name": "Firmware Inventory",
            "Members@odata.count": 1,
            "Members": [
                {
                    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/WebInterface"
                }
            ],
        }
    },
    {
        "endpoint": "/redfish/v1/UpdateService/FirmwareInventory/WebInterface",
        "assert_cases": { 
            "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/WebInterface",
            "@odata.type": "#SoftwareInventory.v1_3_0.SoftwareInventory",
            "Name": "Web Interface firmware",
            "Updateable": True,
            # "Version": "0103",
            "SoftwareId": "WEB-INTERFACE"
        }
    },
]


def test_update_service_upload(client, basic_auth_header):
    """[TestCase] update_service API: /redfish/v1/UpdateService/Actions/UpdateCdu.SimpleUpdate"""
    print(f"Endpoint: {endpoint}")
    
    file = None
    filename = "testcase-updateservice-example.zip.gpg"
    filepath = os.path.join(test_root, filename)
    with open(filepath, "rb") as f:
        file = BytesIO(f.read())
        file.name = filename
        # file.seek(0)  
    
    data = {
        "File": (file, filename)
    }
    t1 = time.time()
    # response = client.post(endpoint, headers=basic_auth_header, data={"File": file})
    response = client.post(
        endpoint,
        headers=basic_auth_header,
        data=data,
        content_type="multipart/form-data"
    )
    t2 = time.time()

    print_response_details(response)

    assert response.status_code == 200 # 200代表上傳&更新韌體成功 (這邊是sync.的設計)
    assert t2 - t1 < 120 # 120秒內完成
    
def test_update_service_upload_noPassword(client, basic_auth_header):
    """[TestCase] update_service API: /redfish/v1/UpdateService/Actions/UpdateCdu.SimpleUpdate (noPassword)
    Expect:
        Http status: 400
        Response json:
            {
                "message": "ZIP file must be password-protected"
            }
    """
    print(f"Endpoint: {endpoint}")
    file = None
    filename = "testcase-updateservice-example-noPassword.zip.gpg"
    filepath = os.path.join(test_root, filename)
    

    with open(filepath, "rb") as f:
        file = BytesIO(f.read())
        file.name = filename
    
    data = {
        "File": (file, filename)
    }    
    # response = client.post(endpoint, headers=basic_auth_header, data={"File": file})
    response = client.post(
        endpoint,
        headers=basic_auth_header,
        data=data,
        content_type="multipart/form-data"
    )
    print_response_details(response)
    assert response.status_code == 400
    
def test_update_service_upload_noSpareDir(client, basic_auth_header):
    """[TestCase] update_service API: /redfish/v1/UpdateService/Actions/UpdateCdu.SimpleUpdate (noSpareDir)"""
    print(f"Endpoint: {endpoint}")
    
    file = None
    filename = "testcase-updateservice-example-noSpareDir.zip.gpg"
    filepath = os.path.join(test_root, filename)
    with open(filepath, "rb") as f:
        file = BytesIO(f.read())
        file.name = filename
    
    data = {
        "File": (file, filename)
    }
    t1 = time.time()
    # response = client.post(endpoint, headers=basic_auth_header, data={"File": file})
    response = client.post(
        endpoint,
        headers=basic_auth_header,
        data=data,
        content_type="multipart/form-data"
    )
    t2 = time.time()
    print_response_details(response, **data)
    # assert response.status_code != 200 # 200代表上傳&更新韌體成功
    assert response.status_code == 200 # why要設計成資料不完整也能更新成功？
            
 
@pytest.mark.parametrize('testcase', updateservice_testcases)
def test_updateservice_api(client, basic_auth_header, testcase):
    """[TestCase] updateservice API"""
    print(f"Endpoint: {testcase['endpoint']}")
    response = client.get(testcase['endpoint'], headers=basic_auth_header)
    assert response.status_code == 200
    
    resp_json = response.json
    print_response_details(response)
    for key, value in testcase['assert_cases'].items():
        # Members比較特殊，排序後確認內容
        if key == "Members":
            resp_json[key] = sorted(resp_json[key], key=lambda x: x['@odata.id'])
            assert resp_json[key] == value
        elif key == "Status":
            assert isinstance(resp_json["Status"], dict)
            # assert resp_json["Status"]["State"] in ["Absent", "Enabled", "Disabled"]
            assert resp_json["Status"]["Health"] in ["OK", "Warning", "Critical"]
        else:
            assert resp_json[key] == value