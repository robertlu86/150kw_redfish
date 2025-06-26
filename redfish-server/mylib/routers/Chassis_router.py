from flask import request, jsonify
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
from mylib.utils.system_info import get_system_uuid


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
    "ChassisType": "Sidecar",
    "Manufacturer": "Supermicro",
    "Model": "CDU 150kW",
    "SerialNumber": "130001",
    "PartNumber": "LCS-SCDU-1K3LR001",
    "UUID": "00000000-0000-0000-0000-e45f013e98f8", # 機殼 UUID (未做)
    "AssetTag": "130001",
    "SKU": "130-D0150000A0-T01",
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
    # "NetworkAdapters": {"@odata.id": "/redfish/v1/Chassis/1/NetworkAdapters"},
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
            # "Reservoirs": {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Reservoirs"},
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
    "Members@odata.count": 0,
    "Members": [
        # {"@odata.id": "/redfish/v1/Chassis/1/Controls/OperationMode"},
        # {"@odata.id": "/redfish/v1/Chassis/1/Controls/PumpsSpeedControl"},
        # {"@odata.id": "/redfish/v1/Chassis/1/Controls/FansSpeedControl"},
    ],
    "Oem": {
        "Supermicro": {
            "@odata.id": "/redfish/v1/Chassis/1/Controls/Oem/Supermicro/Operation",
            "@odata.type": "#Supermicro.Control",
            "ControlMode":"N/A", # Disable / Automatic / Manual
            "TargetTemperature": -1,
            "TargetPressure": -1,
            "PumpSwapTime": -1,
            "FanSetPoint": -1,
            "PumpSetPoint": -1,
            "Pump1Switch": False,
            "Pump2Switch": False,
            "Pump3Switch": False,
        }
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
    "Status": {"State": "Enabled", "Health": "OK"},
    "Oem": {},
}

class MyBaseChassis(MyResource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

def ControlMode_change(new_mode):
    mapping = {
        "Automatic" : "auto",     
        "Manual"    : "manual",   
        "Disabled"  : "stop", 
        "Override"  : "override" 
    }
    return mapping.get(new_mode)
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
        Chassis_data_1["AssetTag"] = version_data["SN"]
        Chassis_data_1["UUID"] = get_system_uuid()
        Chassis_data_1["Oem"]["supermicro"]["Main MC"]["State"] = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/mc")["main_mc"]
        return Chassis_data_1
#================================================
# 控制介面（Controls）
#================================================
# controls 資源
@Chassis_ns.route("/Chassis/<chassis_id>/Controls")
class Controls(MyBaseChassis):
    # @requires_auth
    def get(self, chassis_id):
        
        # return Controls_data
        return RfChassisService().get_control(chassis_id)

#================================================
# 電源子系統（PowerSubsystem）
#================================================

@Chassis_ns.route("/Chassis/<chassis_id>/PowerSubsystem")
class PowerSubsystem(MyBaseChassis):
    # @requires_auth
    def get(self, chassis_id):
        rep = PowerSubsystem_data
        status = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/chassis/summary")["power_total"]["status"]
        rep["Status"]["State"], rep["Status"]["Health"] = status["state"], status["health"]
        return rep


@Chassis_ns.route("/Chassis/<chassis_id>/PowerSubsystem/PowerSupplies")
class PowerSupplies(MyBaseChassis):
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
class Assembly(MyBaseChassis):    
    # @requires_auth
    def get(self, chassis_id: str, power_supply_id: int):
        Assembly_data = {
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{power_supply_id}/Assembly",
            "@odata.type": "#Assembly.v1_5_1.Assembly",
            
            "Id": str(power_supply_id),
            "Name": "Assembly",
        }
        return Assembly_data
    
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
#================================================
# 感測器（Sensors）
#================================================
@Chassis_ns.route("/Chassis/<chassis_id>/Sensors")
class Sensors(MyBaseChassis):
    # @requires_auth
    def get(self, chassis_id):
        chassis_service = RfChassisService()
        return chassis_service.fetch_sensors_collection(chassis_id)


@Chassis_ns.route("/Chassis/<chassis_id>/Sensors/<sensor_id>")
class FetchSensorsById(MyBaseChassis):
    # @requires_auth
    def get(self, chassis_id: str, sensor_id: str) -> Dict:
        """
        :param sensor_id: str, e.g. PrimaryFlowLitersPerMinute, CPUFan1, CPUFan2, ...
        :return: dict

        @see https://www.dmtf.org/sites/default/files/standards/documents/DSP2064_1.1.0.pdf Section 5.6.6, 5.13
        """
        chassis_service = RfChassisService()
        rep = chassis_service.fetch_sensors_by_name(chassis_id, sensor_id)

        return jsonify(rep)
#================================================
# 散熱子系統（ThermalSubsystem）
#================================================
# OperationMode patch model設置
FanSwitch_patch = Chassis_ns.model('FanSwitchpatch', {
    'SetPoint': fields.Integer(
        required=True,
        description='Fan_Speed',
        default=True,   # 是否設定預設值
        example=50,   # 讓 UI 顯示範例
    ),
    'ControlMode': fields.String(
        required=True,
        description='Switch_Mode',
        default=True,   # 是否設定預設值
        example="Manual",   # 讓 UI 顯示範例
        enum=['Automatic', 'Manual', 'Disabled']
    ),
})

Fan_model = Chassis_ns.model('FanModel', {
    'SpeedControlPercent': fields.Nested(FanSwitch_patch, description='Fan settings')
})

@Chassis_ns.route("/Chassis/1/ThermalSubsystem")
class ThermalSubsystem(MyBaseChassis):
    # @requires_auth
    def get(self):
        return ThermalSubsystem_data


@Chassis_ns.route("/Chassis/<chassis_id>/ThermalSubsystem/Fans")
class ThermalSubsystem_Fans(MyBaseChassis):
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

        return  rep, 200
    
    @Chassis_ns.expect(Fan_model, validate=True)
    def patch(self, chassis_id, fan_id):
        body = request.get_json(force=True)
        
        return RfChassisService().patch_thermal_subsystem_fans_data(chassis_id, fan_id, body)
    
@Chassis_ns.route("/Chassis/<chassis_id>/ThermalSubsystem/ThermalMetrics")
class ThermalMetrics(MyBaseChassis):
    # @requires_auth
    def get(self, chassis_id):
        ThermalMetrics_data = {
            "@odata.context": "/redfish/v1/$metadata#ThermalMetrics.ThermalMetrics",
            "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem/ThermalMetrics",
            "@odata.type": "#ThermalMetrics.v1_3_2.ThermalMetrics",
            
            "Id": "ThermalMetrics",
            "Name": "Chassis Thermal Metrics",
            
            "TemperatureSummaryCelsius": {
                "Ambient": {
                    "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/TemperatureCelsius",
                },
                "Exhaust": {
                    "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/PrimarySupplyTemperatureCelsius",
                },
                "Intake": {
                    "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/PrimaryReturnTemperatureCelsius",
                },
            }
        }
        return ThermalMetrics_data    
    
#================================================
# Supermicro OEM Operation 資源
#================================================
# Operation patch model設置  
Operation_patch = Chassis_ns.model('Operation', {
    'ControlMode': fields.String(
        required=True,
        description='Switch_Mode',
        default=True,   # 是否設定預設值
        example="Manual",   # 讓 UI 顯示範例
        enum=['Automatic', 'Manual', 'Disabled']
    ),
    'TargetTemperature': fields.Float(
        # required=True,
        description='Target_Temperature',
        default=True,   # 是否設定預設值
        example=50,   # 讓 UI 顯示範例
    ),
    'TargetPressure': fields.Float(
        # required=True,
        description='Target_Pressure',
        default=True,   # 是否設定預設值
        example=10,   # 讓 UI 顯示範例
    ),
    'PumpSwapTime': fields.Integer(
        # required=True,
        description='Pump_Swap_Time',
        default=True,   # 是否設定預設值
        example=100,   # 讓 UI 顯示範例
    ),
    'FanSetPoint': fields.Float(
        # required=True,
        description='Fan_Set_Point',
        default=True,   # 是否設定預設值
        example=50,   # 讓 UI 顯示範例
    ),
    'PumpSetPoint': fields.Float(
        # required=True,
        description='Pump_Set_Point',
        default=True,   # 是否設定預設值
        example=50,   # 讓 UI 顯示範例
    ),
    'Pump1Switch': fields.Boolean(
        # required=True,
        description='Pump1_Switch',
        default=True,   # 是否設定預設值
        example=True,   # 讓 UI 顯示範例
    ),
    'Pump2Switch': fields.Boolean(
        # required=True,
        description='Pump2_Switch',
        default=True,   # 是否設定預設值
        example=True,   # 讓 UI 顯示範例
    ),
    'Pump3Switch': fields.Boolean(
        # required=True,
        description='Pump3_Switch',
        default=True,   # 是否設定預設值
        example=True,   # 讓 UI 顯示範例
    )

})   

@Chassis_ns.route("/Chassis/<chassis_id>/Controls/Oem/Supermicro/Operation")
class Operation(MyBaseChassis):
    # @requires_auth
    def get(self, chassis_id):
        return RfChassisService().get_Oem_Spuermicro_Operation(chassis_id)
    
    @Chassis_ns.expect(Operation_patch, validate=True)
    def patch(self, chassis_id):
        body = request.get_json(force=True)
        
        return RfChassisService().patch_Oem_Spuermicro_Operation(chassis_id, body)
    
