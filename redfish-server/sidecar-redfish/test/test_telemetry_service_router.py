import os
import json
import pytest
import sys
import time
test_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(test_root)
from .conftest import print_response_details
from unittest.mock import MagicMock, patch
from http import HTTPStatus
from mylib.models.rf_resource_model import RfResetType
from mylib.models.rf_manager_model import RfResetToDefaultsType
from mylib.utils.DateTimeUtil import DateTimeUtil



telemetry_service_testcases = [
    {
        "endpoint": f'/redfish/v1/TelemetryService',
        "assert_cases": {
            "@odata.id": "/redfish/v1/TelemetryService",
            "@odata.type": "#TelemetryService.v1_3_4.TelemetryService",
            "@odata.context": "/redfish/v1/$metadata#TelemetryService.v1_3_4.TelemetryService",
            "Id": "TelemetryService",
        }
    },
    {
        "endpoint": f'/redfish/v1/TelemetryService/MetricReports',
        "assert_cases": {
            "@odata.id": "/redfish/v1/TelemetryService/MetricReports",
            # "Members@odata.count": -1,
            "Members": [
                {
                "@odata.id": "/redfish/v1/TelemetryService/MetricReports/1"
                },
                {
                "@odata.id": "/redfish/v1/TelemetryService/MetricReports/2"
                },
                {
                "@odata.id": "/redfish/v1/TelemetryService/MetricReports/3"
                }
            ]
        }
    },
    {
        "endpoint": f'/redfish/v1/TelemetryService/MetricReports/1',
        "assert_cases": {
            "@odata.id": "/redfish/v1/TelemetryService/MetricReports/1",
            "Id": "CDU_Report_001",
            "Timestamp": os.getenv("DATETIME_FORMAT"),
            "MetricValues": [
                {
                    "MetricId": "temp_clntSply",
                    "MetricValue": 0,
                    "Timestamp": "2025-03-31T08:00:00Z"
                },
                {
                    "MetricId": "temp_clntSplySpare",
                    "MetricValue": 0,
                    "Timestamp": "2025-03-31T08:00:00Z"
                },
            ]
        }
    },
]




##                                                                                                             
# NNNNNNNN        NNNNNNNN                                                                               lllllll 
# N:::::::N       N::::::N                                                                               l:::::l 
# N::::::::N      N::::::N                                                                               l:::::l 
# N:::::::::N     N::::::N                                                                               l:::::l 
# N::::::::::N    N::::::N   ooooooooooo   rrrrr   rrrrrrrrr      mmmmmmm    mmmmmmm     aaaaaaaaaaaaa    l::::l 
# N:::::::::::N   N::::::N oo:::::::::::oo r::::rrr:::::::::r   mm:::::::m  m:::::::mm   a::::::::::::a   l::::l 
# N:::::::N::::N  N::::::No:::::::::::::::or:::::::::::::::::r m::::::::::mm::::::::::m  aaaaaaaaa:::::a  l::::l 
# N::::::N N::::N N::::::No:::::ooooo:::::orr::::::rrrrr::::::rm::::::::::::::::::::::m           a::::a  l::::l 
# N::::::N  N::::N:::::::No::::o     o::::o r:::::r     r:::::rm:::::mmm::::::mmm:::::m    aaaaaaa:::::a  l::::l 
# N::::::N   N:::::::::::No::::o     o::::o r:::::r     rrrrrrrm::::m   m::::m   m::::m  aa::::::::::::a  l::::l 
# N::::::N    N::::::::::No::::o     o::::o r:::::r            m::::m   m::::m   m::::m a::::aaaa::::::a  l::::l 
# N::::::N     N:::::::::No::::o     o::::o r:::::r            m::::m   m::::m   m::::ma::::a    a:::::a  l::::l 
# N::::::N      N::::::::No:::::ooooo:::::o r:::::r            m::::m   m::::m   m::::ma::::a    a:::::a l::::::l
# N::::::N       N:::::::No:::::::::::::::o r:::::r            m::::m   m::::m   m::::ma:::::aaaa::::::a l::::::l
# N::::::N        N::::::N oo:::::::::::oo  r:::::r            m::::m   m::::m   m::::m a::::::::::aa:::al::::::l
# NNNNNNNN         NNNNNNN   ooooooooooo    rrrrrrr            mmmmmm   mmmmmm   mmmmmm  aaaaaaaaaa  aaaallllllll
##
@pytest.mark.parametrize("testcase", telemetry_service_testcases)
def test_telemetry_service_normal_api(client, basic_auth_header, testcase):
    """[TestCase] TelemetryService API"""
    # 獲取當前測試案例的序號
    index = telemetry_service_testcases.index(testcase) + 1
    print(f"Running test case {index}/{len(telemetry_service_testcases)}: {testcase}")

    print(f"Endpoint: {testcase['endpoint']}")
    response = client.get(testcase['endpoint'], headers=basic_auth_header)
    resp_json = response.json
    print(f"Response: {resp_json}")
    assert response.status_code == 200
    
    print(f"Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
    for key, value in testcase['assert_cases'].items():
        try:
            if key == "MetricValues":
                assert len(resp_json[key]) > 3
            elif key == "Members":
                assert len(resp_json[key]) == resp_json["Members@odata.count"]
            elif key == "Timestamp":
                assert DateTimeUtil.is_match_format(resp_json[key], os.getenv("DATETIME_FORMAT"))
            elif key == "Status":
                assert isinstance(resp_json["Status"], dict)
                # assert resp_json["Status"]["State"] in ["Absent", "Enabled", "Disabled"]
                assert resp_json["Status"]["Health"] in ["OK", "Warning", "Critical"]
            else:
                assert resp_json[key] == value
            
            print(f"PASS: `{key}` of response json is expected to be {value}")
        except AssertionError as e:
            print(f"AssertionError: {e}, key: {key}, value: {value}")
            raise e
