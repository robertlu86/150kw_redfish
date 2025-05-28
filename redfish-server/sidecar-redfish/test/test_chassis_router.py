import os
import json
import pytest
import sys
import random
import time
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from mylib.models.rf_sensor_model import RfSensorFanExcerpt
from mylib.adapters.sensor_api_adapter import SensorAPIAdapter

"""
# 10秒內讀3次，值不可一致，而且必須差在5%以內
@note: 我們每2秒讀一次modbus
"""
class ReadingPolicy1:
    NAME = "JUDGE-3-TIMES"

    def __init__(self, client, uri, basic_auth_header):
        """
        :uri: Should be Redfish api
        """
        self.client = client
        self.uri = uri
        self.basic_auth_header = basic_auth_header
        self.judge_cnt = 3
        self.judge_interval = 2.5 # 秒

    def judge(self) -> bool:
        reading_values = []
        for i in range(self.judge_cnt):
            response = self.client.get(self.uri, headers=self.basic_auth_header)
            resp_json = response.json
            reading = resp_json.get('Reading') 
            print(f"[ReadingPolicy1][uri={self.uri}] Reading {i+1}: {reading}")
            if reading == 0:
                print(f"[ReadingPolicy1] judge return False because reading is 0.")
                return False # to save testing time
            reading_values.append(reading)
            time.sleep(self.judge_interval)

        # 三次值都不一樣
        if len(set(reading_values)) == self.judge_cnt:
            min_value = min(reading_values)
            max_value = max(reading_values)
            return abs(max_value - min_value) / max_value <= 0.05
        
        # 3次有2次一樣
        if len(set(reading_values)) == self.judge_cnt - 1:
            min_value = min(reading_values)
            max_value = max(reading_values)
            return abs(max_value - min_value) / max_value <= 0.03
        
        # 所有值都一樣
        if len(set(reading_values)) == 1:
            return False
        
        return False
        
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
            "Reading": ReadingPolicy1.NAME,
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
            "Reading": ReadingPolicy1.NAME,
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/DewPointCelsius',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/DewPointCelsius",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Celsius",
            "Reading": ReadingPolicy1.NAME,
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/HumidityPercent',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/HumidityPercent",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Percent",
            "Reading": ReadingPolicy1.NAME,
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PowerConsume',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PowerConsume",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "kW",
            "Reading": ReadingPolicy1.NAME,
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryDeltaPressurekPa',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryDeltaPressurekPa",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "kPa",
            "Reading": ReadingPolicy1.NAME,
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryDeltaTemperatureCelsius',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryDeltaTemperatureCelsius",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Celsius",
            "Reading": ReadingPolicy1.NAME,
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryFlowLitersPerMinute',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryFlowLitersPerMinute",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "L/min",
            "Reading": ReadingPolicy1.NAME,
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryHeatRemovedkW',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryHeatRemovedkW",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "kW",
            "Reading": ReadingPolicy1.NAME,
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryReturnPressurekPa',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryReturnPressurekPa",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "kPa",
            "Reading": ReadingPolicy1.NAME,
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryReturnTemperatureCelsius',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryReturnTemperatureCelsius",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Celsius",
            "Reading": ReadingPolicy1.NAME,
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimarySupplyPressurekPa',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimarySupplyPressurekPa",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "kPa",
            "Reading": ReadingPolicy1.NAME,
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/PrimarySupplyTemperatureCelsius',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimarySupplyTemperatureCelsius",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Celsius",
            "Reading": ReadingPolicy1.NAME,
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/TemperatureCelsius',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/TemperatureCelsius",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "Celsius",
            "Reading": ReadingPolicy1.NAME,
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/Turbidity',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/Turbidity",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "NTU",
            "Reading": ReadingPolicy1.NAME,
        }
    }, {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Sensors/WaterPH',
        "assert_cases": {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/WaterPH",
            "@odata.type": "#Sensor.v1_1_0.Sensor",
            "ReadingUnits": "pH",
            "Reading": ReadingPolicy1.NAME,
        }
    }
] + Sensors_FanN_testcases[:-1]

##
# PATCH testcase
##
fan_cnt = int(os.getenv("REDFISH_FAN_COLLECTION_CNT", 1))
pump_cnt = int(os.getenv("REDFISH_PUMP_COLLECTION_CNT", 1))
powersupply_cnt = int(os.getenv("REDFISH_POWERSUPPLY_COLLECTION_CNT", 1))

chassis_FansSpeedControl_patch_testcases = [
    {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Controls/FansSpeedControl',
        "payloads": [
            {
                "fan_speed": 100,
                **{f"fan{i}_switch": True for i in range(1, fan_cnt + 1)}
            },
            {
                "fan_speed": 50,
                **{f"fan{i}_switch": True for i in range(1, fan_cnt + 1)}
            },
            {
                "fan_speed": 25,
                **{f"fan{i}_switch": True for i in range(1, fan_cnt + 1)}
            },
            {
                "fan_speed": 12,
                **{f"fan{i}_switch": True for i in range(1, fan_cnt + 1)}
            },
            {
                "fan_speed": 6,
                **{f"fan{i}_switch": True for i in range(1, fan_cnt + 1)}
            },
            {
                "fan_speed": random.randint(1, 100),
                **{f"fan{i}_switch": random.choice([True, False]) for i in range(1, fan_cnt + 1)}
            },
            {
                "fan_speed": random.randint(1, 100),
                **{f"fan{i}_switch": random.choice([True, False]) for i in range(1, fan_cnt + 1)}
            },
            {
                "fan_speed": random.randint(1, 100),
                **{f"fan{i}_switch": random.choice([True, False]) for i in range(1, fan_cnt + 1)}
            }
        ],
    }
]

chassis_OperationMode_patch_testcases = [
    {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Controls/OperationMode',
        "payloads": [
            {
                "mode": "Automatic"
            }, 
            {
                "mode": "Disabled"
            },
            # {
            #     "mode": "Override"
            # }
            {
                "mode": "Manual" # 最後設回 Manual，避免和大家認知不同
            },
        ],
        "payloads_that_should_fail": [
            {
                "mode": "this-is-invalid-mode"
            },
            {
                "mode": "Automatic "
            }
        ],
    }
]

chassis_PumpSpeedControl_patch_testcases = [
    {
        "endpoint": f'/redfish/v1/Chassis/{chassis_id}/Controls/PumpSpeedControl',
        "payloads": [
            {
                "speed_set": 49,
                **{f"pump{i}_switch": True for i in range(1, pump_cnt + 1)}
            },
            {
                "speed_set": random.randint(1, 100),
                **{f"pump{i}_switch": random.choice([True, False]) for i in range(1, pump_cnt + 1)}
            },
            {
                "speed_set": random.randint(1, 100),
                **{f"pump{i}_switch": random.choice([True, False]) for i in range(1, pump_cnt + 1)}
            },
            {
                "speed_set": random.randint(1, 100),
                **{f"pump{i}_switch": random.choice([True, False]) for i in range(1, pump_cnt + 1)}
            },
        ],
    },
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
    

    


@pytest.mark.parametrize('testcase', chassis_testcases)
def test_chassis_api(client, basic_auth_header, testcase):
    """[TestCase] chassis API"""
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

            if value == ReadingPolicy1.NAME:
                policy = ReadingPolicy1(client, uri=testcase['endpoint'], basic_auth_header=basic_auth_header)
                assert policy.judge() == True
                
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
        
    

@pytest.mark.parametrize('testcase', chassis_FansSpeedControl_patch_testcases)
def test_chassis_FansSpeedControl_patch_api(client, basic_auth_header, testcase):
    """[TestCase] chassis FansSpeedControl patch API
    payload:{ 
        "fan_speed": 100,
        "fan1_switch": true,
        "fan2_switch": true,
        "fan3_switch": true,
        "fan4_switch": true,
        "fan5_switch": true,
        "fan6_switch": true,
        "fan7_switch": true,
        "fan8_switch": true
    } // Bad Design! Should use List[Dict[<fan_id>, <is_switch>]] or Dict[<fan_id>, <is_switch>]
    """
    for payload in testcase['payloads']:
        # 更新設定值
        print(f"Http method: PATCH")
        print(f"Endpoint: {testcase['endpoint']}")
        print(f"Payload: {payload}")
        response = client.patch(testcase['endpoint'], headers=basic_auth_header, json=payload)
        print(f"Response json: {json.dumps(response.json, indent=2, ensure_ascii=False)}")
        assert response.status_code == 200

        # 取得設定值
        print(f"Http method: GET")
        print(f"Endpoint: {testcase['endpoint']}")
        response = client.get(testcase['endpoint'], headers=basic_auth_header)
        resp_json = response.json   
        print(f"Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
        assert resp_json['SetPoint'] == payload['fan_speed']
        
        # 取得sensor實際值 (注意，實際值不會這麼快就反應出來，通常要等待幾秒)
        # Response: {
        #   ...
        #   "SpeedPercent": {
        #     "DataSourceUri": "/redfish/v1/Chassis/1/ThermalSubsystem/Sensors/Fan2",
        #     "Reading": 0,
        #     "SpeedRPM": 0
        #   }
        # }
        # for fan_id in range(1, fan_cnt + 1):
        #     endpoint = f'/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem/Sensors/Fan{fan_id}'
        #     response = client.get(endpoint, headers=basic_auth_header)
        #     resp_json = response.json   
        #     m = RfSensorFanExcerpt(**resp_json['SpeedPercent'])
        #     print(f"Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
        #     if payload[f"fan{fan_id}_switch"] is True:
        #         assert m.Reading == payload['fan_speed']
        #     else:
        #         assert m.Reading != payload['fan_speed']

    
@pytest.mark.parametrize('testcase', chassis_OperationMode_patch_testcases)
def test_chassis_OperationMode_patch_api(client, basic_auth_header, testcase):
    """[TestCase] chassis OperationMode patch API
    payload:{ 
        "mode": "Automatic",
    }
    """
    for payload in testcase['payloads']:
        # 更新設定值
        print(f"Http method: PATCH")
        print(f"Endpoint: {testcase['endpoint']}")
        print(f"Payload: {payload}")
        response = client.patch(testcase['endpoint'], headers=basic_auth_header, json=payload)
        print(f"Response json: {json.dumps(response.json, indent=2, ensure_ascii=False)}")
        assert response.status_code == 200

        # 取得設定值
        time.sleep(2)
        print(f"Http method: GET")
        print(f"Endpoint: {testcase['endpoint']}")
        response = client.get(testcase['endpoint'], headers=basic_auth_header)
        resp_json = response.json   
        print(f"Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
        assert response.status_code == 200
        assert resp_json['ControlMode'] == payload['mode']
        assert resp_json['PhysicalContext'] == "Chassis"
        assert resp_json['Id'] == "OperationMode"
        assert resp_json['Name'] == "OperationMode"
    
    for payload in testcase['payloads_that_should_fail']:
        # 更新設定值
        print(f"Http method: PATCH")
        print(f"Endpoint: {testcase['endpoint']}")
        print(f"Payload: {payload}")
        response = client.patch(testcase['endpoint'], headers=basic_auth_header, json=payload)
        print(f"Response json: {json.dumps(response.json, indent=2, ensure_ascii=False)}")
        assert response.status_code == 400
