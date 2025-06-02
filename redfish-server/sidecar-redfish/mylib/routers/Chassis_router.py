from flask import request
from flask_restx import Namespace, Resource, fields
from flask import abort
from http import HTTPStatus
from mylib.services.rf_chassis_service import RfChassisService
from mylib.utils.load_api import load_raw_from_api 
from mylib.utils.load_api import CDU_BASE
import requests
import os
from typing import Dict
from mylib.common.my_resource import MyResource
from mylib.utils.system_info import get_mac_uuid


Chassis_ns = Namespace('', description='Chassis Collection')

Chassis_data = {
    "@odata.id": "/redfish/v1/Chassis",
    "@odata.type": "#ChassisCollection.ChassisCollection",
    "@odata.context": "/redfish/v1/$metadata#ChassisCollection.ChassisCollection",
    "Name": "Chassis Collection",
    "Members@odata.count": 1,
    "Members": [{"@odata.id": "/redfish/v1/Chassis/1"}],
    "Description": "A collection of all chassis resources",
    "Oem": {}
}

Chassis_data_1 = {
    "@odata.id": "/redfish/v1/Chassis/1",
    "@odata.type": "#Chassis.v1_26_0.Chassis",
    "@odata.context":  "/redfish/v1/$metadata#Chassis.v1_26_0.Chassis",
    
    "Id": "1",
    "Name": "Catfish System Chassis",
    "Description": "Main rack-mount chassis for Catfish System",
    # 標準硬體資訊
    "ChassisType": "RackMount",
    "Manufacturer": "Supermicro",
    "Model": "CDU 150kW",
    "SerialNumber": "130001",
    "PartNumber": "LCS-SCDU-1K3LR001",
    "UUID": "00000000-0000-0000-0000-e45f013e98f8", # 機殼 UUID (未做)
    "AssetTag": "TBD", #  (未做)
    "SKU": "TBD", # 機殼硬體版本或型號 (未做)
    "Version": "ok", # 機殼軟體版本或型號 
    
    # 狀態與指示燈 (status 未做)
    "PowerState": "On",
    "LocationIndicatorActive": True,
    "Status": {
        "State": "Enabled", 
        "Health": "OK"
    },
    
    # 各子系統連結
    "PowerSubsystem": {"@odata.id": "/redfish/v1/Chassis/1/PowerSubsystem"},
    "ThermalSubsystem": {"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem"},
    "EnvironmentMetrics": {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/EnvironmentMetrics"},
    # ==============0514新增=============
    # "Fans":{"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans"},
    # "Drives": {"@odata.id": "/redfish/v1/Chassis/1/Drives"},
    "NetworkAdapters": {"@odata.id": "/redfish/v1/Chassis/1/NetworkAdapters"},
    # "PCIeDevices": {"@odata.id": "/redfish/v1/Chassis/1/PCIeDevices"},
    # "Power": {"@odata.id": "/redfish/v1/Chassis/1/Power"},
    # "Thermal": {"@odata.id": "/redfish/v1/Chassis/1/Thermal"},
    # "TrustedComponents": {"@odata.id": "/redfish/v1/Chassis/1/TrustedComponents"},

    # ==============0514新增=============
    
    # 感測器/控制集合
    "Sensors": {"@odata.id": "/redfish/v1/Chassis/1/Sensors"},
    "Controls": {"@odata.id": "/redfish/v1/Chassis/1/Controls"},
    

    # Links 關聯
    "Links": {
        "ManagedBy": [{"@odata.id": "/redfish/v1/Managers/CDU"}],
        "CoolingUnits": [{"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1"}],
        # "ComputerSystems": [{"@odata.id": "/redfish/v1/Systems/1"}], # 未確認
        # "CooledBy": [{}], # 未做
        # "PoweredBy": [{}], # 未做
    },
    "Actions": {},
    "@Redfish.WriteableProperties": [
        "LocationIndicatorActive",
    ],
    # OEM 擴充
    "Oem": {
        "supermicro": {
            "@odata.type": "#Oem.Chassis.v1_26_0.Chassis",
            "LeakDetection": {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection"},
            "Pumps": {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps"},
            "PrimaryCoolantConnectors": {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/PrimaryCoolantConnectors"},
            "Reservoirs": {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Reservoirs"},
            "Main MC": {
                "State":True
            }
        }
 
    },
}

Controls_data = {
    "@odata.id": "/redfish/v1/Chassis/1/Controls",
    "@odata.type": "#ControlCollection.ControlCollection",
    "@odata.context": "/redfish/v1/$metadata#ControlCollection.ControlCollection",
    "Name": "Control Collection",
    "Description": "Contains all control interfaces for issuing commands",
    "Members@odata.count": 3,
    "Members": [
        {"@odata.id": "/redfish/v1/Chassis/1/Controls/OperationMode"},
        {"@odata.id": "/redfish/v1/Chassis/1/Controls/PumpsSpeedControl"},
        {"@odata.id": "/redfish/v1/Chassis/1/Controls/FansSpeedControl"},
    ],
    "Oem": {
    }
}

Controls_data_all = {
    "OperationMode": {
        "@odata.id": "/redfish/v1/Chassis/1/Controls/OperationMode",
        "@odata.type": "#Control.v1_5_1.Control",
        "@odata.context": "/redfish/v1/$metadata#Control.v1_5_1.Control",
        "Id": "OperationMode",
        "Name": "Operation Mode",
        "PhysicalContext": "Chassis",
        "ControlMode": "Manual",
    },
    "PumpsSpeedControl": {
        "@odata.id": "/redfish/v1/Chassis/1/Controls/PumpsSpeedControl",
        "@odata.type": "#Control.v1_5_1.Control",
        "@odata.context": "/redfish/v1/$metadata#Control.v1_5_1.Control",
        "Id": "PumpsSpeedControl",
        "Name": "PumpsSpeed",
        "PhysicalContext": "Chassis",
        "ControlType": "Percent",
        "ControlMode": "Manual",
        "SetPoint": 35,
        "SetPointUnits": "%",
        "AllowableMax": 100,
        "AllowableMin": 25,
    },
        
    "FansSpeedControl": {
        "@odata.id": "/redfish/v1/Chassis/1/Controls/FansSpeedControl",
        "@odata.type": "#Control.v1_5_1.Control",
        "@odata.context": "/redfish/v1/$metadata#Control.v1_5_1.Control",
        "Id": "FansSpeedControl",
        "Name": "FansSpeed",
        "PhysicalContext": "Chassis",
        "ControlMode": "Manual",
        "SetPoint": 35,
        "SetPointUnits": "%",
        "AllowableMax": 100,
        "AllowableMin": 0, 
        # 0513新增
        "ControlType": "Percent",
    },
}

PowerSubsystem_data = {
    "@odata.id": "/redfish/v1/Chassis/1/PowerSubsystem",
    "@odata.type": "#PowerSubsystem.v1_1_3.PowerSubsystem",
    "@odata.context": "/redfish/v1/$metadata#PowerSubsystem.v1_1_3.PowerSubsystem",
    
    "Id": "PowerSubsystem",
    "Name": "Chassis Power Subsystem",
    "Description":   "Chassis Power Subsystem",
    
    # TBD
    "Status": {
        "State": "Enabled", 
        "Health": "OK"
    },
    
    # 整個子系統的額定最大功率
    # 一次工作一組 360w
    # 24v 240w 12v 120w
    "CapacityWatts": 360,
    
    # 本次與下游元件協商分配與請求的功率 TBD
    "Allocation": {
        "AllocatedWatts": 80.0,
        "RequestedWatts": 90.0
    },
    
    # "PowerSupplyRedundancy": [
    #     {
    #         "RedundancyType": "Failover",
    #         "MaxSupportedInGroup": 2,
    #         "MinNeededInGroup": 1,
    #         "RedundancyGroup": [
    #             {"@odata.id": "/redfish/v1/Chassis/1/PowerSubsystem/PowerSupplies/1"},
    #             {"@odata.id": "/redfish/v1/Chassis/1/PowerSubsystem/PowerSupplies/2"}
    #         ],
    #         # TBD
    #         "Status": {
    #             "State": "UnavailableOffline",
    #             "Health": "OK"
    #         }
    #     }
    # ],
    
    # 與各個電源模組的關聯
    "PowerSupplies": {
        "@odata.id": "/redfish/v1/Chassis/1/PowerSubsystem/PowerSupplies"
    },
    
    "Oem": {}
}


ThermalSubsystem_data = {
    "@odata.context": "/redfish/v1/$metadata#ThermalSubsystem.ThermalSubsystem",
    "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem",
    "@odata.type": "#ThermalSubsystem.v1_3_3.ThermalSubsystem",
    "Id": "ThermalSubsystem",
    "Name": "Thermal Subsystem",
    "Fans": {"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans"},
    "ThermalMetrics": {
        "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/ThermalMetrics"
    },
    # TBD 備用
    "FanRedundancy": [
        {
            "MaxSupportedInGroup": 2,
            "MinNeededInGroup": 1,
            "RedundancyGroup": [
                {
                    "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/1"
                },
            ],
            "RedundancyType": "NPlusM",
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "MaxSupportedInGroup": 2,
            "MinNeededInGroup": 1,
            "RedundancyGroup": [
                {
                    "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/1"
                },
                {
                    "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/2"
                }
            ],
            "RedundancyType": "NPlusM",
            "Status": {
                "State": "Disabled"
            }
        }
    ],
    # TBD
    "Status": {"State": "Enabled", "Health": "OK"},
    "Oem": {},
}

class MyBaseChassis(MyResource):
    def __init__(self, *args, **kwargs):
        self.chassis_count = 1
        self.power_supply_count = int(os.getenv("REDFISH_POWERSUPPLY_COLLECTION_CNT", 1))
        self.fan_count = int(os.getenv("REDFISH_FAN_COLLECTION_CNT", 1))
    
    def _validate_request(self):
        try:
            chassis_id = request.view_args.get("chassis_id")
            power_supply_id = request.view_args.get("power_supply_id")
            fan_id = request.view_args.get("fan_id")
            if not self._is_valid_id(chassis_id, self.chassis_count):
                abort(HTTPStatus.NOT_FOUND, description=f"chassis_id, {chassis_id}, not found")
            
            if not self._is_valid_id(power_supply_id, self.power_supply_count):
                abort(HTTPStatus.NOT_FOUND, description=f"power_supply_id, {power_supply_id}, not found")
            
            if not self._is_valid_id(fan_id, self.fan_count):
                abort(HTTPStatus.NOT_FOUND, description=f"fan_id, {fan_id}, not found")
        except Exception as e:
            abort(HTTPStatus.NOT_FOUND, description=f"[Unexpected Error] {e}")
    
    def _is_valid_id(self, id: str, max_value: int):
        if id: # request有傳id進來才檢查
            if not id.isdigit():
                return False
            if not (0 < int(id) <= max_value):
                return False
        return True
        

# def get_thermal_subsystem_fans_data():
#     fan_cnt = int(os.getenv("REDFISH_FAN_COLLECTION_CNT", 8))
#     base_path = "/redfish/v1/Chassis/1/ThermalSubsystem/Fans"

#     # 用 list comprehension 動態產生 Members 清單
#     members = [
#         {"@odata.id": f"{base_path}/{i}"}
#         for i in range(1, fan_cnt + 1)
#     ]

#     ThermalSubsystem_Fans_data = {
#         "@odata.context": "/redfish/v1/$metadata#Fans.FanCollection",
#         "@odata.id": base_path,
#         "@odata.type": "#FanCollection.FanCollection",
#         "Name": "Fans Collection",
#         "Members@odata.count": fan_cnt,
#         "Members": members
#     }

#     FAN_COUNT = int(os.getenv("REDFISH_FAN_COLLECTION_CNT", 8))

#     FAN_TEMPLATE = {
#         "@odata.type": "#Fan.v1_5_0.Fan",
#         "@odata.context": "/redfish/v1/$metadata#Fan.v1_5_0.Fan",
#         "PhysicalContext": "Chassis",
#         "PartNumber": "PN-FAN-100",
#         "SerialNumber": "SN12345678", 
#         "Manufacturer": "Supermicro",
#         "Model": "FAN-42",
#         "SparePartNumber": "SPN-FAN-100",
#         "Status": {"State": "Enabled", "Health": "OK"},
#         "Location": {
#             "PartLocation": {"LocationType": "Bay"}
#         },
#         "Oem": {}
#     }

#     Fans_data = {}
#     base_id = "/redfish/v1/Chassis/1/ThermalSubsystem/Fans"

#     for i in range(1, FAN_COUNT + 1):
#         # 複製範本
#         item = FAN_TEMPLATE.copy()

#         # 設定每支風扇特有欄位
#         item["@odata.id"] = f"{base_id}/{i}"
#         item["Id"] = str(i)
#         item["Name"] = f"Fan Right {i}"
#         item["Description"] = f"Fan Right {i}"
#         # 速度感測器連結
#         item["SpeedPercent"] = {
#             "DataSourceUri": f"/redfish/v1/Chassis/1/Sensors/Fan{i}",
#             # "@odata.id": f"/redfish/v1/Chassis/1/Sensors/Fan{i}",
#             "Reading": 0,
#             "SpeedRPM": 0
#         }
#         # 位置服務標籤
#         item["Location"]["PartLocation"]["ServiceLabel"] = f"Fan Bay {i}"

#         # 加入字典
#         Fans_data[f"Fan{i}"] = item
#     return Fans_data, ThermalSubsystem_Fans_data 




#================================================
# 共用資源
#================================================
def GetControlMode():
    mode = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/status/op_mode")["mode"]
    mapping = {
        "auto":     "Automatic",
        "manual":   "Manual",
        "stop":     "Disabled",
        "override": "Override"
    }
    ctrl = mapping.get(mode, Controls_data_all["OperationMode"]["ControlMode"])
    return ctrl
#================================================
# 機箱資源（Chassis）
#================================================
@Chassis_ns.route("/Chassis")
class Chassis(Resource):
    # # @requires_auth
    def get(self):
        return Chassis_data


@Chassis_ns.route("/Chassis/1")
class Chassis1(Resource):
    # # @requires_auth
    def get(self):
        version = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/display/version")
        version_data = version["fw_info"]
        Chassis_data_1["Model"] = version_data["Model"]
        Chassis_data_1["SerialNumber"] = version_data["SN"]
        Chassis_data_1["PartNumber"] = version_data["PartNumber"]
        Chassis_data_1["Version"] = version["version"]["Redfish_Server"]
        Chassis_data_1["UUID"] = get_mac_uuid()
        Chassis_data_1["Oem"]["supermicro"]["Main MC"]["State"] = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/mc")["main_mc"]
        return Chassis_data_1
#================================================
# 控制介面（Controls）
#================================================
# OperationMode patch設置
OperationMode_patch = Chassis_ns.model('OperationModePatch', {
    'mode': fields.String(
        required=True,
        description='Setting Mode',
        default='Manual',   # 這裡設定預設值
        example='Manual',   # 讓 UI 顯示範例
        enum=['Automatic', 'Manual', 'Disabled', 'Override']  # 如果有固定選項，也可以列出
    ),
})
# PumpSpeed patch設置
pumpspeed_patch_all = Chassis_ns.model('pumpspeed_patch_all', {
    'speed_set': fields.Integer(
        required=True,
        description='fan speed set',
        default='50',   # 這裡設定預設值
        example='50',   # 讓 UI 顯示範例
    ),
    'pump1_switch': fields.Boolean(
        required=True,
        description='pump switch',
        default=True,   # 這裡設定預設值
        example=True,   # 讓 UI 顯示範例
    ),    
    'pump2_switch': fields.Boolean(
        required=True,
        description='pump switch',
        default=True,   # 這裡設定預設值
        example=True,   # 讓 UI 顯示範例
    ),      
    'pump3_switch': fields.Boolean(
        required=True,
        description='pump switch',
        default=True,   # 這裡設定預設值
        example=True,   # 讓 UI 顯示範例
    ),    
})
# fanspeed patch設置
fanspeed_patch = Chassis_ns.model('FanSpeedControlPatch', {
    'fan_speed': fields.Integer(
        required=True,
        description='fan speed (0–100)',
        min=0, max=100
    ),
    'fan1_switch': fields.Boolean(
        required=True,
        description='fan switch',
        default=True,   # 這裡設定預設值
        example=True,   # 讓 UI 顯示範例
    ),
    'fan2_switch': fields.Boolean(
        required=True,
        description='fan switch',
        default=True,   # 這裡設定預設值
        example=True,   # 讓 UI 顯示範例
    ),
    'fan3_switch': fields.Boolean(
        required=True,
        description='fan switch',
        default=True,   # 這裡設定預設值
        example=True,   # 讓 UI 顯示範例
    ),
    'fan4_switch': fields.Boolean(
        required=True,
        description='fan switch',
        default=True,   # 這裡設定預設值
        example=True,   # 讓 UI 顯示範例
    ),
    'fan5_switch': fields.Boolean(
        required=True,
        description='fan switch',
        default=True,   # 這裡設定預設值
        example=True,   # 讓 UI 顯示範例
    ),
    'fan6_switch': fields.Boolean(
        required=True,
        description='fan switch',
        default=True,   # 這裡設定預設值
        example=True,   # 讓 UI 顯示範例
    ),
    # 'fan7_switch': fields.Boolean(
    #     required=True,
    #     description='fan switch',
    #     default=True,   # 這裡設定預設值
    #     example=True,   # 讓 UI 顯示範例
    # ),
    # 'fan8_switch': fields.Boolean(
    #     required=True,
    #     description='fan switch',
    #     default=True,   # 這裡設定預設值
    #     example=True,   # 讓 UI 顯示範例
    # ),    
})
# controls 資源
@Chassis_ns.route("/Chassis/<chassis_id>/Controls")
class Controls(Resource):
    # @requires_auth
    def get(self, chassis_id):
        return Controls_data

# operation mode 控制
@Chassis_ns.route("/Chassis/<chassis_id>/Controls/OperationMode")
class OperationMode(Resource):
    # # @requires_auth
    def get(self, chassis_id):
        Controls_data_all["OperationMode"]["ControlMode"] = GetControlMode()
        return Controls_data_all["OperationMode"], 200
    
    @Chassis_ns.expect(OperationMode_patch, validate=True)
    # @requires_auth
    def patch(self, chassis_id):
        global mode_all
        payload = request.get_json(force=True)
        new_mode  = payload["mode"]
        inv = {
            "Automatic": "auto",
            "Manual":    "manual",
            "Disabled":  "stop",
            "Override":  "override"
        }
        
        api_payload = inv[new_mode]
        print(api_payload)
        try:
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/status/op_mode",
                json={"mode": api_payload},  
                timeout=3
            )
            r.raise_for_status()
        except requests.HTTPError:
            # 如果 CDU 回了 4xx/5xx，直接把它的 status code 和 body 回來
            try:
                err_body = r.json()
            except ValueError:
                err_body = {"error": r.text}
            return err_body, r.status_code

        except requests.RequestException as e:
            # 純粹網路／timeout／連線失敗
            return {
                "error": "Forwarding to the CDU control service failed",
                "details": str(e)
            }, 502

        # 內部服務回傳 OK，更新 Redfish 內存資料
        Controls_data_all["OperationMode"]["ControlMode"] = new_mode

        # 回傳更新後的 Redfish Control 資源
        return Controls_data_all["OperationMode"], 200
    
# pump speed 控制
@Chassis_ns.route("/Chassis/<chassis_id>/Controls/PumpsSpeedControl")
class PumpsSpeedControl(Resource):
    # @requires_auth
    def get(self, chassis_id):
        
        pump_set_speed = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/control/pump_speed")
        Controls_data_all["PumpsSpeedControl"]["SetPoint"] = pump_set_speed["pump_speed"]
        Controls_data_all["PumpsSpeedControl"]["ControlMode"] = GetControlMode()
        # 回傳各 pump 速度
        # control_speed = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/control/pump_speed")
        # Controls_data_all["PumpsSpeedControl"]["oem"]["pump1_speed"] = control_speed["pump1_speed"]
        # Controls_data_all["PumpsSpeedControl"]["oem"]["pump2_speed"] = control_speed["pump2_speed"]
        # Controls_data_all["PumpsSpeedControl"]["oem"]["pump3_speed"] = control_speed["pump3_speed"]
        return Controls_data_all["PumpsSpeedControl"]
    
    # @requires_auth
    @Chassis_ns.expect(pumpspeed_patch_all, validate=True)
    def patch(self, chassis_id):
        body = request.get_json(force=True)
        
        Controls_data_all["PumpsSpeedControl"]["ControlMode"] = GetControlMode()
        # 驗證模式
        if Controls_data_all["PumpsSpeedControl"]["ControlMode"] != "Manual": 
            return {
                "error": {
                    "code": "Base.1.0.PropertyValueNotInSupportedRange",
                    "message": "Only Manual mode can be used for this operation.",
                }
            }, 400      

            
        
        new_sp = body['speed_set']
        new_sw1 = body['pump1_switch']
        new_sw2 = body['pump2_switch']
        new_sw3 = body['pump3_switch']
        
        # 驗證範圍
        scp = Controls_data_all["PumpsSpeedControl"]
        if not (scp["AllowableMin"] <= new_sp <= scp["AllowableMax"]):
            return {
                "error": f"pump_speed 必須介於 {scp['AllowableMin']} 和 {scp['AllowableMax']}"
            }, 400

        # 轉發到內部控制 API
        try:
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/control/pump1_speed",
                json={"pump_speed": new_sp, "pump_switch": new_sw1},
                timeout=3
            )
            r.raise_for_status()
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/control/pump2_speed",
                json={"pump_speed": new_sp, "pump_switch": new_sw2},
                timeout=3
            )
            r.raise_for_status()
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/control/pump3_speed",
                json={"pump_speed": new_sp, "pump_switch": new_sw3},
                timeout=3
            )
            r.raise_for_status()
        except requests.HTTPError:
            # 如果 CDU 回了 4xx/5xx，直接把它的 status code 和 body 回來
            try:
                err_body = r.json()
            except ValueError:
                err_body = {"error": r.text}
            return err_body, r.status_code

        except requests.RequestException as e:
            # 純粹網路／timeout／連線失敗
            return {
                "error": "Forwarding to the CDU control service failed",
                "details": str(e)
            }, 502

        # 更新內存資料
        scp["SetPoint"] = new_sp
        # pump_switch 控制 State
        # cdus_pumps_1["Status"]["State"] = "Enabled" if new_sw1 else "Disabled"
        # cdus_pumps_2["Status"]["State"] = "Enabled" if new_sw2 else "Disabled"
        # cdus_pumps_3["Status"]["State"] = "Enabled" if new_sw3 else "Disabled"

        # 回傳整個 Pump 資源
        return Controls_data_all["PumpsSpeedControl"], 200

# fanspeed 控制
@Chassis_ns.route("/Chassis/<chassis_id>/Controls/FansSpeedControl")
class FansSpeedControl(Resource):
    # @requires_auth
    def get(self, chassis_id):
        fan_control_speed = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/control/fan_speed")["fan_set"]
        Controls_data_all["FansSpeedControl"]["SetPoint"] = fan_control_speed
        Controls_data_all["FansSpeedControl"]["ControlMode"] = GetControlMode()
        print(fan_control_speed)
        return Controls_data_all["FansSpeedControl"], 200
    
    @Chassis_ns.expect(fanspeed_patch, validate=True)
    # @requires_auth
    def patch(self, chassis_id):
        payload = request.get_json(force=True)
        new_sp = payload["fan_speed"]
        fan1_switch = payload["fan1_switch"]
        fan2_switch = payload["fan2_switch"]
        fan3_switch = payload["fan3_switch"]
        fan4_switch = payload["fan4_switch"]
        fan5_switch = payload["fan5_switch"]
        fan6_switch = payload["fan6_switch"]
        # fan7_switch = payload["fan7_switch"]
        # fan8_switch = payload["fan8_switch"]

        Controls_data_all["FansSpeedControl"]["ControlMode"] = GetControlMode()
        # 驗證模式
        if Controls_data_all["FansSpeedControl"]["ControlMode"] != "Manual": 
            return {"error": "Only Manual mode can set fan speed"}, 405

        try:
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/control/fan_speed",
                json={"fan_speed": new_sp},  
                timeout=3
            )
            r.raise_for_status()
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/status/op_mode",
                json={  
                    "mode": "manual",
                    "fan1_switch": fan1_switch,
                    "fan2_switch": fan2_switch,
                    "fan3_switch": fan3_switch,
                    "fan4_switch": fan4_switch,
                    "fan5_switch": fan5_switch,
                    "fan6_switch": fan6_switch,
                    # "fan7_switch": fan7_switch,
                    # "fan8_switch": fan8_switch
                },  
                timeout=3
            )
            r.raise_for_status()

        except requests.HTTPError:
            # 如果 CDU 回了 4xx/5xx，直接把它的 status code 和 body 回來
            try:
                err_body = r.json()
            except ValueError:
                err_body = {"error": r.text}
            return err_body, r.status_code

        except requests.RequestException as e:
            # 純粹網路／timeout／連線失敗
            return {
                "error": "Forwarding to the CDU control service failed",
                "details": str(e)
            }, 502

        # 內部服務回傳 OK，更新 Redfish 內存資料
        Controls_data_all["FansSpeedControl"]["SetPoint"] = new_sp

        # 回傳更新後的 Redfish Control 資源
        return Controls_data_all["FansSpeedControl"], 200
#================================================
# 電源子系統（PowerSubsystem）
#================================================

@Chassis_ns.route("/Chassis/<chassis_id>/PowerSubsystem")
class PowerSubsystem(Resource):
    # @requires_auth
    def get(self, chassis_id):
        rep = PowerSubsystem_data
        status = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/chassis/summary")["power_total"]["status"]
        rep["Status"]["State"], rep["Status"]["Health"] = status["state"], status["health"]
        return rep


@Chassis_ns.route("/Chassis/<chassis_id>/PowerSubsystem/PowerSupplies")
class PowerSupplies(Resource):
    # @requires_auth
    def get(self, chassis_id):
        chassis_service = RfChassisService()
        rep = chassis_service.fetch_PowerSubsystem_PowerSupplies(chassis_id)
        return rep

@Chassis_ns.route("/Chassis/<chassis_id>/PowerSubsystem/PowerSupplies/<power_supply_id>")
class PowerSuppliesById(MyBaseChassis):
    # @requires_auth
    def get(self, chassis_id: str, power_supply_id: str):
        chassis_service = RfChassisService()
        # TBD
        rep = chassis_service.fetch_PowerSubsystem_PowerSupplies(chassis_id, power_supply_id)
        #  ['AC100To127V', 'AC100To240V', 'AC100To277V', 'AC120V', 'AC200To240V', 'AC200To277V', 'AC208V', 'AC230V', 'AC240V', 'AC240AndDC380V', 'AC277V', 'AC277AndDC380V', 'AC400V', 'AC480V', 'DC48V', 'DC240V', 'DC380V', 'DCNeg48V', 'DC16V', 'DC12V', 'DC9V', 'DC5V', 'DC3_3V', 'DC1_8V']
        rep["Metrics"] = {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{power_supply_id}/Metrics"}
        rep["Assembly"] = {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{power_supply_id}/Assembly"}
     
        return rep
    
@Chassis_ns.route("/Chassis/<chassis_id>/PowerSubsystem/PowerSupplies/<power_supply_id>/Assembly")
class Assembly(Resource):    
    # @requires_auth
    def get(self, chassis_id: str, power_supply_id: int):
        Assembly_data = {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{power_supply_id}/Assembly",
            "@odata.type": "#Assembly.v1_5_1.Assembly",
            
            "Id": str(power_supply_id),
            "Name": "Assembly",
        }
        return Assembly_data
#================================================
# 感測器（Sensors）
#================================================
@Chassis_ns.route("/Chassis/<chassis_id>/Sensors")
class Sensors(Resource):
    # @requires_auth
    def get(self, chassis_id):
        chassis_service = RfChassisService()
        return chassis_service.fetch_sensors_collection(chassis_id)


@Chassis_ns.route("/Chassis/<chassis_id>/Sensors/<sensor_id>")
class FetchSensorsById(Resource):
    # @requires_auth
    def get(self, chassis_id: str, sensor_id: str) -> Dict:
        """
        :param sensor_id: str, e.g. PrimaryFlowLitersPerMinute, CPUFan1, CPUFan2, ...
        :return: dict

        @see https://www.dmtf.org/sites/default/files/standards/documents/DSP2064_1.1.0.pdf Section 5.6.6, 5.13
        """
        chassis_service = RfChassisService()
        return chassis_service.fetch_sensors_by_name(chassis_id, sensor_id)
#================================================
# 散熱子系統（ThermalSubsystem）
#================================================
# OperationMode patch設置
FanSwitch_patch = Chassis_ns.model('FanSwitchpatch', {
    'fan_switch': fields.Boolean(
        required=True,
        description='Fan_Switch',
        default=True,   # 設定預設值
        example=True,   # 讓 UI 顯示範例
    ),
})

@Chassis_ns.route("/Chassis/1/ThermalSubsystem")
class ThermalSubsystem(Resource):
    # @requires_auth
    def get(self):
        return ThermalSubsystem_data


@Chassis_ns.route("/Chassis/<chassis_id>/ThermalSubsystem/Fans")
class ThermalSubsystem_Fans(Resource):
    # @requires_auth
    def get(self, chassis_id):
        ThermalSubsystem_Fans_data = RfChassisService()
        return ThermalSubsystem_Fans_data.get_thermal_subsystem_fans_count(chassis_id)


@Chassis_ns.route("/Chassis/<chassis_id>/ThermalSubsystem/Fans/<string:fan_id>")
class ThermalSubsystem_Fans_by_id(MyBaseChassis):
    # @requires_auth
    def get(self, fan_id, chassis_id):
        ThermalSubsystem_Fans_by_id = RfChassisService()
        rep = ThermalSubsystem_Fans_by_id.get_thermal_subsystem_fans_data(chassis_id, fan_id)
        # 要優化
        fan_mc_id = 1 if int(fan_id) <= 3 else 2
        rep["Oem"] = {
            "Supermicro": {
                "@odata.type": "#Supermicro.Fan.v1_5_2.Fan",
                f"Fan{fan_id} MC": {
                    "fan MC":load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/mc")[f"fan_mc{fan_mc_id}"]
                }
            }
            
        }
        return  rep, 200
    
    @Chassis_ns.expect(FanSwitch_patch, validate=True)
    def patch(self, chassis_id, fan_id):
        
        body = request.get_json(force=True)
        # 驗證模式
        if Controls_data_all["OperationMode"]["ControlMode"] != "Manual": return "only Manual can setting"
        fan_switch = body["fan_switch"]

        # 轉發到內部控制 API
        try:
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/status/op_mode",
                json={"mode": "manual", f"fan{fan_id}_switch": fan_switch },
                timeout=3
            )
            r.raise_for_status()

        except requests.HTTPError:
            # 如果 CDU 回了 4xx/5xx，直接把它的 status code 和 body 回來
            try:
                err_body = r.json()
            except ValueError:
                err_body = {"error": r.text}
            return err_body, r.status_code

        except requests.RequestException as e:
            # 純粹網路／timeout／連線失敗
            return {
                "error": "Forwarding to the CDU control service failed",
                "details": str(e)
            }, 502
        
        # 內部儲存
        state = "Enabled" if fan_switch else "Disabled"
        # Sensors_data_all[f"Fan{fan_id}"]["ControlMode"] = state
        ThermalSubsystem_Fans_by_id = RfChassisService()
        
        return ThermalSubsystem_Fans_by_id.get_thermal_subsystem_fans_data(chassis_id, fan_id), 200
    
@Chassis_ns.route("/Chassis/<chassis_id>/ThermalSubsystem/ThermalMetrics")
class ThermalMetrics(Resource):
    # @requires_auth
    def get(self, chassis_id):
        ThermalMetrics_data = {
            "@odata.context": "/redfish/v1/$metadata#ThermalMetrics.ThermalMetrics",
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem/ThermalMetrics",
            "@odata.type": "#ThermalMetrics.v1_3_2.ThermalMetrics",
            
            "Id": "ThermalMetrics",
            "Name": "Chassis Thermal Metrics",
            
            "TemperatureReadingsCelsius": [
                {
                    "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/IntakeTemp",
                    "DeviceName": "Intake",
                    "Reading": 24.8
                },
                {
                    "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/ExhaustTemp",
                    "DeviceName": "Exhaust",
                    "Reading": 40.5
                }
            ],
            "TemperatureSummaryCelsius": {
                "Ambient": {
                    "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/AmbientTemp",
                    "Reading": 22.5
                },
                "Exhaust": {
                    "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/ExhaustTemp",
                    "Reading": 40.5
                },
                "Intake": {
                    "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/IntakeTemp",
                    "Reading": 24.8
                },
                "Internal": {
                    "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/CPU1Temp",
                    "Reading": 39
                }
            }
        }
        return ThermalMetrics_data    
    
# ===============================0514新增(以下 TBD)===============================================
# 儲存驅動集合(硬碟、健康、製造商...)
# Drives_data = {
#     "@odata.context": "/redfish/v1/$metadata#DriveCollection.DriveCollection",
#     "@odata.id":      "/redfish/v1/Chassis/1/Drives",
#     "@odata.type":    "#DriveCollection.DriveCollection",
#     "Name":           "Drive Collection",
#     "Members@odata.count": 1,
#     "Members": [
#         { "@odata.id": "/redfish/v1/Chassis/1/Drives/1" }
#     ],
#     "Oem": {}
# }
# 網路集合(數據接口...)
NetworkAdapters_data = {
    "@odata.id": "/redfish/v1/Chassis/1/NetworkAdapters",
    "@odata.type": "#NetworkAdapterCollection.NetworkAdapterCollection",
    
    "Name": "Network Adapter Collection",
    "Description": "Collection of Network Adapters for this Chassis",
    
    "Members@odata.count": 1,
    "Members": [
        { "@odata.id": "/redfish/v1/Chassis/1/NetworkAdapters/1" }
    ],
    "Oem": {}
}
# PCIed擴展集合
# PCIeDevices_data = {
#     "@odata.id": "/redfish/v1/Chassis/1/PCIeDevices",
#     "@odata.type": "#PCIeDeviceCollection.PCIeDeviceCollection",
    
#     "Name": "PCIe Device Collection",
#     "Description": "Collection of PCIe Devices for this Chassis",
    
#     "Members@odata.count": 1,
#     "Members": [
#         { "@odata.id": "/redfish/v1/Chassis/1/PCIeDevices/1" }
#     ],
#     "Oem": {}
# }
# # 電源子系統(PSU狀態、輸入電壓、功率...)
# Power_data = {
#     "@odata.id": "/redfish/v1/Chassis/1/Power",
#     "@odata.type": "#Power.v1_7_3.Power",
    
#     "Id": "Power",
#     "Name": "Power Collection",
#     "Description": "Collection of Power for this Chassis",
    
#     "PowerControl": [
#         {
#             "@odata.id": "/redfish/v1/Chassis/1/Power/PowerControl/1",
#             "@odata.context": "/redfish/v1/$metadata#Power.PowerControl",
#             "@odata.type": "#Power.v1_7_2.PowerControl",
#             "MemberId": "1",
#             "Name": "System Input Power",
            
#             "PowerConsumedWatts": 344,
#             "PowerCapacityWatts": 800,
            
#             "PowerMetrics": {
#                 "IntervalInMin": 30,
#                 "MinConsumedWatts": 271,
#                 "MaxConsumedWatts": 489,
#                 "AverageConsumedWatts": 319
#             },
#         }
#     ],
    
#     "PowerSupplies": [
#         {
#             "@odata.id": "/redfish/v1/Chassis/1/Power/PowerSupplies/0",
#             "FirmwareVersion": "1.00",
#             "InputRanges": [
#                 {
#                     "InputType": "AC",
#                     "MaximumVoltage": 120,
#                     "MinimumVoltage": 100,
#                     "OutputWattage": 800
#                 },
#                 {
#                     "InputType": "AC",
#                     "MaximumVoltage": 240,
#                     "MinimumVoltage": 200,
#                     "OutputWattage": 1300
#                 }
#             ],
#             "LastPowerOutputWatts": 325,
#             "LineInputVoltage": 120,
#             "LineInputVoltageType": "AC240V",
#             "Manufacturer": "ManufacturerName",
#             "MemberId": "0",
#             "Model": "499253-B21",
#             "Name": "Power Supply Bay",
#             "PartNumber": "0000001A3A",
#             "PowerCapacityWatts": 800,
#             "PowerSupplyType": "AC",
#             "RelatedItem": [
#                 {
#                     "@odata.id": "/redfish/v1/Chassis/1/Power/PowerSupplies/0/RelatedItem/0",
#                 }
#             ],
#             "SerialNumber": "1Z0000001",
#             "SparePartNumber": "0000001A3A",
#             "Status": {
#                 "Health": "Warning",
#                 "State": "Enabled"
#             },
#             "PowerInputWatts": 325,
#             "PowerOutputWatts": 325,
#             "Redundancy": [{"@odata.id": "/redfish/v1/Chassis/1/Redundancy"}],
#         },
#         {
#             "@odata.id": "/redfish/v1/Chassis/1/Power/PowerSupplies/1",
#             "FirmwareVersion": "1.00",
#             "InputRanges": [
#                 {
#                     "InputType": "AC",
#                     "MaximumVoltage": 120,
#                     "MinimumVoltage": 100,
#                     "OutputWattage": 800
#                 },
#                 {
#                     "InputType": "AC",
#                     "MaximumVoltage": 240,
#                     "MinimumVoltage": 200,
#                     "OutputWattage": 1300
#                 }
#             ],
#             "LastPowerOutputWatts": 325,
#             "LineInputVoltage": 120,
#             "LineInputVoltageType": "AC240V",
#             "Manufacturer": "ManufacturerName",
#             "MemberId": "0",
#             "Model": "499253-B21",
#             "Name": "Power Supply Bay",
#             "PartNumber": "0000001A3A",
#             "PowerCapacityWatts": 800,
#             "PowerSupplyType": "AC",
#             "RelatedItem": [
#                 {
#                     "@odata.id": "/redfish/v1/Chassis/1",
#                 }
#             ],
#             "SerialNumber": "1Z0000001",
#             "SparePartNumber": "0000001A3A",
#             "Status": {
#                 "Health": "Warning",
#                 "State": "Enabled"
#             },
#             "PowerInputWatts": 325,
#             "PowerOutputWatts": 325,
#             "Redundancy": [{"@odata.id": "/redfish/v1/Chassis/1/Power/PowerSupplies/1/Redundancy"}],
#         },
#     ],
#     "Redundancy": [
#         {
#             "@odata.id": "/redfish/v1/Chassis/1/Power/Redundancy",
#             "Name": "Redundancy",
#             "Mode": "RedundancySet",
#             "MinNumNeeded": 1,
#             "RedundancySet": [{"@odata.id": "/redfish/v1/Chassis/1/Power/PowerSupplies/0"}],
#             "MemberId": "0"
#         }
#     ],
    
#     "Oem": {}    
# }
# # 熱管理子系統(溫度讀取、風扇配置...)
# Thermal_data = {
#     "@odata.id": "/redfish/v1/Chassis/1/Thermal",
#     "@odata.type": "#Thermal.v1_7_3.Thermal",

#     "Id": "Thermal",   
#     "Name": "Thermal Collection",
#     "Description": "Collection of Thermal for this Chassis",
    
#     "Fans": [
#         {
#             "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans",
#             "Name": "Fans",
#             "PhysicalContext": "Chassis",
#             "Reading": 1000,
#             "ReadingUnits": "RPM",
#             "Status": {
#                 "Health": "OK",
#                 "State": "Enabled"
#             }
#         }
#     ],
#     "Temperatures": [
#         {
#             "@odata.id": "/redfish/v1/Chassis/1/Thermal/Temperatures",
#             "MemberId": "0",
#             "Name": "Temperatures",
#             "PhysicalContext": "Chassis",
#             "ReadingCelsius": 1000,
#             "Status": {
#                 "Health": "OK",
#                 "State": "Enabled"
#             }
#         },
#     ],
#     "Oem": {}    
# }
# # 可信集合(TPM、硬體信任...)
# TrustedComponents_data = {
#     "@odata.id": "/redfish/v1/Chassis/1/TrustedComponents",
#     "@odata.type": "#TrustedComponentCollection.TrustedComponentCollection",
    
#     "Name": "Trusted Components Collection",
#     "Description": "Collection of Trusted Components for this Chassis",
    
#     "Members@odata.count": 1,
#     "Members": [
#         { "@odata.id": "/redfish/v1/Chassis/1/TrustedComponents/1" }
#         ],
#     "Oem": {}
# }


# ================
# Drvives
# ================
# @Chassis_ns.route("/Chassis/<chassis_id>/Drives")
# class Drives(Resource):
#     # @requires_auth
#     def get(self, chassis_id):
#         return Drives_data
    
# @Chassis_ns.route("/Chassis/<string:chassis_id>/Drives/<string:drive_id>")
# class Drive(Resource):
#     def get(self, chassis_id, drive_id):
#         return {
#             "@odata.context": "/redfish/v1/$metadata#Drive.v1_21_0.Drive",
#             "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Drives/{drive_id}",
#             "@odata.type": "#Drive.v1_21_0.Drive",
            
#             "Id": drive_id,
#             "Name": f"Drive {drive_id}",
            
#             "BlockSizeBytes": 512,
#             "CapacityBytes": 1000000000000,
#             "Status": {"State": "Enabled", "Health": "OK"},
            
#             "Manufacturer": "Supermicro",
#             "MediaType": "HDD",
#             "Model": "TBD",
#             "PhysicalLocation": {},
#             "LocationIndicatorActive": True,
#             "Protocol": "SAS",
#             "Revision": "TBD",
#             "SerialNumber": "TBD",
            
            
#         }    
    
# ================
# NetworkAdapters
# ================    

@Chassis_ns.route("/Chassis/<chassis_id>/NetworkAdapters") 
class NetworkAdapters(Resource):
    # @requires_auth
    def get(self, chassis_id):
        return NetworkAdapters_data

@Chassis_ns.route("/Chassis/<chassis_id>/NetworkAdapters/<string:NetworkAdapter_id>") 
class NetworkAdapters(Resource):
    # @requires_auth
    def get(self, chassis_id, NetworkAdapter_id):
        return {
            "@odata.context": "/redfish/v1/$metadata#NetworkAdapter.NetworkAdapter",
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/NetworkAdapters/{NetworkAdapter_id}",
            "@odata.type": "#NetworkAdapter.v1_11_0.NetworkAdapter",
            "Id": NetworkAdapter_id,
            "Name": f"NetworkAdapter {NetworkAdapter_id}",
            
            "PartNumber": "Transcend-TS2TMTS970T-I",
            "SerialNumber": "MAC",
            "Ports": {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/NetworkAdapters/{NetworkAdapter_id}/Ports"}
        }    
        
@Chassis_ns.route("/Chassis/<chassis_id>/NetworkAdapters/<string:NetworkAdapter_id>/Ports") 
class NetworkAdapters(Resource):
    # @requires_auth
    def get(self, chassis_id, NetworkAdapter_id):
        Port_data = {
            "@odata.context": "/redfish/v1/$metadata#PortCollection.PortCollection",
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/NetworkAdapters/{NetworkAdapter_id}/Ports",
            "@odata.type": "#PortCollection.PortCollection",
            
            "Name": "Port Collection",
            
            "Members@odata.count": 1,
            "Members": [
                { "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/NetworkAdapters/{NetworkAdapter_id}/Ports/1" }
            ]
        }
        return Port_data
    
@Chassis_ns.route("/Chassis/<chassis_id>/NetworkAdapters/<string:NetworkAdapter_id>/Ports/<string:Port_id>") 
class NetworkAdapters(Resource):
    # @requires_auth
    def get(self, chassis_id, NetworkAdapter_id, Port_id):
        NetworkAdapter_id_Port_id = {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/NetworkAdapters/{NetworkAdapter_id}/Ports/{Port_id}",
            "@odata.type": "#Port.v1_16_0.Port",
            "@odata.context": "/redfish/v1/$metadata#Port.Port",
            
            "Id": Port_id,
            "Name": f"Port {Port_id}",
            
            "MaxSpeedGbps": 10,
            "CurrentSpeedGbps": 10,
            "Ethernet": {
                "LLDPEnabled": True,
                "LLDPReceive": {
                    "ChassisId": "TBD", # 放MAC
                    "ChassisIdSubtype": "ChassisComp",
                    "ManagementAddressIPv4": "192.168.1.100",
                    "ManagementAddressMAC": "00:11:22:33:44:55",
                    "ManagementVlanId": 0,
                    "PortId": "01", # 單一組:01 多組:01:0A:FF:10
                    "PortIdSubtype": "ChassisComp",
                    "SystemDescription": "TBD",
                    "SystemName": "TBD"
                }
            },
            "LinkState": "Enabled",
            "LinkStatus": "LinkUp",
            "Width": 1,
            "Status": {"State": "Enabled", "Health": "OK"},
        }
        return NetworkAdapter_id_Port_id
            
# ================
# PCIeDevices
# ================    
# @Chassis_ns.route("/Chassis/<chassis_id>/PCIeDevices")
# class PCIeDevices(Resource):
#     # @requires_auth
#     def get(self, chassis_id):
#         return PCIeDevices_data 
    
# @Chassis_ns.route("/Chassis/<chassis_id>/PCIeDevices/<string:PCIeDevices_id>") 
# class PCIeDevices(Resource):
#     # @requires_auth
#     def get(self, chassis_id, PCIeDevices_id):
#         return {
#             "@odata.context": "/redfish/v1/$metadata#PCIeDevices.v1_18_0.PCIeDevices",
#             "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PCIeDevices/{PCIeDevices_id}",
#             "@odata.type": "#PCIeDevice.v1_18_0.PCIeDevice",
#             "Id": PCIeDevices_id,
#             "Name": f"PCIeDevices {PCIeDevices_id}",
            
#             "DeviceType": "SingleFunction",
#             "FirmwareVersion": "1",
#             "Manufacturer": "Supermicro",
#             "Model": "TBD",
#             "PartNumber": "TBD",
#             "SerialNumber": "TBD",
#             "Slot": None,
#             "Status": {"State": "Enabled", "Health": "OK"},
            
#             "PCIeFunctions": {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PCIeDevices/{PCIeDevices_id}/PCIeFunctions"}
#         }       
 
# @Chassis_ns.route("/Chassis/<string:chassis_id>/PCIeDevices/<string:device_id>/PCIeFunctions")
# class PCIeFunctionCollection(Resource):
#     def get(self, chassis_id, device_id):
#         # 假设只有一个功能 ID = "1"
#         members = [
#             {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PCIeDevices/{device_id}/PCIeFunctions/1"}
#         ]
#         return {
#             "@odata.context": "/redfish/v1/$metadata#PCIeFunctionCollection.PCIeFunctionCollection",
#             "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PCIeDevices/{device_id}/PCIeFunctions",
#             "@odata.type": "#PCIeFunctionCollection.PCIeFunctionCollection",
#             "Name": "PCIe Function Collection",
#             "Members@odata.count": len(members),
#             "Members": members,
#             "Oem": {}
#         }       

# @Chassis_ns.route("/Chassis/<string:chassis_id>/PCIeDevices/<string:device_id>/PCIeFunctions/<string:function_id>")
# class PCIeFunction(Resource):
#     def get(self, chassis_id, device_id, function_id):
#         return {
#             "@odata.context": "/redfish/v1/$metadata#PCIeFunction.v1_6_0.PCIeFunction",
#             "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PCIeDevices/{device_id}/PCIeFunctions/{function_id}",
#             "@odata.type": "#PCIeFunction.v1_6_0.PCIeFunction",
            
#             "Id": str(function_id),
#             "Name": f"PCIe Function {function_id}",
#             "FunctionId": int(function_id),
            
#             # 要用十六進位
#             "DeviceClass": "UnclassifiedDevice",
#             "DeviceId": "0x1B64",
#             "SubsystemId": "0x0000",
#             "SubsystemVendorId": "0x15D9",
#             "VendorId": "0x15D9",

#             "Oem": {}
#         }
# ================
# Power
# ================ 
# @Chassis_ns.route("/Chassis/<chassis_id>/Power")
# class Power(Resource):
#     # @requires_auth
#     def get(self, chassis_id):
#         return Power_data    


# @Chassis_ns.route("/Chassis/<chassis_id>/Power/PowerSupplies/<power_supply_id>")
# class PowerSuppliesById(Resource):
#     def abort_if_uri_not_exist(self, power_supply_id: int):
#         if not (1 <= power_supply_id <= int(os.getenv("REDFISH_POWERSUPPLY_COLLECTION_CNT", 1))):
#             abort(HTTPStatus.NOT_FOUND, description=f"Power supply id, {power_supply_id}, not found")
    
#     # @requires_auth
#     def get(self, chassis_id: str, power_supply_id: str):
#         self.abort_if_uri_not_exist(int(power_supply_id))
#         chassis_service = RfChassisService()
#         # TBD
#         rep = chassis_service.fetch_PowerSubsystem_PowerSupplies(chassis_id, power_supply_id)
#         rep["Metrics"] = {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{power_supply_id}/Metrics"}
#         rep["Assembly"] = {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{power_supply_id}/Assembly"}
     
#         return rep


 
@Chassis_ns.route("/Chassis/<chassis_id>/PowerSubsystem/PowerSupplies/<string:power_supply_id>/Metrics")
class PowerSuppliesMetrics(MyBaseChassis):
    # @requires_auth
    def get(self, chassis_id, power_supply_id):
        power_Metrics_data = {
            "@odata.context": "/redfish/v1/$metadata#PowerSupplyMetrics.PowerSupplyMetrics",
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{power_supply_id}/Metrics",
            "@odata.type": "#PowerSupplyMetrics.v1_1_2.PowerSupplyMetrics",
            
            "Id": f"PowerSupplyMetrics{power_supply_id}",
            "Name": "Chassis Power Supply Metrics",
            
            # "FrequencyHz":{"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/FrequencyHz"},
            # "InputCurrentAmps":{"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/InputCurrentAmps"},
            # "InputPowerWatts":{"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/InputPowerWatts"},
            # "InputVoltage":{"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/InputVoltage"},
            # "OutputPowerWatts":{"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/OutputPowerWatts"},
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            },
            # 這裡最少要有一個 Reading 欄位
            # "ReadingWatts": 480.0
}
        return power_Metrics_data        

# ================
# Thermal
# ================ 
# Thermal_sub = "/Chassis/<chassis_id>/Thermal"
# @Chassis_ns.route("/Chassis/<chassis_id>/Thermal")    
# class Thermal(Resource):
#     # @requires_auth
#     def get(self, chassis_id):
#         return Thermal_data

# @Chassis_ns.route("/Chassis/<string:chassis_id>/ThermalSubsystem/ThermalMetrics")
# class ThermalMetrics(Resource):
#     # @requires_auth
#     def get(self, chassis_id):
#         ThermalMetrics_data = {
#             "@odata.context": "/redfish/v1/$metadata#ThermalMetrics.ThermalMetrics",
#             "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem/ThermalMetrics",
#             "@odata.type": "#ThermalMetrics.v1_3_2.ThermalMetrics",
#             "Id": f"ThermalMetrics{chassis_id}",
#             "Name": "Chassis Thermal Metrics",
#             # "Status": {
#             #     "State": "Enabled",
#             #     "Health": "OK"
#             # },
#         }
#         return ThermalMetrics_data

# @Chassis_ns.route("/Chassis/<chassis_id>/Thermal/Temperatures")
# class Temperatures(Resource):
#     # @requires_auth
#     def get(self, chassis_id):
#         Temperatures_data = {
#             "@odata.context": "/redfish/v1/$metadata#TemperatureCollection.TemperatureCollection",
#             "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Thermal/Temperatures",
#             "@odata.type": "#TemperatureCollection.TemperatureCollection",
#             "Name": "Chassis Temperatures",
#         }
#         return Temperatures_data
# ================
# TrustedComponents
# ================ 
# @Chassis_ns.route("/Chassis/<chassis_id>/TrustedComponents")
# class TrustedComponents(Resource):
#     # @requires_auth
#     def get(self, chassis_id):
#         return TrustedComponents_data 
    

# @Chassis_ns.route("/Chassis/<chassis_id>/TrustedComponents/<string:TrustedComponents_id>")
# class TrustedComponents(Resource):
#     # @requires_auth
#     def get(self, chassis_id, TrustedComponents_id):
#         TrustedComponents_component_data = {
#             "@odata.context": "/redfish/v1/$metadata#TrustedComponent.TrustedComponent",
#             "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/TrustedComponents/{TrustedComponents_id}",
#             "@odata.type": "#TrustedComponent.v1_3_2.TrustedComponent",
            
#             "Id": str(TrustedComponents_id),
#             "Name": "Chassis Trusted Components",
            
#             "Certificates": {"@odata.id": f"/redfish/v1/CertificateService/Certificates"},
#             "FirmwareVersion": "1.0.0",
#             "Manufacturer": "supermicro",
#             "Model": "Chassis",
#             "PartNumber": "TBD",
#             "SerialNumber": "TBD",
#             "Status": {
#                 "State": "Enabled",
#                 "Health": "OK"
#             },
#             "TrustedComponentType": "Discrete",
#         }
#         return TrustedComponents_component_data         