'''
這是Redfish的chassis service
'''
from mylib.models.sensor_model import SensorCollectionModel, SensorModel
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
        m = SensorModel(chassis_id=chassis_id)
        m.Id = sensor_name
        m.Name = self._camel_to_words(m.Id)
        m.Reading = 0.0
        m.ReadingUnits = self._get_unit_by_sensor_id(m.Id)
        m.odata_id = f"/redfish/v1/Chassis/{chassis_id}/Sensors/{sensor_name}"

        # to be continue
        # url = "http://127.0.0.1:5001/api/v1/cdu/status/sensor_value"
        # response = self.send_get(url)
        # response.json()['coolant_flow_rate']

        return m.model_dump(by_alias=True)

    def _get_unit_by_sensor_id(self, sensor_id: str) -> str:
        id_readingUnit_map = {
            "PrimaryFlowLitersPerMinute": "L/min",
            "PrimaryHeatRemovedkW": "kW",
            "PrimarySupplyTemperatureCelsius": "Celsius",
            "PrimaryReturnTemperatureCelsius": "Celsius",
            "PrimaryDeltaTemperatureCelsius": "Celsius",
            "PrimarySupplyPressurekPa": "kPa",
            "PrimaryReturnPressurekPa": "kPa",
            "PrimaryDeltaPressurekPa": "kPa",
            "TemperatureCelsius": "Celsius",
            "DewPointCelsius": "Celsius",
            "HumidityPercent": "Percent",
            "WaterPH": "pH",
            "Conductivity": "μs/cm",
            "Turbidity": "NTU",
            "PowerConsume": "kW",
        }
        return id_readingUnit_map.get(sensor_name, "")
    
    def _camel_to_words(name: str) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', name)
