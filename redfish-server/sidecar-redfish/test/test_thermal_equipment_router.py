import os
import json
import pytest
import sys

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 以下是 redfish 1.14.0 的Chassis API
cdu_id = 1

thermal_equipment_reserviors_testcases = [
    {
        "endpoint": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Reservoirs",
        "assert_cases": {
            "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Reservoirs",
            "@odata.type": "#ReservoirCollection.ReservoirCollection",
            "Members@odata.count": int(os.getenv("REDFISH_RESERVOIR_COLLECTION_CNT", 1)),
            "Members": [
                {"@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Reservoirs/{sn}"}
                for sn in range(1, int(os.getenv("REDFISH_RESERVOIR_COLLECTION_CNT", 1)) + 1)
            ],
        }
    }
] + [
    {
        "endpoint": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Reservoirs/{sn}",
        "assert_cases": {
            "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Reservoirs/{sn}",
            "@odata.type": "#Reservoir.v1_0_0.Reservoir",
        }
    }
    for sn in range(1, int(os.getenv("REDFISH_RESERVOIR_COLLECTION_CNT", 1)) + 1)
]

thermal_equipment_leakdetection_testcases = [
    {
        "endpoint": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/LeakDetection",
        "assert_cases": {
            "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/LeakDetection",
            "@odata.type": "#LeakDetection.v1_1_0.LeakDetection",
        }
    }, {
        "endpoint": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/LeakDetection/LeakDetectors",
        "assert_cases": {
            "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/LeakDetection/LeakDetectors",
            "@odata.type": "#LeakDetectorCollection.LeakDetectorCollection",
            "Members@odata.count": 1,
        }
    }
]

thermal_equipment_testcases = [
    {
        "endpoint": f"/redfish/v1/ThermalEquipment/CDUs",
        "assert_cases": { # 代表這個endpoint的response json要測以下三項
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs",
            "@odata.type": "#CoolingUnitCollection.CoolingUnitCollection",
            "@odata.context": "/redfish/v1/$metadata#CoolingUnitCollection.CoolingUnitCollection",

            "Members@odata.count": int(os.getenv("REDFISH_CDUS_COLLECTION_CNT", 1)),
            "Members": [
                {"@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{sn}"}
                for sn in range(1, int(os.getenv("REDFISH_CDUS_COLLECTION_CNT", 1)) + 1)
            ],
        }
    },
    {
        "endpoint": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/PrimaryCoolantConnectors",
        "assert_cases": { # 代表這個endpoint的response json要測以下三項
            "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/PrimaryCoolantConnectors",
            "@odata.type": "#CoolantConnectorCollection.CoolantConnectorCollection",
            "Members@odata.count": int(os.getenv("REDFISH_PRIMARYCOOLANTCONNECTORS_COLLECTION_CNT", 1)),
            "Members": [
                {"@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/PrimaryCoolantConnectors/{sn}"}
                for sn in range(1, int(os.getenv("REDFISH_PRIMARYCOOLANTCONNECTORS_COLLECTION_CNT", 1)) + 1)
            ],
        }
    },
    {
        "endpoint": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/EnvironmentMetrics",
        "assert_cases": { 
            "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/EnvironmentMetrics",
            "@odata.type": "#EnvironmentMetrics.v1_3_2.EnvironmentMetrics",
        }
    },
    {
        "endpoint": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Pumps",
        "assert_cases": { # 代表這個endpoint的response json要測以下三項
            "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Pumps",
            "@odata.type": "#PumpCollection.PumpCollection",
            "Members@odata.count": int(os.getenv("REDFISH_PUMP_COLLECTION_CNT", 1)),
            "Members": [
                {"@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Pumps/{sn}"}
                for sn in range(1, int(os.getenv("REDFISH_PUMP_COLLECTION_CNT", 1)) + 1)
            ],
        }
    }
] + [
    {
        "endpoint": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Pumps/{sn}",
        "assert_cases": {
            "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Pumps/{sn}",
            "@odata.type": "#Pump.v1_2_0.Pump",
            "Id": f"{sn}",
        }
    } 
    for sn in range(1, int(os.getenv("REDFISH_PUMP_COLLECTION_CNT", 1)) + 1)
]
# thermal_equipment_testcases += thermal_equipment_reserviors_testcases 
thermal_equipment_testcases += thermal_equipment_leakdetection_testcases


@pytest.mark.parametrize('testcase', thermal_equipment_testcases)
def test_thermal_equipment_api(client, basic_auth_header, testcase):
    """[TestCase] thermal_equipment API"""
    print(f"Endpoint: {testcase['endpoint']}")
    response = client.get(testcase['endpoint'], headers=basic_auth_header)
    assert response.status_code == 200
    
    resp_json = response.json
    print(f"Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
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
            
 
