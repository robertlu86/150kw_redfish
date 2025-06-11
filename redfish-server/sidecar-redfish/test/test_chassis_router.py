import os
import json
import pytest
import sys
import random
import time
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from load_env import hardware_info
from mylib.models.rf_sensor_model import RfSensorFanExcerpt
from mylib.adapters.sensor_api_adapter import SensorAPIAdapter
from conftest import TestcaseFinder
from reading_judger import ReadingJudgerPolicy1, ReadingJudgerPolicy2, ReadingJudgerPolicy3

        
chassis_id = 1

ThermalSubsystem_Fans_testcases = [
    {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem/Fans/{sn}',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem/Fans/{sn}",
            "@odata.type": "#Fan.v1_5_0.Fan",
            "@odata.context": "/redfish/v1/$metadata#Fan.v1_5_0.Fan",
            "PhysicalContext": "Chassis",
            "Description": hardware_info["Fans"].get(str(sn), {}).get("LocatedAt")
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
            "Reading": "(ReadingJudger)",
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

chassis_normal_testcases = [
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
            "@odata.type": "#PowerSubsystem.v1_1_3.PowerSubsystem",
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
            "@odata.type": "#ThermalSubsystem.v1_3_3.ThermalSubsystem",
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
            "Reading": "(ReadingJudger)",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/DewPointCelsius',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/DewPointCelsius",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Celsius",
            "Reading": "(ReadingJudger)",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/HumidityPercent',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/HumidityPercent",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Percent",
            "Reading": "(ReadingJudger)",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PowerConsume',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PowerConsume",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "kW",
            "Reading": "(ReadingJudger)",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryDeltaPressurekPa',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryDeltaPressurekPa",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "kPa",
            "Reading": "(ReadingJudger)",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryDeltaTemperatureCelsius',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryDeltaTemperatureCelsius",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Celsius",
            "Reading": "(ReadingJudger)",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryFlowLitersPerMinute',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryFlowLitersPerMinute",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "L/min",
            "Reading": "(ReadingJudger)",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryHeatRemovedkW',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryHeatRemovedkW",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "kW",
            "Reading": "(ReadingJudger)",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryReturnPressurekPa',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryReturnPressurekPa",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "kPa",
            "Reading": "(ReadingJudger)",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryReturnTemperatureCelsius',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryReturnTemperatureCelsius",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Celsius",
            "Reading": "(ReadingJudger)",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimarySupplyPressurekPa',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimarySupplyPressurekPa",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "kPa",
            "Reading": "(ReadingJudger)",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimarySupplyTemperatureCelsius',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimarySupplyTemperatureCelsius",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Celsius",
            "Reading": "(ReadingJudger)",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/TemperatureCelsius',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/TemperatureCelsius",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Celsius",
            "Reading": "(ReadingJudger)",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/Turbidity',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/Turbidity",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "NTU",
            "Reading": "(ReadingJudger)",
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/WaterPH',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/WaterPH",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "pH",
            "Reading": "(ReadingJudger)",
        }
    }
] + Sensors_FanN_testcases[:-1]


##
# PATCH testcase
##
fan_cnt = int(os.getenv("REDFISH_FAN_COLLECTION_CNT", 1))
pump_cnt = int(os.getenv("REDFISH_PUMP_COLLECTION_CNT", 1))
powersupply_cnt = int(os.getenv("REDFISH_POWERSUPPLY_COLLECTION_CNT", 1))

endpoint_FansSpeedControl = f'/redfish/v1/Chassis/{chassis_id}/Controls/FansSpeedControl'
chassis_FansSpeedControl_patch_testcases = [
    {
        "id": "fan-all-on",
        "endpoint": endpoint_FansSpeedControl,
        "payload": {
            "description": "Manual模式下，風扇全設為ON, speed=50",
            "fan_speed": 50,
            **{f"fan{i}_switch": True for i in range(1, fan_cnt + 1)}
        },
    },
    {
        "id": "fan-random-on-case1",
        "endpoint": endpoint_FansSpeedControl,
        "payload": {
            "description": "Manual模式下，風扇亂數隨機開關, speed=15~60之間隨機選 (case1)",
            "fan_speed": random.randint(15, 60),
            **{f"fan{i}_switch": random.choice([True, False]) for i in range(1, fan_cnt + 1)}
        },
    },
    {
        "id": "fan-random-on-case2",
        "endpoint": endpoint_FansSpeedControl,
        "payload": {
            "description": "Manual模式下，風扇亂數隨機開關, speed=15~60之間隨機選 (case2)",
            "fan_speed": random.randint(15, 60),
            **{f"fan{i}_switch": random.choice([True, False]) for i in range(1, fan_cnt + 1)}
        },
    }
] + [
    {
        "id": f"fan-individual-on-fan{fan_sn}",
        "endpoint": endpoint_FansSpeedControl,
        "payload": {
            "description": f"Manual模式下，風扇個別開, speed={40 + fan_sn*2} (case{fan_sn})",
            "fan_speed": 40 + fan_sn*2,
            **{f"fan{i}_switch": True if i == fan_sn else False for i in range(1, fan_cnt + 1)}
        },
    }
    for fan_sn in range(1, fan_cnt + 1)
]

endpoint_OperationMode = f'/redfish/v1/Chassis/{chassis_id}/Controls/OperationMode'
chassis_OperationMode_patch_testcases = [
    {
        "id": "automatic", # [DRY] easy to find for other test cases
        "endpoint": endpoint_OperationMode,
        "payload": { 
            "mode": "Automatic" 
        }
    },
    {
        "id": "disabled",
        "endpoint": endpoint_OperationMode,
        "payload": { 
            "mode": "Disabled" 
        }
    },
    {
        "id": "manual",
        "endpoint": endpoint_OperationMode,
        "payload": { 
            "mode": "Manual" 
        }
    },
]

chassis_OperationMode_patch_fail_testcases = [
    {
        "endpoint": endpoint_OperationMode,
        "payload": { 
            "mode": "this-is-invalid-mode" 
        }
    },
    {
        "endpoint": endpoint_OperationMode,
        "payload": { 
            "mode": "Automatic " 
        }
    },
]



endpoint_PumpsSpeedControl = f'/redfish/v1/Chassis/{chassis_id}/Controls/PumpsSpeedControl'
chassis_PumpsSpeedControl_patch_testcases = [
    {
        "id": "pump-all-on",
        "endpoint": endpoint_PumpsSpeedControl,
        "payload": {
            "description": "Manual模式下，pump全設為ON, speed=50",
            "speed_set": 50,
            **{f"pump{i}_switch": True for i in range(1, pump_cnt + 1)}
        },
    },
    {
        "id": "pump-random-on",
        "endpoint": endpoint_PumpsSpeedControl,
        "payload": {
            "description": "Manual模式下，pump亂數隨機開關, speed=25~60之間隨機選 (case1)",
            "speed_set": random.randint(25, 60),
            **{f"pump{i}_switch": random.choice([True, False]) for i in range(1, pump_cnt + 1)}
        },
    },
    {
        "id": "pump-random-on-2",
        "endpoint": endpoint_PumpsSpeedControl,
        "payload": {
            "description": "Manual模式下，pump亂數隨機開關, speed=25~60之間隨機選 (case2)",
            "speed_set": random.randint(25, 60),
            **{f"pump{i}_switch": random.choice([True, False]) for i in range(1, pump_cnt + 1)}
        },
    }
] + [
    {
        "id": f"pump-individual-on-pump{pump_sn}",
        "endpoint": endpoint_PumpsSpeedControl,
        "payload": {
            "description": f"Manual模式下，pump個別開, speed={40 + pump_sn*2} (case{pump_sn})",
            "speed_set": 40 + pump_sn*2,
            **{f"pump{i}_switch": True if i == pump_sn else False for i in range(1, pump_cnt + 1)}
        },
    }
    for pump_sn in range(1, pump_cnt + 1)
]

chassis_ThermalSubsystem_Fans_patch_testcases = [
    {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem/Fans/{sn}',
        "payloads": [
            { "fan_switch": random.choice([True, False]) },
            { "fan_switch": random.choice([True, False]) },
            { "fan_switch": random.choice([True, False]) },
        ],
    } 
    for sn in range(1, fan_cnt + 1)
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
@pytest.mark.parametrize('testcase', chassis_normal_testcases)
def test_chassis_normal_api(client, basic_auth_header, testcase):
    """[TestCase] chassis API"""
    # 獲取當前測試案例的序號
    index = chassis_normal_testcases.index(testcase) + 1
    print(f"Running test case {index}/{len(chassis_normal_testcases)}: {testcase}")

    print(f"Endpoint: {testcase['endpoint']}")
    response = client.get(testcase['endpoint'], headers=basic_auth_header)
    assert response.status_code == 200
    
    resp_json = response.json
    print(f"Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
    for key, value in testcase['assert_cases'].items():
        try:
            # Members比較特殊，排序後確認內容
            if key == "Members":
                resp_json[key] = sorted(resp_json[key], key=lambda x: x['@odata.id'])
                assert resp_json[key] == value
            elif key in ("ReadingUnits"): # Sensor獨有
                assert isinstance(resp_json["Reading"], (float, int))    
            elif key == "Reading":
                    policy = ReadingJudgerPolicy1(client, uri=testcase['endpoint'], basic_auth_header=basic_auth_header)
                    # policy = ReadingJudgerPolicy2(client, uri=testcase['endpoint'], basic_auth_header=basic_auth_header)
                    judge_result = policy.judge()
                    print(f"Reading: {resp_json['Reading']}, Judge result: {judge_result}")
                    assert judge_result["is_judge_success"] == True
            elif key == "Status":
                assert isinstance(resp_json["Status"], dict)
                # assert resp_json["Status"]["State"] in ["Absent", "Enabled", "Disabled"]
                assert resp_json["Status"]["Health"] in ["OK", "Warning", "Critical"]
            else:
                assert resp_json[key] == value
            
            print(f"PASS: `{key}` of response json is expected to be {value}")
        except AssertionError as e:
            print(f"AssertionError: {e}, key: {key}, value: {value}")
            #raise
            

redundant_testcases = [
    {
        "endpoint": f'/redfish/v1/Chassis/9999',
    },
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
        print(f"PASS: Endpoint: {redundant_testcase['endpoint']} is expected to return 404")
    except Exception as e:
        print(f"FAIL: Endpoint: {redundant_testcase['endpoint']} is expected to return 404, but got {e}")
        raise e
        
    
@pytest.mark.parametrize('testcase', Sensors_FanN_testcases[:-1])
def test_fan_sensors_should_be_corrected(client, basic_auth_header, testcase):
    """[TestCase] Fan sensors should be corrected.
    i.e., fan sensor value should equal to `SetPoint` from /FansSpeedControl
    """
    # get setting value
    print("## Get sensor target value:")
    endpoint = f"/redfish/v1/Chassis/{chassis_id}/Controls/FansSpeedControl"
    response = client.get(endpoint, headers=basic_auth_header)
    target_value = response.json['SetPoint'] 
    print(f"Sensor target value is {target_value}")
    assert target_value != 0

    print("## Check sensor value:")
    response = client.get(testcase['endpoint'], headers=basic_auth_header)
    resp_json = response.json
    # m = RfSensorFanExcerpt(**resp_json['Reading'])
    print(f"- Endpoint: {testcase['endpoint']}")
    print(f"  Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
    sensor_value = resp_json['Reading']
    assert ReadingJudgerPolicy1.validate_sensor_value_in_reasonable_vibration(sensor_value, target_value) == True



##
# RRRRRRRRRRRRRRRRR                                                  d::::::d  iiii                                       
# R::::::::::::::::R                                                 d::::::d i::::i                                      
# R::::::RRRRRR:::::R                                                d::::::d  iiii                                       
# RR:::::R     R:::::R                                               d:::::d                                              
#   R::::R     R:::::R    eeeeeeeeeeee    aaaaaaaaaaaaa      ddddddddd:::::d iiiiiiinnnn  nnnnnnnn       ggggggggg   ggggg
#   R::::R     R:::::R  ee::::::::::::ee  a::::::::::::a   dd::::::::::::::d i:::::in:::nn::::::::nn    g:::::::::ggg::::g
#   R::::RRRRRR:::::R  e::::::eeeee:::::eeaaaaaaaaa:::::a d::::::::::::::::d  i::::in::::::::::::::nn  g:::::::::::::::::g
#   R:::::::::::::RR  e::::::e     e:::::e         a::::ad:::::::ddddd:::::d  i::::inn:::::::::::::::ng::::::ggggg::::::gg
#   R::::RRRRRR:::::R e:::::::eeeee::::::e  aaaaaaa:::::ad::::::d    d:::::d  i::::i  n:::::nnnn:::::ng:::::g     g:::::g 
#   R::::R     R:::::Re:::::::::::::::::e aa::::::::::::ad:::::d     d:::::d  i::::i  n::::n    n::::ng:::::g     g:::::g 
#   R::::R     R:::::Re::::::eeeeeeeeeee a::::aaaa::::::ad:::::d     d:::::d  i::::i  n::::n    n::::ng:::::g     g:::::g 
#   R::::R     R:::::Re:::::::e         a::::a    a:::::ad:::::d     d:::::d  i::::i  n::::n    n::::ng::::::g    g:::::g 
# RR:::::R     R:::::Re::::::::e        a::::a    a:::::ad::::::ddddd::::::ddi::::::i n::::n    n::::ng:::::::ggggg:::::g 
# R::::::R     R:::::R e::::::::eeeeeeeea:::::aaaa::::::a d:::::::::::::::::di::::::i n::::n    n::::n g::::::::::::::::g 
# R::::::R     R:::::R  ee:::::::::::::e a::::::::::aa:::a d:::::::::ddd::::di::::::i n::::n    n::::n  gg::::::::::::::g 
# RRRRRRRR     RRRRRRR    eeeeeeeeeeeeee  aaaaaaaaaa  aaaa  ddddddddd   dddddiiiiiiii nnnnnn    nnnnnn    gggggggg::::::g 
#                                                                                                                 g:::::g 
#                                                                                                     gggggg      g:::::g 
#                                                                                                     g:::::gg   gg:::::g 
#                                                                                                      g::::::ggg:::::::g 
#                                                                                                       gg:::::::::::::g  
#                                                                                                         ggg::::::ggg    
#                                                                                                            gggggg       
##

@pytest.mark.parametrize('testcase', Sensors_FanN_testcases[:-1])
def test_fan_sensors_should_be_corrected(client, basic_auth_header, testcase):
    """[TestCase] Fan sensors should be corrected.
    i.e., fan sensor value should equal to `SetPoint` from /FansSpeedControl
    @note: 這個case可用於測試，已經有目標值的情況下(例如剛剛PATCH)，想確認sensor值是否正確
    """
    print("## Get sensor target value:")
    endpoint = f"/redfish/v1/Chassis/{chassis_id}/Controls/FansSpeedControl"
    response = client.get(endpoint, headers=basic_auth_header)
    target_value = response.json['SetPoint'] 
    print(f"Sensor target value is {target_value}")
    # assert target_value != 0
    # print(f"PASS: Target value from `{endpoint}` is expected NOT to be 0")

    print("## Check sensor value:")
    response = client.get(testcase['endpoint'], headers=basic_auth_header)
    resp_json = response.json
    print(f"- Endpoint: {testcase['endpoint']}")
    print(f"  Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
    sensor_value = resp_json['Reading']
    assert ReadingJudgerPolicy1.validate_sensor_value_in_reasonable_vibration(sensor_value, target_value) == True
    print(f"PASS: Sensor value, {sensor_value}, from `{testcase['endpoint']}` is expected to be in reasonable vibration range")

    judge_result = ReadingJudgerPolicy2(client, uri=testcase['endpoint'], basic_auth_header=basic_auth_header).judge(target_value)
    print(f"Judge result: {judge_result}")
    assert judge_result['is_judge_success'] == True
    print(f"PASS: Judge reading value from policy2 is judged to {judge_result['is_judge_success']}")


##                                                                                                       
# PPPPPPPPPPPPPPPPP        AAA         TTTTTTTTTTTTTTTTTTTTTTT       CCCCCCCCCCCCCHHHHHHHHH     HHHHHHHHH
# P::::::::::::::::P      A:::A        T:::::::::::::::::::::T    CCC::::::::::::CH:::::::H     H:::::::H
# P::::::PPPPPP:::::P    A:::::A       T:::::::::::::::::::::T  CC:::::::::::::::CH:::::::H     H:::::::H
# PP:::::P     P:::::P  A:::::::A      T:::::TT:::::::TT:::::T C:::::CCCCCCCC::::CHH::::::H     H::::::HH
#   P::::P     P:::::P A:::::::::A     TTTTTT  T:::::T  TTTTTTC:::::C       CCCCCC  H:::::H     H:::::H  
#   P::::P     P:::::PA:::::A:::::A            T:::::T       C:::::C                H:::::H     H:::::H  
#   P::::PPPPPP:::::PA:::::A A:::::A           T:::::T       C:::::C                H::::::HHHHH::::::H  
#   P:::::::::::::PPA:::::A   A:::::A          T:::::T       C:::::C                H:::::::::::::::::H  
#   P::::PPPPPPPPP A:::::A     A:::::A         T:::::T       C:::::C                H:::::::::::::::::H  
#   P::::P        A:::::AAAAAAAAA:::::A        T:::::T       C:::::C                H::::::HHHHH::::::H  
#   P::::P       A:::::::::::::::::::::A       T:::::T       C:::::C                H:::::H     H:::::H  
#   P::::P      A:::::AAAAAAAAAAAAA:::::A      T:::::T        C:::::C       CCCCCC  H:::::H     H:::::H  
# PP::::::PP   A:::::A             A:::::A   TT:::::::TT       C:::::CCCCCCCC::::CHH::::::H     H::::::HH
# P::::::::P  A:::::A               A:::::A  T:::::::::T        CC:::::::::::::::CH:::::::H     H:::::::H
# P::::::::P A:::::A                 A:::::A T:::::::::T          CCC::::::::::::CH:::::::H     H:::::::H
# PPPPPPPPPPAAAAAAA                   AAAAAAATTTTTTTTTTT             CCCCCCCCCCCCCHHHHHHHHH     HHHHHHHHH
#
# @see https://patorjk.com/software/taag/#p=display&f=Doh&t=PATCH
# @note 硬體的設計，風扇的speed值(轉速值)介於0~100，且所有風扇的speed值必須一致。但是可以單獨開關風扇。一旦風扇被關，預期sensor的reading值為0。
# @note pump同上。
##                                                                                                       
                                                                                                       
@pytest.mark.parametrize('testcase', chassis_FansSpeedControl_patch_testcases)
def test_chassis_FansSpeedControl_patch_api(client, basic_auth_header, testcase):
    """[TestCase] chassis FansSpeedControl patch API
    payload:{ 
        "fan_speed": 50,
        "fan1_switch": true,
        "fan2_switch": true,
        "fan3_switch": true,
        "fan4_switch": true,
        ...
    } // Bad Design! Should use List[Dict[<fan_id>, <is_switch>]] or Dict[<fan_id>, <is_switch>]
    """
    payload = testcase['payload']
    # 更新設定值
    print(f"## Update target value:")
    print(f"Http method: PATCH")
    print(f"Endpoint: {testcase['endpoint']}")
    print(f"Payload: {payload}")
    response = client.patch(testcase['endpoint'], headers=basic_auth_header, json=payload)
    print(f"Response json: {json.dumps(response.json, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    print(f"PASS: PATCH {testcase['endpoint']} with payload {payload} is expected to return 200")


    # 取得設定值 (存於PLC的register)
    target_value = payload['fan_speed']
    wating_seconds = 1
    print(f"## Waiting for PLC to update target value: {target_value}")
    while wating_seconds < 30:
        print(f"Wait {wating_seconds} seconds...")
        time.sleep(wating_seconds)
        wating_seconds = wating_seconds * 2
        print(f"Http method: GET")
        print(f"Endpoint: {testcase['endpoint']}")
        response = client.get(testcase['endpoint'], headers=basic_auth_header)
        resp_json = response.json   
        print(f"Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
        if resp_json['SetPoint'] == target_value:
            break
    assert resp_json['SetPoint'] == target_value
    print(f"PASS: GET {testcase['endpoint']} is expected resp_json.SetPoint == target_value ({target_value})")
    
    
    # 取得sensor實際值 (注意，實際值不會這麼快就反應出來，通常要等待幾秒)
    # Endpoint: f'/redfish/v1/Chassis/{chassis_id}/Sensors/Fan{fan_id}'
    # Response: {
    #     ...
    #     "Reading": 0,
    #     "ReadingUnits": "rpm",
    # }
    print(f"## Wait for fan sensor value reaching the target value: {target_value}")
    time.sleep(10)
    print(f"## Check Sensor Value:")
    for fan_id in range(1, fan_cnt + 1):
        try:
            endpoint = f'/redfish/v1/Chassis/{chassis_id}/Sensors/Fan{fan_id}'
            response = client.get(endpoint, headers=basic_auth_header)
            resp_json = response.json   
            # m = RfSensorFanExcerpt(**resp_json['Reading'])
            print(f"Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
            sensor_value = resp_json['Reading']
            if payload[f"fan{fan_id}_switch"] is True:
                # assert ReadingJudgerPolicy1.validate_sensor_value_in_reasonable_vibration(sensor_value, payload['fan_speed']) == True
                # print(f"PASS: Sensor value, {sensor_value}, from `{endpoint}` is expected to be in reasonable vibration range")

                judge_result = ReadingJudgerPolicy3(client, uri=endpoint, basic_auth_header=basic_auth_header).judge(target_value)
                print(f"Judge result: {judge_result}")
                assert judge_result['is_judge_success'] == True
                print(f"PASS: Judge reading value from policy2 is judged to {judge_result['is_judge_success']}.")
            else:
                # assert ReadingJudgerPolicy1.validate_sensor_value_in_reasonable_vibration(sensor_value, 0) == True
                # print(f"PASS: Sensor value, {sensor_value}, from `{endpoint}` is expected to be 0")

                judge_result = ReadingJudgerPolicy3(client, uri=endpoint, basic_auth_header=basic_auth_header).judge(0)
                print(f"Judge result: {judge_result}")
                assert judge_result['is_judge_success'] == True
                print(f"PASS: Judge reading value from policy2 is judged to be 0.")
        except Exception as e:
            print(f"Error: {e}")
            raise e
            

@pytest.mark.parametrize('testcase', chassis_PumpsSpeedControl_patch_testcases)
def test_chassis_PumpsSpeedControl_patch_api(client, basic_auth_header, testcase):
    """[TestCase] chassis FansSpeedControl patch API
    payload:{ 
        "speed_set": 50,
        "pump1_switch": true,
        "pump2_switch": true,
        "pump3_switch": true
        ...
    @note: N個pump的設定值只會有一個，但會對應N個sensor
    } 
    """
    payload = testcase['payload']
    # 更新設定值
    print(f"## Http method: PATCH")
    print(f"Endpoint: {testcase['endpoint']}")
    print(f"Payload: {payload}")
    response = client.patch(testcase['endpoint'], headers=basic_auth_header, json=payload)
    print(f"Response json: {json.dumps(response.json, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    print(f"PASS: PATCH {testcase['endpoint']} with payload {payload} is expected to return 200")


    # 取得設定值
    target_value = payload['speed_set']
    wating_seconds = 1
    print(f"## Waiting for PLC to update target value: {target_value}")
    while wating_seconds < 30:
        time.sleep(wating_seconds)
        wating_seconds = wating_seconds * 2
        print(f"## Http method: GET")
        print(f"Endpoint: {testcase['endpoint']}")
        response = client.get(testcase['endpoint'], headers=basic_auth_header)
        resp_json = response.json   
        print(f"Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
        if resp_json['SetPoint'] == target_value:
            break
    assert resp_json['SetPoint'] == target_value
    print(f"PASS: GET {testcase['endpoint']} is expected resp_json.SetPoint == target_value ({target_value})")
    
    # 取得sensor實際值 (注意，實際值不會這麼快就反應出來，通常要等待幾秒)
    # URI: /redfish/v1/ThermalEquipment/CDUs/1/Pumps/1
    # Response: {
    #     ...
    #     "PumpSpeedPercent": {
    #         "Reading": 49,
    #         "SpeedRPM": 4.9
    #     },
    # }
    print(f"## Wait for pump sensor value reaching the target value: {target_value}")
    time.sleep(10)
    print(f"## Check Sensor Value:")
    for pump_id in range(1, pump_cnt + 1):
        endpoint = f'/redfish/v1/ThermalEquipment/CDUs/1/Pumps/{pump_id}'
        response = client.get(endpoint, headers=basic_auth_header)
        resp_json = response.json   
        # m = RfSensorFanExcerpt(**resp_json['PumpSpeedPercent'])
        print(f"- Endpoint: {endpoint}")
        print(f"  Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
        sensor_value = resp_json['PumpSpeedPercent']['Reading']
        judge_policy = ReadingJudgerPolicy3(
                client, 
                uri=endpoint, 
                basic_auth_header=basic_auth_header,
                params={ "judge_interval": 1 }
            )
        if payload[f"pump{pump_id}_switch"] is True:
            # assert ReadingJudgerPolicy1.validate_sensor_value_in_reasonable_vibration(sensor_value, payload['speed_set']) == True

            judge_result = judge_policy.judge(target_value)
            print(f"Judge result: {judge_result}")
            assert judge_result['is_judge_success'] == True
            print(f"PASS: Judge reading value from policy2 is judged to be {judge_result['is_judge_success']} (target_value: {target_value}).")
        else:
            # assert ReadingJudgerPolicy1.validate_sensor_value_in_reasonable_vibration(sensor_value, 0) == True

            judge_result = judge_policy.judge(0)
            print(f"Judge result: {judge_result}")
            assert judge_result['is_judge_success'] == True
            print(f"PASS: Judge reading value from policy2 is judged to be {judge_result['is_judge_success']} (target_value: 0).")


@pytest.mark.parametrize('testcase', chassis_OperationMode_patch_testcases)
def test_chassis_OperationMode_patch_api(client, basic_auth_header, testcase):
    """[TestCase] chassis OperationMode patch API
    payload:{ 
        "mode": "Automatic",
    }
    """
    payload = testcase['payload']
    # 更新設定值
    print(f"Http method: PATCH")
    print(f"Endpoint: {testcase['endpoint']}")
    print(f"Payload: {payload}")
    response = client.patch(testcase['endpoint'], headers=basic_auth_header, json=payload)
    print(f"Response json: {json.dumps(response.json, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200

    # 取得設定值
    time.sleep(3)
    print(f"Http method: GET")
    print(f"Endpoint: {testcase['endpoint']}")
    response = client.get(testcase['endpoint'], headers=basic_auth_header)
    resp_json = response.json   
    print(f"Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    assert resp_json['ControlMode'] == payload['mode']
    assert resp_json['PhysicalContext'] == "Chassis"
    assert resp_json['Id'] == "OperationMode"
    assert resp_json['Name'] == "Operation Mode"
    print(f"PASS: PATCH {testcase['endpoint']} with payload {payload} is expected to return 200")
    
@pytest.mark.parametrize('testcase', chassis_OperationMode_patch_fail_testcases)
def test_chassis_OperationMode_patch_fail_api(client, basic_auth_header, testcase):
    """[TestCase] chassis OperationMode patch fail API
    payload:{ 
        "mode": "Automatic",
    }
    """
    payload = testcase['payload']
    # 更新設定值
    print(f"Http method: PATCH")
    print(f"Endpoint: {testcase['endpoint']}")
    print(f"Payload: {payload}")
    response = client.patch(testcase['endpoint'], headers=basic_auth_header, json=payload)
    print(f"Response json: {json.dumps(response.json, indent=2, ensure_ascii=False)}")
    assert response.status_code == 400
    print(f"PASS: PATCH {testcase['endpoint']} with payload {payload} is expected to return 400")


##
#                AAA                                     tttt                           
#               A:::A                                 ttt:::t                           
#              A:::::A                                t:::::t                           
#             A:::::::A                               t:::::t                           
#            A:::::::::A        uuuuuu    uuuuuuttttttt:::::ttttttt       ooooooooooo   
#           A:::::A:::::A       u::::u    u::::ut:::::::::::::::::t     oo:::::::::::oo 
#          A:::::A A:::::A      u::::u    u::::ut:::::::::::::::::t    o:::::::::::::::o
#         A:::::A   A:::::A     u::::u    u::::utttttt:::::::tttttt    o:::::ooooo:::::o
#        A:::::A     A:::::A    u::::u    u::::u      t:::::t          o::::o     o::::o
#       A:::::AAAAAAAAA:::::A   u::::u    u::::u      t:::::t          o::::o     o::::o
#      A:::::::::::::::::::::A  u::::u    u::::u      t:::::t          o::::o     o::::o
#     A:::::AAAAAAAAAAAAA:::::A u:::::uuuu:::::u      t:::::t    tttttto::::o     o::::o
#    A:::::A             A:::::Au:::::::::::::::uu    t::::::tttt:::::to:::::ooooo:::::o
#   A:::::A               A:::::Au:::::::::::::::u    tt::::::::::::::to:::::::::::::::o
#  A:::::A                 A:::::Auu::::::::uu:::u      tt:::::::::::tt oo:::::::::::oo 
# AAAAAAA                   AAAAAAA uuuuuuuu  uuuu        ttttttttttt     ooooooooooo   
##                                                                                      


chassis_AutoMode_PumpsSpeedControl_patch_testcases = [
    {
        "before_hands": [
            TestcaseFinder(chassis_OperationMode_patch_testcases).find_testcase_by_id("manual"), # manual mode
            TestcaseFinder(chassis_PumpsSpeedControl_patch_testcases).find_testcase_by_id("pump-all-on"), # pump全開
        ],
        "id": "auto-mode-to-test-pump",
        "endpoint": endpoint_OperationMode,
        "payload": {
            "mode": "Automatic"
        },
    }
]

@pytest.mark.parametrize('testcase', chassis_AutoMode_PumpsSpeedControl_patch_testcases)
def test_chassis_AutoMode_patch_api(client, basic_auth_header, testcase):
    """[TestCase] chassis AutoMode patch API
    """
    # 前置動作: (1)設為manual mode (2)pump全ON
    before_hands = testcase['before_hands']
    target_value = 0
    for before_hand in before_hands:
        print(f"## Http method: PATCH")
        print(f"Endpoint: {before_hand['endpoint']}")
        print(f"Payload: {before_hand['payload']}")
        if 'speed_set' in before_hand['payload']:
            target_value = before_hand['payload']['speed_set']
        response = client.patch(before_hand['endpoint'], headers=basic_auth_header, json=before_hand['payload'])
        print(f"Response json: {json.dumps(response.json, indent=2, ensure_ascii=False)}")
        assert response.status_code == 200
        print(f"PASS: Complete before_hand: {before_hand.get('id')}")
        time.sleep(2)
    
    # 更新設定值: 設為AutoMode
    print(f"## Http method: PATCH")
    print(f"Endpoint: {testcase['endpoint']}")
    print(f"Payload: {testcase['payload']}")
    response = client.patch(testcase['endpoint'], headers=basic_auth_header, json=testcase['payload'])
    print(f"Response json: {json.dumps(response.json, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    print(f"PASS: Set to AutoMode")
    
    # 取得pump sensor值
    time.sleep(5)
    pump_on_cnt = 0
    pump_off_cnt = 0
    for pump_id in range(1, pump_cnt + 1):
        endpoint = f'/redfish/v1/ThermalEquipment/CDUs/1/Pumps/{pump_id}'
        response = client.get(endpoint, headers=basic_auth_header)
        resp_json = response.json   
        # m = RfSensorFanExcerpt(**resp_json['PumpSpeedPercent'])
        print(f"- Endpoint: {endpoint}")
        print(f"  Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")

        judge_policy = ReadingJudgerPolicy3(
                client, 
                uri=endpoint, 
                basic_auth_header=basic_auth_header,
                params={ "judge_interval": 1 }
            )
        judge_result = judge_policy.judge(target_value)
        judge_result_zero = judge_policy.judge_by_reading_values(0, judge_result['reading_values'])
        if judge_result_zero['is_judge_success']:
            pump_off_cnt += 1
        if judge_result['is_judge_success']:
            pump_on_cnt += 1
    
    assert pump_on_cnt > 0 and pump_off_cnt == 1
    print(f"PASS: Only one pump sensor value is expected to be 0")
        
    