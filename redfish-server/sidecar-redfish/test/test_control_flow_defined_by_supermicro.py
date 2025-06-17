'''
測試supermicro定義的cdu控制流程
'''
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
from pydantic import BaseModel

cdu_id = 1

# class PatchControlTestCase(BaseModel):
#     endpoint: str
#     get_endpoint: str
#     payload: dict

# 用api來開關sensor會產生很多冗餘的程式，因此使用一個controller來包裝
class TestChassisController:
    pass

##
# PATCH testcase
##
fan_cnt = int(os.getenv("REDFISH_FAN_COLLECTION_CNT", 1))
pump_cnt = int(os.getenv("REDFISH_PUMP_COLLECTION_CNT", 1))
powersupply_cnt = int(os.getenv("REDFISH_POWERSUPPLY_COLLECTION_CNT", 1))

# 取得control值(GET)
endpoint_Control = f'/redfish/v1/Chassis/{cdu_id}/Controls'
# 設定control值(PATCH)
endpoint_ThermalSubsystem_Fans = f'/redfish/v1/Chassis/{cdu_id}/ThermalSubsystem/Fans'
endpoint_Control_Oem_Supermicro_Operation = f'/redfish/v1/Chassis/{cdu_id}/Controls/Oem/Supermicro/Operation'



"""
Supermicro指定的control測項
@see https://docs.google.com/spreadsheets/d/17wUQT6gknXt-3O08U7qBTuJxTU0cLX-X/edit?gid=156057379#gid=156057379
"""
supermicro_test_cases = [
    {
        "method": "PATCH",
        "endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Actions/CoolingUnit.SetMode',
        "get_endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}',
        "payload": {
            "Mode": "Disabled"
        }
    },
    {
        "method": "PATCH",
        "endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/PrimaryCoolantConnectors/1',
        "get_endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}',
        "payload": {
            "SupplyTemperatureControlCelsius": {
                "SetPoint": 30,
                "ControlMode": "Automatic"
            },
            "DeltaPressureControlkPa": {
                "SetPoint": 50,
                "ControlMode": "Automatic"
            }
        }
    },
    {
        "method": "PATCH",
        "endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/PrimaryCoolantConnectors/1',
        "get_endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}',
        "payload": {
            "SupplyTemperatureControlCelsius": {
                "SetPoint": 35,
                "ControlMode": "Automatic"
            },
            "DeltaPressureControlkPa": {
                "SetPoint": 70,
                "ControlMode": "Automatic"
            }
        }
    },
    {
        "method": "PATCH",
        "endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Actions/CoolingUnit.SetMode',
        "get_endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}',
        "payload": {
            "Mode": "Disabled"
        }
    },
    {
        "method": "PATCH",
        "endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Actions/CoolingUnit.SetMode',
        "get_endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}',
        "payload": {
            "Mode": "Enabled"
        }
    },
    {
        "method": "PATCH",
        "endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Actions/CoolingUnit.SetMode',
        "get_endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}',
        "payload": {
            "Mode": "Disabled"
        }
    },
] + [
    {
        "method": "PATCH",
        "endpoint": f'/redfish/v1/Chassis/1/ThermalSubsystem/Fans/{sn}',
        "get_endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}',
        "payload": {
            "SpeedControlPercent": {
                "SetPoint": 50 - 10*(sn % 2),
                "ControlMode": "Manual"
            }
        }
    }
    for sn in range(1, fan_cnt + 1)
] + [
    {
        "method": "PATCH",
        "endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Pumps/{sn}',
        "get_endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}',
        "payload": {
            "SpeedControlPercent": {
                "SetPoint": 50 - 20*(sn % 2),
                "ControlMode": "Manual"
            }
        }
    }
    for sn in range(1, pump_cnt + 1)
] + [
    {
        "method": "PATCH",
        "endpoint": f'/redfish/v1/Chassis/1/ThermalSubsystem/Fans/{sn}',
        "get_endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}',
        "payload": {
            "SpeedControlPercent": {
                "SetPoint": 80 - 20*(sn % 2),
                "ControlMode": "Manual"
            }
        }
    }
    for sn in range(1, fan_cnt + 1)
] + [
    {
        "method": "PATCH",
        "endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Pumps/{sn}',
        "get_endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}',
        "payload": {
            "SpeedControlPercent": {
                "SetPoint": 80 - 20*(sn % 2),
                "ControlMode": "Manual"
            }
        }
    }
    for sn in range(1, pump_cnt + 1)
] + [
    {
        "method": "PATCH",
        "endpoint": f'/redfish/v1/Chassis/1/Controls/Oem/Supermicro/Operation',
        "get_endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}',
        "payload": {
            "ControlMode": "Manual",
            "Pump1Switch": True,
            "Pump2Switch": True,
            "Pump3Switch": True
        }
    },
    {
        "method": "PATCH",
        "endpoint": f'/redfish/v1/Chassis/1/Controls/Oem/Supermicro/Operation',
        "get_endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}',
        "payload": {
            "ControlMode": "Manual",
            "Pump1Switch": True,
            "Pump2Switch": True,
            "Pump3Switch": False
        }
    },
    {
        "method": "PATCH",
        "endpoint": f'/redfish/v1/Chassis/1/Controls/Oem/Supermicro/Operation',
        "get_endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}',
        "payload": {
            "ControlMode": "Manual",
            "Pump1Switch": True,
            "Pump2Switch": False,
            "Pump3Switch": False
        }
    },
    {
        "method": "PATCH",
        "endpoint": f'/redfish/v1/Chassis/1/Controls/Oem/Supermicro/Operation',
        "get_endpoint": f'/redfish/v1/ThermalEquipment/CDUs/{cdu_id}',
        "payload": {
            "ControlMode": "Manual",
            "Pump1Switch": False,
            "Pump2Switch": False,
            "Pump3Switch": False
        }
    },
]





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

@pytest.mark.parametrize('testcase', supermicro_test_cases)
def test_supermicro_test_cases__only_patch(client, basic_auth_header, testcase):
    """[TestCase] Supermicro test cases
    """
    time.sleep(0.5)

    index = supermicro_test_cases.index(testcase) + 1
    print(f"Running test case {index}/{len(supermicro_test_cases)}: {testcase}")

    payload = testcase['payload']
    # 更新設定值
    print(f"## Update target value:")
    print(f"Http method: {testcase['method']}")
    print(f"Endpoint: {testcase['endpoint']}")
    print(f"Payload: {payload}")
    response = client.patch(testcase['endpoint'], headers=basic_auth_header, json=payload)
    print(f"Response json: {json.dumps(response.json, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    print(f"PASS: PATCH {testcase['endpoint']} with payload {payload} is expected to return 200")



@pytest.mark.parametrize('testcase', supermicro_test_cases)
def test_supermicro_test_cases_patch_and_get(client, basic_auth_header, testcase):
    """[TestCase] Supermicro test cases
    """
    payload = testcase['payload']
    # 更新設定值
    print(f"## Update target value:")
    print(f"Http method: {testcase['method']}")
    print(f"Endpoint: {testcase['endpoint']}")
    print(f"Payload: {payload}")
    response = client.patch(testcase['endpoint'], headers=basic_auth_header, json=payload)
    print(f"Response json: {json.dumps(response.json, indent=2, ensure_ascii=False)}")
    assert response.status_code == 200
    print(f"PASS: PATCH {testcase['endpoint']} with payload {payload} is expected to return 200")


    # 取得設定值 (存於PLC的register)
    target_value = payload['FanSetPoint']
    wating_seconds = 1
    print(f"## Waiting for PLC to update target value: {target_value}")
    while wating_seconds < 30:
        print(f"Wait {wating_seconds} seconds...")
        time.sleep(wating_seconds)
        wating_seconds = wating_seconds * 2
        print(f"Http method: GET")
        print(f"Endpoint: {testcase['get_endpoint']}")
        response = client.get(testcase['get_endpoint'], headers=basic_auth_header)
        resp_json = response.json   
        print(f"Response json: {json.dumps(resp_json, indent=2, ensure_ascii=False)}")
        if resp_json['Oem']['Supermicro']['FanSetPoint'] == target_value:
            break
    assert resp_json['Oem']['Supermicro']['FanSetPoint'] == target_value
    print(f"PASS: GET {testcase['get_endpoint']} is expected resp_json.Oem.Supermicro.FanSetPoint == target_value ({target_value})")
    
    
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

            if payload["FanSetPoint"] > 1:
                judge_result = ReadingJudgerPolicy3(client, uri=endpoint, basic_auth_header=basic_auth_header).judge(target_value)
                print(f"Judge result: {judge_result}")
                assert judge_result['is_judge_success'] == True
                print(f"PASS: Judge reading value from policy2 is judged to {judge_result['is_judge_success']}.")
            else:
                judge_result = ReadingJudgerPolicy3(client, uri=endpoint, basic_auth_header=basic_auth_header).judge(0)
                print(f"Judge result: {judge_result}")
                assert judge_result['is_judge_success'] == True
                print(f"PASS: Judge reading value from policy2 is judged to be 0.")
        
        except Exception as e:
            print(f"Error: {e}")
            raise e            




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



        
    