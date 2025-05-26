from flask import request
from flask_restx import Namespace, Resource, fields
from mylib.models.rf_environment_metrics_model import RfEnvironmentMetricsModel
from mylib.services.rf_ThermalEquipment_service import RfThermalEquipmentService
from mylib.utils.load_api import load_raw_from_api 
from mylib.utils.load_api import CDU_BASE
from mylib.routers.Chassis_router import Controls_data_all
import requests

ThermalEquipment_ns = Namespace('', description='ThermalEquipment Collection')

ThermalEquipment_data= {
    "@odata.id": "/redfish/v1/ThermalEquipment",
    "@odata.type": "#ThermalEquipment.v1_0_0.ThermalEquipment",
    "@odata.context": "/redfish/v1/$metadata#ThermalEquipmentCollection.ThermalEquipmentCollection",
    
    "Name": "Thermal Equipment",
    "Id": "ThermalEquipment",
    "Description": "List all thermal management equipment",
    
    "CDUs": {
        "@odata.id": "/redfish/v1/ThermalEquipment/CDUs"   
    },
}

# CDUs_data = {
#     "@odata.id": "/redfish/v1/ThermalEquipment/CDUs",
#     "@odata.type": "#CoolingUnitCollection.CoolingUnitCollection",
#      "@odata.context": "/redfish/v1/$metadata#CoolingUnitCollection.CoolingUnitCollection",
     
#     "Name": "CDU Collection",
#     "Description": "中控分配單元（CDU）集合",
    
#     "Members@odata.count": 1,
#     "Members": [{"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1"}],
#     "Oem": {}
# }
CDUs_data_1 = {
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1",
    "@odata.type": "#CoolingUnit.v1_1_0.CoolingUnit",
    "@odata.context": "/redfish/v1/$metadata#CoolingUnit.v1_1_0.CoolingUnit",
    
    "Name": "#1 Cooling Distribution Unit",
    "Id": "1",
    "Description": "First Cooling Distribution Unit for chassis liquid cooling",
    
    # 資訊
    "Manufacturer": "Supermicro",
    "Model": "CoolingUnit",
    # "UUID": "00000000-0000-0000-0000-e45f013e98f8",
    "SerialNumber": "test_1",
    "PartNumber": "test_1",
    "FirmwareVersion": "1.0.0",
    "Version": "test_1",
    "ProductionDate": "2024-10-05T00:00:00Z",
    
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    
    "CoolingCapacityWatts": 100,
    "EquipmentType": "CDU",
    
    # 底下服務
    "Filters": {
        "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Filters"
    },
    "PrimaryCoolantConnectors": {
        "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/PrimaryCoolantConnectors"
    },
    # "SecondaryCoolantConnectors": {
    #     "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/SecondaryCoolantConnectors"
    # },
    "Pumps": {
        "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps"
    },
    "LeakDetection": {
        "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection"
    },
    # 液冷劑參數    
    "Coolant": {
        "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Coolant",
        "CoolantType": "Water",
        "DensityKgPerCubicMeter": 1000,
        "SpecificHeatkJoulesPerKgK": 4180
    },
    # 泵冗餘示例
    "PumpRedundancy": [
        {
            "RedundancyType": "NPlusM",
            "MinNeededInGroup": 1,
            "RedundancyGroup": [
                {
                    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/1"
                },
                {
                    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/2"
                },                
                {
                    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/3"
                }
            ],
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        }
    ],
    "Reservoirs": {
        "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Reservoirs"
    },
    "EnvironmentMetrics": {
        "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/EnvironmentMetrics"
    },
    "Actions": {
        "#CoolingUnit.SetMode": {
            "target": "/redfish/v1/ThermalEquipment/CDUs/1/Actions/CoolingUnit.SetMode",
            "CoolingUnitMode@Redfish.AllowableValues": [
                "Enabled",
                "Disabled"
            ],
            "Mode@Redfish.AllowableValues": [
                "Enabled",
                "Disabled"
            ]
        }

    },
    
    "Links": {
        "Chassis": [
            {
                "@odata.id": "/redfish/v1/Chassis/1"
            }
        ],
        "ManagedBy": [
            {
                "@odata.id": "/redfish/v1/Managers/CDU"
            }
        ]
    },
    # 0513新增
    "Oem": {
        "Supermicro": {
            # "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Oem/Supermicro",
            # "DateTime": {                    
            #     "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Oem/Supermicro/DateTime"
            # },
            # "LedLight": {                  
            #     "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Oem/Supermicro/LedLight"
            # },
            # "Network": {                  
            #     "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Oem/Supermicro/Network"
            # },
            # "Device": {                
            #     "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Oem/Supermicro/Device"
            # },
            # "Unit": { 
            #     "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Oem/Supermicro/Unit"
            # },
            # "Operation": {                   
            #     "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Oem/Supermicro/Operation"
            # }
        }
    }
}

PrimaryCoolantConnectors_data = {
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/PrimaryCoolantConnectors",
    "@odata.type": "#CoolantConnectorCollection.CoolantConnectorCollection",
    "Name": "Primary (supply side) Cooling Loop Connection Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/PrimaryCoolantConnectors/1"
        }
    ],
}

PrimaryCoolantConnectors_data_1 ={
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/PrimaryCoolantConnectors/1",
    "@odata.type": "#CoolantConnector.v1_1_0.CoolantConnector",
    "@odata.context": "/redfish/v1/$metadata#CoolantConnector.v1_1_0.CoolantConnector",
    
    "Id": "1",
    "Name": "Mains Input from Chiller",
    "Description": "Primary input from facility chiller",
    # 額定流量
    "RatedFlowLitersPerMinute": 100,
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "Coolant": {
        "CoolantType": "Water",
        "DensityKgPerCubicMeter": 1000,
        "SpecificHeatkJoulesPerKgK": 4180,
        "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Coolant"
    },
    "CoolantConnectorType": "Pair",
    "FlowLitersPerMinute": {
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/PrimaryFlowLitersPerMinute",
        "Reading": "Out of range"
    },
    "HeatRemovedkW": {
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/PrimaryHeatRemovedkW",
        "Reading": 0.2
    },
    "SupplyTemperatureCelsius": {
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/PrimarySupplyTemperatureCelsius",
        "Reading": 23.32
    },
    "ReturnTemperatureCelsius": {
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/PrimaryReturnTemperatureCelsius",
        "Reading": 23.45
    },
    "DeltaTemperatureCelsius": {
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/PrimaryDeltaTemperatureCelsius",
        "Reading": 0.13
    },
    "SupplyPressurekPa": {
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/PrimarySupplyPressurekPa",
        "Reading": 220.0
    },
    "ReturnPressurekPa": {
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/PrimaryReturnPressurekPa",
        "Reading": 85.0
    },
    "DeltaPressurekPa": {
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/PrimaryDeltaPressurekPa",
        "Reading": 135.0
    },
    "Oem": {
        "supermirco": {  
            "PumpSwapTime": {
                "@odata.type": "#supermirco.PumpSwapTime.v1_0_0.PumpSwapTime", # 一定要放
                "SetPoint": {
                    "Value": 50,
                    "Units": "Hours"
                }
            }   
        }

    },
    
}

cdus_pumps={
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps",
    "@odata.type": "#PumpCollection.PumpCollection",
    "Name": "Cooling Pump Collection",
    "Members@odata.count": 3,
    "Members": [
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/1"
        },
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/2"
        },
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/3"
        }
    ],
}

cdus_pumps_1={
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/1",
    "@odata.type": "#Pump.v1_2_0.Pump",
    "Id": "1",
    "PumpType": "Liquid",
    "Name": "Pump Left",
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "PumpSpeedPercent": {
        "Reading": 0,
        "SpeedRPM": 0
    },
    "FirmwareVersion": "0601",
    "ServiceHours": 1340.3,
    "Location": {
        "PartLocation": {
            "ServiceLabel": "Pump 1",
            "LocationType": "Bay"
        }
    },
    "SpeedControlPercent": {
        "SetPoint": 0,
        "AllowableMax": 100,
        "AllowableMin": 25,
        "ControlMode": "manual"
    },
    "Actions": {
        "#Pump.SetMode": {
            "target": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/1/Actions/Pump.SetMode"
        }
    },
    
}

cdus_pumps_2 = {
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/2",
    "@odata.type": "#Pump.v1_2_0.Pump",
    "Id": "2",
    "PumpType": "Liquid",
    "Name": "Pump Right",
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "PumpSpeedPercent": {
        "Reading": 29,
        "SpeedRPM": 2004
    },
    "FirmwareVersion": "0601",
    "ServiceHours": 1336.67,
    "Location": {
        "PartLocation": {
            "ServiceLabel": "Pump 2",
            "LocationType": "Bay"
        }
    },
    "SpeedControlPercent": {
        "SetPoint": 0,
        "AllowableMax": 100,
        "AllowableMin": 25,
        "ControlMode": "Automatic"
    },
    "Actions": {
        "#Pump.SetMode": {
            "target": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/2/Actions/Pump.SetMode"
        }
    },
    
}

cdus_pumps_3 = {
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/3",
    "@odata.type": "#Pump.v1_2_0.Pump",
    "Id": "3",
    "PumpType": "Liquid",
    "Name": "Pump Right",
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "PumpSpeedPercent": {
        "Reading": 29,
        "SpeedRPM": 3004
    },
    "FirmwareVersion": "0601",
    "ServiceHours": 1336.67,
    "Location": {
        "PartLocation": {
            "ServiceLabel": "Pump 3",
            "LocationType": "Bay"
        }
    },
    "SpeedControlPercent": {
        "SetPoint": 0,
        "AllowableMax": 100,
        "AllowableMin": 25,
        "ControlMode": "Automatic"
    },
    "Actions": {
        "#Pump.SetMode": {
            "target": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/3/Actions/Pump.SetMode"
        }
    },
   
}

cdus_filters={
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Filters",
    "@odata.type": "#FilterCollection.FilterCollection",
    
    "Name": "Filter Collection",

    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Filters/1"
        }
    ]
}

cdus_filters_1 = {
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Filters/1",
    "@odata.type": "#Filter.v1_0_0.Filter",
    "@odata.context": "/redfish/v1/$metadata#Filter.v1_0_0.Filter",
    
    "Id": "1",
    "Name": "Cooling Loop Filter",
    "Description": "Cooling Loop Filter",
    # 設備資訊
    "ServicedDate": "2020-12-24T08:00:00Z",
    "Manufacturer": "Contoso",
    "Model": "MrCoffee",
    "PartNumber": "Cone4",
    # 設備服務時間
    "ServiceHours": 5791,
    "RatedServiceHours": 10000,
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    # 實體位置
    "Location": {
        "Placement": {
        "Row": "North 1"
        }
    },
}

# environment_metrics = {
#     "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/EnvironmentMetrics",
#     "@odata.type": "#EnvironmentMetrics.v1_3_2.EnvironmentMetrics",
#     "@odata.context": "/redfish/v1/$metadata#EnvironmentMetrics.v1_3_2.EnvironmentMetrics",
    
#     "Id": "EnvironmentMetrics",
#     "Name": "CDU Environment Metrics",
#     "Description":    "冷卻分配單元環境感測指標",

#     # 溫度（Celsius）
#     "TemperatureCelsius": {
#         "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/TemperatureCelsius",
#         "Reading": 19.81
#     },
#     # 露點（Celsius）
#     "DewPointCelsius": {
#         "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/DewPointCelsius",
#         "Reading": 13.53
#     },
#     # 相對濕度（百分比）
#     "HumidityPercent": {
#         "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/HumidityPercent",
#         "Reading": 67.11
#     },
#     # 絕對濕度（克／立方米)
#     "AbsoluteHumidity": {
#         "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/AbsoluteHumidity",
#         "Reading": 11.46
#     },
#     "Oem": {},
# }

reservoirs = {
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Reservoirs",
    "@odata.type": "#ReservoirCollection.ReservoirCollection",
    "@odata.context": "/redfish/v1/$metadata#ReservoirCollection.ReservoirCollection",
    
    "Name": "Reservoir Collection",
    "Description": "Reservoirs Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Reservoirs/1"
        },
    ],
    "Oem":{}
}

reservoirs_1 = {
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Reservoirs/1",
    "@odata.type": "#Reservoir.v1_0_0.Reservoir",
    "@odata.context": "/redfish/v1/$metadata#Reservoir.v1_0_0.Reservoir",
    
    "Id": "1",
    "Name": "Liquid Level",
    "Description": "Primary reserve reservoir for CDU 1",
    # 容量資訊
    "ReservoirType": "Reserve",
    "CapacityLiters": -1, # 最大容量 未有此功能填-1
    "FluidLevelStatus": "OK",
    # "FluidLevelPercent": { # 考慮要不要
    #     "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/ReservoirFluidLevelPercent",
    #     "Reading": 82.5
    # },
    
    # 設備資訊
    "Manufacturer": "supermirco",
    "Model": "ReservoirModelX",
    "PartNumber": "RES-100",
    "SparePartNumber": "SPN-100",
    "PhysicalContext": "LiquidInlet",
    # 狀態
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    
    # 實體位置
    "Location": {
        "PartLocation": {
            "ServiceLabel": "Reservoir 1",
            "LocationType": "Bay"
        }
    },
    "Oem": {}
}

LeakDetection_data = {
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection",
    "@odata.type": "#LeakDetection.v1_0_0.LeakDetection",
    "@odata.context": "/redfish/v1/$metadata#LeakDetection.v1_0_0.LeakDetection",
    
    "Id": "LeakDetection",
    "Name": "Leak Detection",
    "Description": "LeakDetection",
    # "Members@odata.count": 1,
    # ---------------------------
    # "Status": {
    #     "State": "Enabled",
    #     "Health": "OK"
    # },
    # "LeakDetectorGroups": [
    #     {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection/LeakDetectorGroups"}
    # ],
    # "LeakDetectors": {
    #     "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection/LeakDetectors"
    # },
    # "Members": [
    #     {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection/LeakDetectors"}
    # ], 
    "Oem": {}  
}

LeakDetectionLeakDetectors_data = {
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection/LeakDetectors",
    "@odata.type": "#LeakDetectors.v1_6_0.LeakDetectors",
    "Id": "1",
    "Name": "LeakDetectors",
    "Status": {
        "State": "Enabled",
        "Health": "Critical"
    },
}
# -------------------------------------
# Automatic setting patch設置
PrimaryCoolantConnectors_patch = ThermalEquipment_ns.model('PrimaryCoolantConnectors1Patch', {
    'DeltaTemperatureCelsius': fields.Integer(
        required=True,
        description='temperature setting',
        default=50,
    ),
    "DeltaPressurekPa": fields.Integer(
        required=True,
        description='pressure setting',
        default=50,
    ),
    "PumpSwapTime": fields.Integer(
        required=True,
        description='pump swap time setting',
        default=50,
    ),
})

# pumpspeed patch設置
pumpspeed_patch = ThermalEquipment_ns.model('PumpSpeedControlPatch', {
    'pump_speed': fields.Integer(
        required=True,
        description='pump speed (0–100)',
        default=50,
    ),
    "pump_switch": fields.Boolean(
        required=True,
        description='pump switch',
    ),
})


@ThermalEquipment_ns.route("/ThermalEquipment")
class ThermalEquipment(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("thermal_equipment")
    def get(self):
        """get thermal equipment"""
        return ThermalEquipment_data
            
@ThermalEquipment_ns.route("/ThermalEquipment/CDUs")
class ThermalEquipmentCdus(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("thermal_equipment_cdus")
    def get(self):
        # return CDUs_data
        return RfThermalEquipmentService().fetch_CDUs()
    
@ThermalEquipment_ns.route("/ThermalEquipment/CDUs/<cdu_id>")
class ThermalEquipmentCdus1(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("thermal_equipment_cdus")
    def get(self, cdu_id: str):
        # return CDUs_data_1
        return RfThermalEquipmentService().fetch_CDUs(cdu_id)
    
@ThermalEquipment_ns.route("/ThermalEquipment/CDUs/<cdu_id>/PrimaryCoolantConnectors")
class PrimaryCoolantConnectors(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("primary_coolant_connectors")
    def get(self, cdu_id: str):
        return RfThermalEquipmentService().fetch_CDUs_PrimaryCoolantConnectors(cdu_id)
    
@ThermalEquipment_ns.route("/ThermalEquipment/CDUs/1/PrimaryCoolantConnectors/1")
class PrimaryCoolantConnectors1(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("primary_coolant_connectors_1")
    def get(self):
        value_all = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/status/sensor_value")
        pump_swap_time = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/control/pump_swap_time")
        
        PrimaryCoolantConnectors_data_1["FlowLitersPerMinute"]["Reading"] = value_all["coolant_flow_rate"]
        PrimaryCoolantConnectors_data_1["HeatRemovedkW"]["Reading"] = value_all["heat_capacity"]
        
        SupplyTemperatureCelsius = PrimaryCoolantConnectors_data_1["SupplyTemperatureCelsius"]["Reading"] = value_all["temp_coolant_supply"]
        ReturnTemperatureCelsius = PrimaryCoolantConnectors_data_1["ReturnTemperatureCelsius"]["Reading"] = value_all["temp_coolant_return"]
        PrimaryCoolantConnectors_data_1["DeltaTemperatureCelsius"]["Reading"] = SupplyTemperatureCelsius - ReturnTemperatureCelsius
       
        SupplyPressurekPa = PrimaryCoolantConnectors_data_1["SupplyPressurekPa"]["Reading"] = value_all["pressure_coolant_supply"]
        ReturnPressurekPa = PrimaryCoolantConnectors_data_1["ReturnPressurekPa"]["Reading"] = value_all["pressure_coolant_return"]
        PrimaryCoolantConnectors_data_1["DeltaPressurekPa"]["Reading"] = SupplyPressurekPa - ReturnPressurekPa
        
        PrimaryCoolantConnectors_data_1["Oem"]["supermirco"]["PumpSwapTime"]["SetPoint"]["Value"] = pump_swap_time
        
        return PrimaryCoolantConnectors_data_1
    
    @ThermalEquipment_ns.expect(PrimaryCoolantConnectors_patch, validate=True)
    def patch(self):
        body = request.get_json(force=True)
        # 驗證模式
        if Controls_data_all["OperationMode"]["ControlMode"] != "Automatic": return "only Automatic can setting"
        
        temp_set = body["DeltaTemperatureCelsius"]
        pressure_set = body["DeltaPressurekPa"]
        pump_swap_time = body["PumpSwapTime"]
        # 轉發到內部控制 API
        try:
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/status/op_mode",
                json={"mode": "auto", "temp_set": temp_set, "pressure_set": pressure_set, "pump_swap_time": pump_swap_time},
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
        PrimaryCoolantConnectors_data_1["DeltaTemperatureCelsius"]["Reading"] = temp_set
        PrimaryCoolantConnectors_data_1["DeltaPressurekPa"]["Reading"] = pressure_set
        PrimaryCoolantConnectors_data_1["Oem"]["supermirco"]["PumpSwapTime"]["SetPoint"]["Value"] = pump_swap_time
        
        return PrimaryCoolantConnectors_data_1, 200
    
@ThermalEquipment_ns.route("/ThermalEquipment/CDUs/1/Pumps")
class ThermalEquipmentCdus1Pumps(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("thermal_equipment_cdus_1_pumps")
    def get(self):    
        return cdus_pumps
    
#--------------------------pump1---------------------------------------- 
pump_hight_speed = 1000
@ThermalEquipment_ns.route("/ThermalEquipment/CDUs/1/Pumps/1")
class ThermalEquipmentCdus1Pumps1(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("thermal_equipment_cdus_1_pumps_1")
    def get(self):
        pump_speed = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/status/pump_speed")["pump1_speed"]
        cdus_pumps_1["PumpSpeedPercent"]["Reading"] = pump_speed
        cdus_pumps_1["PumpSpeedPercent"]["SpeedRPM"] = (pump_speed / pump_hight_speed) * 100
        
        state = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/status/pump_state")["pump1_state"]
        health = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/status/pump_health")["pump1_health"]
        service_hours = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/status/pump_service_hours")["pump1_service_hours"]
        if state == "Disable": state = "Disabled"
        cdus_pumps_1["Status"]["State"] = state
        cdus_pumps_1["Status"]["Health"] = health
        cdus_pumps_1["ServiceHours"] = service_hours
        

        return cdus_pumps_1
        
    # @requires_auth
    @ThermalEquipment_ns.expect(pumpspeed_patch, validate=True)
    def patch(self):
        body = request.get_json(force=True)
        new_sp = body['pump_speed']
        new_sw = body['pump_switch']
        
        # 驗證模式
        if Controls_data_all["OperationMode"]["ControlMode"] != "Manual": return "only Manual can setting"
        
        # 驗證範圍
        scp = cdus_pumps_1["SpeedControlPercent"]
        if not (scp["AllowableMin"] <= new_sp <= scp["AllowableMax"]):
            return {
                "error": f"pump_speed needs to be between {scp['AllowableMin']} and {scp['AllowableMax']}"
            }, 400

        # 轉發到內部控制 API
        try:
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/control/pump1_speed",
                json={"pump_speed": new_sp, "pump_switch": new_sw},
                timeout=3
            )
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
        cdus_pumps_1["Status"]["State"] = "Enabled" if new_sw else "Disabled"

        # 回傳整個 Pump 資源
        return cdus_pumps_1, 200

#--------------------------pump2---------------------------------------- 
@ThermalEquipment_ns.route("/ThermalEquipment/CDUs/1/Pumps/2")
class ThermalEquipmentCdus1Pumps2(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("thermal_equipment_cdus_1_pumps_2")
    def get(self):
        pump_speed = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/status/pump_speed")["pump2_speed"]
        cdus_pumps_2["PumpSpeedPercent"]["Reading"] = pump_speed
        cdus_pumps_2["PumpSpeedPercent"]["SpeedRPM"] = (pump_speed / pump_hight_speed) * 100
        
        state = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/status/pump_state")["pump2_state"]
        health = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/status/pump_health")["pump2_health"]
        service_hours = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/status/pump_service_hours")["pump2_service_hours"]
        if state == "Disable": state = "Disabled"
        cdus_pumps_2["Status"]["State"] = state
        cdus_pumps_2["Status"]["Health"] = health
        cdus_pumps_2["ServiceHours"] = service_hours
        
        return cdus_pumps_2
        
    # @requires_auth
    @ThermalEquipment_ns.expect(pumpspeed_patch, validate=True)
    def patch(self):
        body = request.get_json(force=True)
        new_sp = body['pump_speed']
        new_sw = body['pump_switch']
        
        # 驗證模式
        if Controls_data_all["OperationMode"]["ControlMode"] != "Manual": return "only Manual can setting"
        
        # 驗證範圍
        scp = cdus_pumps_2["SpeedControlPercent"]
        if not (scp["AllowableMin"] <= new_sp <= scp["AllowableMax"]):
            return {
                "error": f"pump_speed needs to be between {scp['AllowableMin']} and {scp['AllowableMax']}"
            }, 400

        # 轉發到內部控制 API
        try:
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/control/pump2_speed",
                json={"pump_speed": new_sp, "pump_switch": new_sw},
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
        cdus_pumps_2["Status"]["State"] = "Enabled" if new_sw else "Disabled"

        # 回傳整個 Pump 資源
        return cdus_pumps_2, 200


#--------------------------pump3---------------------------------------- 
@ThermalEquipment_ns.route("/ThermalEquipment/CDUs/1/Pumps/3")
class ThermalEquipmentCdus1Pumps3(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("thermal_equipment_cdus_1_pumps_3")
    def get(self):
        pump_speed = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/status/pump_speed")["pump3_speed"]
        cdus_pumps_3["PumpSpeedPercent"]["Reading"] = pump_speed
        cdus_pumps_3["PumpSpeedPercent"]["SpeedRPM"] = (pump_speed / pump_hight_speed) * 100
        
        state = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/status/pump_state")["pump3_state"]
        health = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/status/pump_health")["pump3_health"]
        service_hours = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/status/pump_service_hours")["pump3_service_hours"]
        if state == "Disable": state = "Disabled"
        cdus_pumps_3["Status"]["State"] = state
        cdus_pumps_3["Status"]["Health"] = health
        cdus_pumps_3["ServiceHours"] = service_hours
        
        return cdus_pumps_3
        
    # @requires_auth
    @ThermalEquipment_ns.expect(pumpspeed_patch, validate=True)
    def patch(self):
        body = request.get_json(force=True)
        new_sp = body['pump_speed']
        new_sw = body['pump_switch']
        
        # 驗證模式
        if Controls_data_all["OperationMode"]["ControlMode"] != "Manual": return "only Manual can setting"
        
        # 驗證範圍
        scp = cdus_pumps_3["SpeedControlPercent"]
        if not (scp["AllowableMin"] <= new_sp <= scp["AllowableMax"]):
            return {
                "error": f"pump_speed needs to be between {scp['AllowableMin']} and {scp['AllowableMax']}"
            }, 400

        # 轉發到內部控制 API
        try:
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/control/pump3_speed",
                json={"pump_speed": new_sp, "pump_switch": new_sw},
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
        cdus_pumps_3["Status"]["State"] = "Enabled" if new_sw else "Disabled"

        # 回傳整個 Pump 資源
        return cdus_pumps_3, 200

    
    
@ThermalEquipment_ns.route("/ThermalEquipment/CDUs/1/Filters")
class ThermalEquipmentCdus1Filters(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("thermal_equipment_cdus_1_filters")
    def get(self):
        
        return cdus_filters
    
@ThermalEquipment_ns.route("/ThermalEquipment/CDUs/1/Filters/1")
class ThermalEquipmentCdus1Filters1(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("thermal_equipment_cdus_1_filters_1")
    def get(self):
        
        return cdus_filters_1
    
@ThermalEquipment_ns.route("/ThermalEquipment/CDUs/<cdu_id>/EnvironmentMetrics")
class ThermalEquipmentCdus1EnvironmentMetrics(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("thermal_equipment_cdus_1_environment_metrics")
    def get(self, cdu_id):
        thermal_equipment_service = RfThermalEquipmentService()
        return thermal_equipment_service.fetch_CDUs_EnvironmentMetrics(cdu_id)
        # return "environment_metrics"
    
@ThermalEquipment_ns.route("/ThermalEquipment/CDUs/1/Reservoirs")
class ThermalEquipmentCdus1Reservoirs(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("thermal_equipment_cdus_1_reservoirs")
    def get(self):
        
        return reservoirs
    
    
@ThermalEquipment_ns.route("/ThermalEquipment/CDUs/1/Reservoirs/1")
class ThermalEquipmentCdus1Reservoirs1(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("thermal_equipment_cdus_1_reservoirs_1")
    def get(self):
        
        return reservoirs_1

@ThermalEquipment_ns.route("/ThermalEquipment/CDUs/<cdu_id>/LeakDetection")
class LeakDetection(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("thermal_equipment_cdus_1_LeakDetection")
    def get(self, cdu_id):
        
        return LeakDetection_data    

test = [
    "/ThermalEquipment/CDUs/<cdu_id>/test",
    "/ThermalEquipment/CDUs/<cdu_id>/test2"
]


@ThermalEquipment_ns.route("/ThermalEquipment/CDUs/<cdu_id>/LeakDetection/LeakDetectors", *test)
class LeakDetectionLeakDetectors(Resource):
    # # @requires_auth
    @ThermalEquipment_ns.doc("thermal_equipment_cdus_1_LeakDetection_LeakDetectors")
    def get(self, cdu_id):
        rf_ThermalEquipment_service = RfThermalEquipmentService()
        resp_json = rf_ThermalEquipment_service.fetch_CDUs_LeakDetection_LeakDetectors(cdu_id)
        return resp_json
           
# 0513新增 /redfish/v1/ThermalEquipment/CDUs/{CoolingUnitId}/Oem
# @ThermalEquipment_ns.route('/ThermalEquipment/CDUs/<string:id>/Oem')
# class CduOem(Resource):
#     def get(self, id):
#         return {
#             "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem",
#             "@odata.type": "#Oem.Supermicro.Oem",
#             "Supermicro": {
#                 "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro"
#             }
#         }, 200

# @ThermalEquipment_ns.route('/ThermalEquipment/CDUs/<string:id>/Oem/Supermicro')
# class CduOemSupermicro(Resource):
#     def get(self, id):
#         return {
#             "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro",
#             "@odata.type": "#Supermicro.Supermicro",
#             "DateTime":     { "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/DateTime" },
#             "LedLight":     { "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/LedLight" },
#             "Network":      { "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/Network" },
#             "Device":       { "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/Device" },
#             "Unit":         { "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/Unit" },
#             "Operation":    { "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/Operation" },
#             "Actions":      { "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/Actions" },
#             "SensorModule": { "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/SensorModule" },
#             "ControlUnit":  { "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/ControlUnit" },
#             "ControlSetting":  { "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/ControlSetting" },
#             "CloseValveStop":  { "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/CloseValveStop" },
#             "ContinueModeSwitch":  { "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/ContinueModeSwitch" },
#             "DebugSwitch":  { "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/DebugSwitch" },
            
#             # "FactorySettingActionInfo":  { "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/FactorySettingActionInfo" },
#             # "PumpOperationTimeResetActionInfo":  { "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/PumpOperationTimeResetActionInfo" },
#         }, 200        

# subnodes = ["DateTime","LedLight","Network","Device","Unit","Operation","Actions","SensorModule","ControlUnit", "ControlSetting", "CloseValveStop", "ContinueModeSwitch", "DebugSwitch"]
# for node in subnodes:
#     @ThermalEquipment_ns.route(f'/ThermalEquipment/CDUs/<string:id>/Oem/Supermicro/{node}')
#     class CduOemNode(Resource):
#         def get(self, id, node=node):
#             return {
#                 "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{id}/Oem/Supermicro/{node}",
#                 "@odata.type": f"#Supermicro.{node}",
#             }, 200        