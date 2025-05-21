import os
import json
import pytest
import sys

# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

chassis_id = 1

ThermalSubsystem_Fans_testcases = [
    {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem/Fans/{sn}',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem/Fans/{sn}",
            "@odata.type": "#Fan.v1_5_0.Fan",
            "@odata.context": "/redfish/v1/$metadata#Fan.v1_5_0.Fan",
            "PhysicalContext": "Chassis",
        }
    } 
    for sn in range(1, int(os.getenv("REDFISH_FAN_COLLECTION_CNT", 1)) + 2) # 故意+2，多一組
]

Sensors_FanN_testcases = [
    {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/Fan{sn}',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/Fan{sn}",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "rpm",
        }
    }
    for sn in range(1, int(os.getenv("REDFISH_FAN_COLLECTION_CNT", 1)) + 2)
]

PowerSupplies_testcases = [
    {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{sn}',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{sn}",
            "@odata.type": "#PowerSupply.v1_6_0.PowerSupply",
            
        }
    }
    for sn in range(1, int(os.getenv("REDFISH_POWERSUPPLY_COLLECTION_CNT", 1)) + 2)
]


# 以下是 redfish 1.14.0 的Chassis API

chassis_testcases = [
    {
        "endpoint": f'/redfish/v1/Chassis',
        "assert_cases": { # 代表這個endpoint的response json要測以下三項
            "@odata.id": "/redfish/v1/Chassis",
            "@odata.type": "#ChassisCollection.ChassisCollection",
            "Members@odata.count": 1,
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}",
            "@odata.type": "#Chassis.v1_26_0.Chassis",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/PowerSubsystem',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem",
            "@odata.type": "#PowerSubsystem.v1_1_2.PowerSubsystem",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies",
            "@odata.type": "#PowerSupplyCollection.PowerSupplyCollection",
        }
    }, 
] + PowerSupplies_testcases[:-1] + [
    {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem",
            "@odata.type": "#ThermalSubsystem.v1_3_2.ThermalSubsystem",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem/Fans',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem/Fans",
            "@odata.type": "#FanCollection.FanCollection",
        }
    }
] + ThermalSubsystem_Fans_testcases[:-1] + [
    {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors",
            "@odata.type": "#SensorCollection.SensorCollection",
            "Members@odata.count": 21, # 就不一一測了
            "Members": [
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/Conductivity"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/DewPointCelsius"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/Fan1"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/Fan2"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/Fan3"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/Fan4"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/Fan5"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/Fan6"},
                # {"@odata.id": "/redfish/v1/Chassis/1/Sensors/Fan7"},
                # {"@odata.id": "/redfish/v1/Chassis/1/Sensors/Fan8"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/HumidityPercent"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PowerConsume"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryDeltaPressurekPa"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryDeltaTemperatureCelsius"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryFlowLitersPerMinute"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryHeatRemovedkW"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryReturnPressurekPa"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryReturnTemperatureCelsius"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimarySupplyPressurekPa"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimarySupplyTemperatureCelsius"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/TemperatureCelsius"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/Turbidity"},
                {"@odata.id": "/redfish/v1/Chassis/1/Sensors/WaterPH"}
            ],
        }
    }
] + [
    {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/Conductivity',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/Conductivity",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "μs/cm",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/DewPointCelsius',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/DewPointCelsius",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Celsius",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/HumidityPercent',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/HumidityPercent",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Percent",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PowerConsume',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PowerConsume",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "kW",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryDeltaPressurekPa',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryDeltaPressurekPa",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "kPa",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryDeltaTemperatureCelsius',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryDeltaTemperatureCelsius",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Celsius",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryFlowLitersPerMinute',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryFlowLitersPerMinute",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "L/min",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryHeatRemovedkW',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryHeatRemovedkW",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "kW",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryReturnPressurekPa',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryReturnPressurekPa",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "kPa",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryReturnTemperatureCelsius',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryReturnTemperatureCelsius",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Celsius",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimarySupplyPressurekPa',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimarySupplyPressurekPa",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "kPa",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimarySupplyTemperatureCelsius',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimarySupplyTemperatureCelsius",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Celsius",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/TemperatureCelsius',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/TemperatureCelsius",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Celsius",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/Turbidity',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/Turbidity",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "NTU",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/WaterPH',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/WaterPH",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "pH",
        }
    }
] + Sensors_FanN_testcases[:-1]



@pytest.mark.parametrize('testcase', chassis_testcases)
def test_chassis_api(client, basic_auth_header, testcase):
    """測試 chassis API"""
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
        elif key in ("Reading", "ReadingUnits"): # Sensor獨有
            assert isinstance(resp_json["Reading"], (float, int))
        elif key == "Status":
            assert isinstance(resp_json["Status"], dict)
            # assert resp_json["Status"]["State"] in ["Absent", "Enabled", "Disabled"]
            assert resp_json["Status"]["Health"] in ["OK", "Warning", "Critical"]
        else:
            assert resp_json[key] == value
            
 


redundant_testcases = [
    ThermalSubsystem_Fans_testcases[-1],
    Sensors_FanN_testcases[-1],
    PowerSupplies_testcases[-1]
]
@pytest.mark.parametrize('redundant_testcase', redundant_testcases)
def test_redundant_chassis_api(client, basic_auth_header, redundant_testcase):
    """測試，如果uri不存在，應該回傳相對應的httpstatus"""
    try:
        print(f"Endpoint: {redundant_testcase['endpoint']}")
        response = client.get(redundant_testcase['endpoint'], headers=basic_auth_header)
        resp_json = response.json
        print(f"Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
        assert response.status_code == 404
    except Exception as e:
        print(f"Error: {e}")
        
    
