import os
import json
import pytest
import sys
import time
from io import BytesIO
test_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(test_root)
from .conftest import print_response_details
from unittest.mock import MagicMock, patch
from http import HTTPStatus
from mylib.models.rf_resource_model import RfResetType
from mylib.models.rf_manager_model import RfResetToDefaultsType
from flask import Response


managers_cdu_reset_to_defaults_testcases = [
    {
        "endpoint": f"/redfish/v1/Managers/CDU/Actions/Manager.ResetToDefaults",
        "payload": {
            "ResetType": RfResetToDefaultsType.ResetAll.value
        },
        "assert_cases": { 
            "status_code": HTTPStatus.OK,
        }
    },
    {
        "endpoint": f"/redfish/v1/Managers/CDU/Actions/Manager.ResetToDefaults",
        "payload": {
            "ResetType": "Invalid"
        },
        "assert_cases": { 
            "status_code": HTTPStatus.BAD_REQUEST,
        }
    },
]

managers_cdu_reset_testcases = [
    {
        "endpoint": f"/redfish/v1/Managers/CDU/Actions/Manager.Reset",
        "payload": {
            "ResetType": RfResetType.ForceRestart.value
        },
        "assert_cases": { 
            "status_code": HTTPStatus.OK,
        }
    },
    {
        "endpoint": f"/redfish/v1/Managers/CDU/Actions/Manager.Reset",
        "payload": {
            "ResetType": RfResetType.GracefulRestart.value
        },
        "assert_cases": { 
            "status_code": HTTPStatus.OK,
        }
    },
    {
        "endpoint": f"/redfish/v1/Managers/CDU/Actions/Manager.Reset",
        "payload": {
            "ResetType": "Invalid"
        },
        "assert_cases": { 
            "status_code": HTTPStatus.BAD_REQUEST,
        }
    },
]

@pytest.mark.parametrize("testcase", managers_cdu_reset_to_defaults_testcases)
def test_manager_cdu_reset_to_defaults(client, basic_auth_header, testcase):
    """[TestCase] manager CDU reset_to_defaults"""
    endpoint = testcase["endpoint"]
    print(f"Endpoint: {endpoint}")
    
    with patch('mylib.adapters.webapp_api_adapter.WebAppAPIAdapter.reset_to_defaults') as mock:
        mock.return_value = Response(
            status=HTTPStatus.OK,
            response=json.dumps({"message": "Reset to defaults Successfully"}),
        )
    
        resp = client.post(endpoint, headers=basic_auth_header, json=testcase["payload"])
        print_response_details(resp)

        assert resp.status_code == testcase["assert_cases"]["status_code"]
        print(f"PASS: POST {endpoint} by MagicMock response HTTPStatus={testcase['assert_cases']['status_code']}")

@pytest.mark.parametrize("testcase", managers_cdu_reset_testcases)
def test_manager_cdu_reset(client, basic_auth_header, testcase):
    """[TestCase] manager CDU reset"""
    endpoint = testcase["endpoint"]
    print(f"Endpoint: {endpoint}")
    
    with patch('mylib.adapters.webapp_api_adapter.WebAppAPIAdapter.reset') as mock:
        mock.return_value = Response(
            status=HTTPStatus.OK,
            response=json.dumps({"message": "Reset Successfully"}),
        )
    
        resp = client.post(endpoint, headers=basic_auth_header, json=testcase["payload"])
        print_response_details(resp)

        assert resp.status_code == testcase["assert_cases"]["status_code"]
        print(f"PASS: POST {endpoint} by MagicMock response HTTPStatus={testcase['assert_cases']['status_code']}")

    
