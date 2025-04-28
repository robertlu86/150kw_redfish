'''
這是Redfish的chassis service
'''
import os, re
from mylib.models.sensor_model import SensorCollectionModel, SensorModel, StatusModel
from mylib.services.base_service import BaseService
import re

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
    }

    def fetch_sensors_collection(self, chassis_id: str):
        """
        對應 "/redfish/v1/Chassis/{CHASSIS_ID}/Sensors"
        ex: "/redfish/v1/Chassis/1/Sensors
        """
        sensor_collection_model = SensorCollectionModel()
        sensor_collection_model.odata_id = sensor_collection_model.build_odata_id(chassis_id)

        for sensor_id in self.SENSOR_IDS:
            sensor_collection_model.Members.append({"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/Sensors/{sensor_id}"})
        sensor_collection_model.Members_odata_count = len(sensor_collection_model.Members)
        return sensor_collection_model.model_dump(by_alias=True)

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

    def fetch_sensors_by_name(self, chassis_id: str, sensor_name: str):
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

        m = SensorModel(
            chassis_id=chassis_id,
            Id = sensor_name,
            Name = self._camel_to_words(sensor_name),
            Reading=reading_info["Reading"],
            ReadingUnits = reading_info["ReadingUnits"],
            Status = StatusModel(Health="OK", State="Enabled")
        )

        # odata_id
        # m.odata_id = f"/redfish/v1/Chassis/{chassis_id}/Sensors/{sensor_name}"

        resp_json = m.model_dump(by_alias=True)
        del resp_json['chassis_id']
        return resp_json

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
        reading_info = id_readingInfo_map.get(sensor_id, {})
        if reading_info:
            url = f"{os.environ['ITG_REST_HOST']}/api/v1/cdu/status/sensor_value"
            response = self.send_get(url)
            sensor_value_json = response.json()
            reading_info["Reading"] = self._calc_delta_value(sensor_value_json, reading_info["fieldNameToFetchSensorValue"])
        else:
            reading_info["Reading"] = 0.0
        return reading_info
    
    
    def _calc_delta_value(self, sensor_value: dict, fieldNameToFetchSensorValue: str ) -> str:
        """
        如果有兩欄(欄位含',')，則計算兩個sensor value的差值
        """
        if "," in fieldNameToFetchSensorValue: 
            fieldNames = fieldNameToFetchSensorValue.split(",")
            return sensor_value[ fieldNames[0] ] - sensor_value[ fieldNames[1] ]
        else:
            return sensor_value[ fieldNameToFetchSensorValue ]

    def _camel_to_words(self, name: str) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
