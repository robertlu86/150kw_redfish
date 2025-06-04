'''
這是Redfish的chassis service
'''
import os, re, json
from typing import Optional
from mylib.models.rf_sensor_model import (
    RfSensorCollectionModel, 
    RfSensorModel, 
)
from mylib.models.rf_status_model import RfStatusModel, RfStatusHealth, RfStatusState
from mylib.services.base_service import BaseService
from mylib.models.rf_power_supply_model import RfPowerSupplyCollectionModel, RfPowerSupplyModel
from mylib.models.rf_cdu_model import RfCduModel, RfCduCollectionModel
from cachetools import LRUCache, cached
from typing import Dict, Any

from load_env import hardware_info


class RfChassisService(BaseService):
    SENSOR_IDS = {
        "PrimaryFlowLitersPerMinute",
        "PrimaryHeatRemovedkW",
        "PrimarySupplyTemperatureCelsius",
        "PrimaryReturnTemperatureCelsius",
        "PrimaryDeltaTemperatureCelsius",
        "PrimarySupplyPressurekPa",
        "PrimaryReturnPressurekPa",
        "PrimaryDeltaPressurekPa",
        "TemperatureCelsius",
        "DewPointCelsius",
        "HumidityPercent",
        "WaterPH",
        "Conductivity",
        "Turbidity",
        "PowerConsume",
        # "fan1",
        # "fan2",
        # "fan3",
        # "fan4",
        # "fan5",
        # "fan6",
        # "fan7",
        # "fan8",
    }
    # 動態調整風扇數量
    fan_cnt = int(os.getenv("REDFISH_FAN_COLLECTION_CNT", 8))
    for i in range(fan_cnt):
        SENSOR_IDS.add(f"Fan{i+1}")

    def fetch_sensors_collection(self, chassis_id: str) -> dict:
        """
        對應 "/redfish/v1/Chassis/{CHASSIS_ID}/Sensors"
        ex: "/redfish/v1/Chassis/1/Sensors
        """
        sensor_collection_model = RfSensorCollectionModel()
        sensor_collection_model.odata_id = sensor_collection_model.build_odata_id(chassis_id)

        for sensor_id in self.SENSOR_IDS:
            sensor_collection_model.Members.append({"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/{sensor_id}"})
        sensor_collection_model.Members = sorted(sensor_collection_model.Members, key=lambda x: x["@odata.id"])
        sensor_collection_model.Members_odata_count = len(sensor_collection_model.Members)
        return sensor_collection_model.to_dict()

        # sensor_collection_data = {
        #     "@odata.type": "#SensorCollection.SensorCollection",
        #     "Name": "Sensor Collection",
        #     "Members@odata.count": 11,
        #     "Members": [
        #         {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryFlowLitersPerMinute"},
        #         {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryHeatRemovedkW"},
        #         {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimarySupplyTemperatureCelsius"},
        #         {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryReturnTemperatureCelsius"},
        #         {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryDeltaTemperatureCelsius"},
        #         {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimarySupplyPressurekPa"},
        #         {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryReturnPressurekPa"},
        #         {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PrimaryDeltaPressurekPa"},
        #         {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/TemperatureCelsius"},
        #         {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/DewPointCelsius"},
        #         {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/HumidityPercent"},
        #         {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/WaterPH"},
        #         {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/Conductivity"},
        #         {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/Turbidity"},
        #         {"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/PowerConsume"},
        #     ],
        #     "Oem": {},
        #     "@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors"
        # }
        # return sensor_collection_data

    def fetch_sensors_by_name(self, chassis_id: str, sensor_name: str) -> dict:
        """
        對應 "/redfish/v1/Chassis/{CHASSIS_ID}/Sensors/{SENSOR_NAME}"
        ex: "/redfish/v1/Chassis/1/Sensors/PrimaryFlowLitersPerMinute"

        :param chassis_id: str
        :param sensor_name: str, ex: PrimaryFlowLitersPerMinute|PrimaryHeatRemovedkW|...
        :return: dict
        """
        # m = SensorModel(chassis_id=chassis_id)

        # m.Id = sensor_name
        # m.Name = self._camel_to_words(m.Id)
        # Reading, ReadingUnits
        reading_info = self._load_reading_info_by_sensor_id(sensor_name)
        # m.Reading = reading_info["Reading"]
        # m.ReadingUnits = reading_info["ReadingUnits"]
        # print("reading: ", reading_info["Reading"]["reading"])
        # print("reading_info: ", reading_info)
        m = RfSensorModel(
            chassis_id=chassis_id,
            Id = sensor_name,
            Name = self._camel_to_words(sensor_name),
            Reading=reading_info["Reading"],
            ReadingUnits = reading_info["ReadingUnits"],
            Status = RfStatusModel(Health=reading_info["Status"].get("Health") or reading_info["Status"].get("health"), State=reading_info["Status"].get("State") or reading_info["Status"].get("state"))
        )

        # odata_id
        # m.odata_id = f"/redfish/v1/Chassis/{chassis_id}/Sensors/{sensor_name}"

        # resp_json = m.model_dump(by_alias=True)
        # del resp_json['chassis_id']
        resp_json = m.to_dict()
        return resp_json
    
    def fetch_PowerSubsystem_PowerSupplies(self, chassis_id: str, power_supply_id: str = None):
        """
        對應 /Chassis/1/PowerSubsystem/PowerSupplies (if `power_supply_id` is None)
        對應 /Chassis/1/PowerSubsystem/PowerSupplies/{power_supply_id}
        :param power_supply_id: str, ex: 1. 
        :return: dict
        :note 
            (1) 目前有四個PowerSupplies：24V * 2台，12V * 2台，RestAPI不會對應電源與Id的關係，由redfish自己mapping
        """
        ret_json = None

        summary_info = self._read_components_chassis_summary_from_cache() # why no chassis_id?

        if power_supply_id is None:
            m = RfPowerSupplyCollectionModel(chassis_id=chassis_id)
            # ret_json = m.model_dump(
            #             by_alias=True,
            #             include=RfPowerSupplyCollectionModel.model_fields.keys(),
            #             exclude_none=True
            #         )
            ret_json = m.to_dict()
        else:
            id_name_dict = self.__read_power_supply_id_name_dict()
            power_supply_name = id_name_dict[power_supply_id]
            
            m = RfPowerSupplyModel(
                chassis_id=chassis_id,
                Id = power_supply_id,
                # **hardware_info.get("PowerSupply", {})
                **hardware_info["PowerSupplies"][power_supply_id]
                # Status = RfStatusModel(Health=RfStatusHealth.OK, State=RfStatusState.Enabled)
            )
            m.Status = RfStatusModel.from_dict(summary_info.get(power_supply_name).get("status", {}))
            # ret_json = m.model_dump(
            #             by_alias=True,
            #             include=RfPowerSupplyModel.model_fields.keys()
            #         )
            ret_json = m.to_dict()
        return ret_json
    
    @cached(cache=LRUCache(maxsize=3))
    def __read_power_supply_id_name_dict(self) -> Dict[str, Any]:
        """
        Generate mapping of (PowerSupplyId, restAPI name)
        (key, value) = (Redfish PowerSupplyId, Name respond from RestAPI)
        """
        json_formatted_str = os.getenv("REDFISH_POWERSUPPLY_COLLECTION_PowerSupplyId_Name_dict", "{}")
        PowerSupplyId_Name_dict = json.loads(json_formatted_str)
        return PowerSupplyId_Name_dict

    def _load_reading_info_by_sensor_id(self, sensor_id: str) -> str:
        """
        @return Reading & ReadingUnits
        @note api response from /cdu/status/sensor_value is
            {
                "temp_coolant_supply": 0,
                " temp_coolant_supply_spare": 0,
                "temp_coolant_return": 0,
                "temp_coolant_return_spare": 0,
                "pressure_coolant_supply": -125,
                "pressure_coolant_supply_spare": -125,
                "pressure_coolant_return": -125,
                "pressure_coolant_return_spare": -125,
                "pressure_filter_in": -125,
                "pressure_filter_out": -125,
                "coolant_flow_rate": -70,
                "temperature_ambient": 0,
                "humidity_relative": 0,
                "temperature_dew_point": 0,
                "ph_level": 0,
                "conductivity": 0,
                "turbidity": 0,
                "power_total": 0,
                "cooling_capacity": 0,
                "heat_capacity": 0,
                "fan1_speed": 0,
                "fan2_speed": 0,
                "fan3_speed": 0,
                "fan4_speed": 0,
                "fan5_speed": 0,
                "fan6_speed": 0,
                "fan7_speed": 0,
                "fan8_speed": 0
            }
        """
        id_readingInfo_map = {
            "PrimaryFlowLitersPerMinute": {
                "ReadingUnits": "L/min", 
                "fieldNameToFetchSensorValue": "coolant_flow_rate"
            },
            "PrimaryHeatRemovedkW": {
                "ReadingUnits": "kW", 
                "fieldNameToFetchSensorValue": "heat_capacity"
            },
            "PrimarySupplyTemperatureCelsius": {
                "ReadingUnits": "Celsius", 
                "fieldNameToFetchSensorValue": "temp_coolant_supply"
            },
            "PrimaryReturnTemperatureCelsius": {
                "ReadingUnits": "Celsius", 
                "fieldNameToFetchSensorValue": "temp_coolant_return"
            }, 
            "PrimaryDeltaTemperatureCelsius": {
                "ReadingUnits": "Celsius", 
                "fieldNameToFetchSensorValue": "temp_coolant_supply,temp_coolant_return"
            },
            "PrimarySupplyPressurekPa": {
                "ReadingUnits": "kPa", 
                "fieldNameToFetchSensorValue": "pressure_coolant_supply"
            },
            "PrimaryReturnPressurekPa": {
                "ReadingUnits": "kPa", 
                "fieldNameToFetchSensorValue": "pressure_coolant_return"
            },
            "PrimaryDeltaPressurekPa": {
                "ReadingUnits": "kPa", 
                "fieldNameToFetchSensorValue": "pressure_coolant_supply,pressure_coolant_return"
            },
            "TemperatureCelsius": {
                "ReadingUnits": "Celsius", 
                "fieldNameToFetchSensorValue": "temperature_ambient"
            },
            "DewPointCelsius": {
                "ReadingUnits": "Celsius", 
                "fieldNameToFetchSensorValue": "temperature_dew_point"
            },
            "HumidityPercent": {
                "ReadingUnits": "Percent", 
                "fieldNameToFetchSensorValue": "humidity_relative"
            },
            "WaterPH": {
                "ReadingUnits": "pH", 
                "fieldNameToFetchSensorValue": "ph_level"
            },
            "Conductivity": {
                "ReadingUnits": "μs/cm", 
                "fieldNameToFetchSensorValue": "conductivity"
            },
            "Turbidity": {
                "ReadingUnits": "NTU", 
                "fieldNameToFetchSensorValue": "turbidity"
            },
            "PowerConsume": {
                "ReadingUnits": "kW", 
                "fieldNameToFetchSensorValue": "power_total"
            },     
        }
        # 動態調整風扇數量
        fan_cnt = int(os.getenv("REDFISH_FAN_COLLECTION_CNT", 8))
        for i in range(fan_cnt):
            id_readingInfo_map[f"Fan{i+1}"] = {
                "ReadingUnits": "rpm", 
                "fieldNameToFetchSensorValue": f"fan{i+1}"
            }
            
        
        reading_info = id_readingInfo_map.get(sensor_id, {})
        if reading_info:
            sensor_value_json = self._read_components_chassis_summary_from_cache()
            # print("Infttest: ", reading_info)
            # print("sensor_value_json: ", sensor_value_json)
            reading_info["Reading"], reading_info["Status"] = self._calc_delta_value_status(sensor_value_json, reading_info["fieldNameToFetchSensorValue"])
            # reading_info["Status"] = sensor_value_json[reading_info["fieldNameToFetchSensorValue"]]["status"]
        else:
            reading_info["Reading"] = 0.0  
        # print("resulttest:" , reading_info)    
        return reading_info
    
    # def _calc_delta_value(self, sensor_value: dict, fieldNameToFetchSensorValue: str ) -> str:
    #     """
    #     如果有兩欄(欄位含',')，則計算兩個sensor value的差值
    #     """
    #     if "," in fieldNameToFetchSensorValue: 
    #         fieldNames = fieldNameToFetchSensorValue.split(",")
    #         return sensor_value[ fieldNames[0] ] - sensor_value[ fieldNames[1] ]
    #     else:
    #         return sensor_value[ fieldNameToFetchSensorValue ]
    
    # 取得 thermal_subsystem 風扇數量
    def get_thermal_subsystem_fans_count(self, chassis_id: str):
        FAN_COUNT = int(os.getenv("REDFISH_FAN_COLLECTION_CNT", 8))
        base_path = f"/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem/Fans"

        # 用 list comprehension 動態產生 Members 清單
        members = [
            {"@odata.id": f"{base_path}/{i}"}
            for i in range(1, FAN_COUNT + 1)
        ]

        ThermalSubsystem_Fans_count = {
            "@odata.context": "/redfish/v1/$metadata#Fans.FanCollection",
            "@odata.id": base_path,
            "@odata.type": "#FanCollection.FanCollection",
            "Name": "Fans Collection",
            "Members@odata.count": FAN_COUNT,
            "Members": members
        }


        return ThermalSubsystem_Fans_count

    # 取得 thermal_subsystem 風扇資訊
    def get_thermal_subsystem_fans_data(self, chassis_id: str, fan_id: str):
        FAN_COUNT = int(os.getenv("REDFISH_FAN_COLLECTION_CNT", 8))
        base_path = f"/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem/Fans"
        sensor_value_json = self._read_components_chassis_summary_from_cache()
        
        FAN_TEMPLATE = {
            "@odata.type": "#Fan.v1_5_0.Fan",
            "@odata.context": "/redfish/v1/$metadata#Fan.v1_5_0.Fan",
            "PhysicalContext": "Chassis",
            "PartNumber": "578-5010007",
            "SerialNumber": "SN12345678", # 風扇本體序號 去哪讀
            "Manufacturer": "Supermicro",
            "Model": "K3G310-PV69-03-42",
            "SparePartNumber": "SPN-FAN-100",
            "Status": {"State": "Enabled", "Health": "OK"},
            "Location": {
                "PartLocation": {"LocationType": "Bay"}
            },
            "Oem": {}
        }

        # 複製範本
        item = FAN_TEMPLATE.copy()

        # 設定每支風扇特有欄位
        item["@odata.id"] = f"{base_path}/{fan_id}"
        item["Id"] = str(fan_id)
        item["Name"] = f"Fan Right {fan_id}"
        item["Description"] = f"Fan Right {fan_id}"
        # 速度感測器連結
        item["SpeedPercent"] = {
            "DataSourceUri": f"/redfish/v1/Chassis/{chassis_id}/ThermalSubsystem/Sensors/Fan{fan_id}",
            "Reading":  sensor_value_json["fan" + str(fan_id)]["reading"],
            "SpeedRPM": sensor_value_json["fan" + str(fan_id)]["reading"] * 16000 / 100,
        }
        # 位置服務標籤
        item["Location"]["PartLocation"]["ServiceLabel"] = f"Fan Bay {fan_id}"

        item["Status"]["State"] = sensor_value_json["fan" + str(fan_id)]["status"]["state"]
        item["Status"]["Health"] = sensor_value_json["fan" + str(fan_id)]["status"]["health"]

            
        return item 