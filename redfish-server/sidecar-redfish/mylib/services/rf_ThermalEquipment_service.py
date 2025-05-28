'''
這是Redfish的chassis service
'''
import os, re
from typing import Optional
from mylib.models.rf_sensor_model import (
    RfSensorCollectionModel, 
    RfSensorModel, 
)
from mylib.services.base_service import BaseService
from mylib.models.rf_environment_metrics_model import RfEnvironmentMetricsModel
from mylib.models.rf_leak_detector import RfLeakDetectorModel
from mylib.models.rf_status_model import RfStatusModel
from mylib.models.rf_primary_coolant_connector_model import RfPrimaryCoolantConnectorCollectionModel
from mylib.models.rf_cdu_model import RfCduModel, RfCduCollectionModel

from load_env import hardware_info

class RfThermalEquipmentService(BaseService):
    def fetch_CDUs(self, cdu_id: Optional[str] = None) -> dict:
        """
        對應 "/redfish/v1/ThermalEquipment/CDUs/1"

        :param cdu_id: str
        :return: dict
        """
        if cdu_id is None:
            m = RfCduCollectionModel()
        else:
            m = RfCduModel(
                cdu_id=cdu_id,
                **hardware_info["CDU"]
            )
            m.Status = {"State": "Enabled", "Health": "OK"}
            m.Oem = {}
            
        return m.to_dict()
    
    def fetch_CDUs_EnvironmentMetrics(self, cdu_id: str) -> dict:
        """
        對應 "/redfish/v1/ThermalEquipment/CDUs/1/EnvironmentMetrics"

        :param cdu_id: str
        :return: dict
        """
        m = RfEnvironmentMetricsModel(cdu_id=cdu_id)
        m.TemperatureCelsius["Reading"] = self._read_reading_value_by_sensor_id("TemperatureCelsius")
        m.DewPointCelsius["Reading"] = self._read_reading_value_by_sensor_id("DewPointCelsius")
        m.HumidityPercent["Reading"] = self._read_reading_value_by_sensor_id("HumidityPercent")
        m.AbsoluteHumidity["Reading"] = 0 or self._read_reading_value_by_sensor_id("AbsoluteHumidity")
        return m.to_dict()
    
    def fetch_CDUs_LeakDetection_LeakDetectors(self, cdu_id: str) -> dict:
        """
        對應 "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection/LeakDetectors"
        Response Example:
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection/LeakDetectors",
            "@odata.type": "#LeakDetectors.v1_3_0.LeakDetectors",
            "Id": "1",
            "Name": "LeakDetectors",
            "Status": {
                "State": "Enabled",
                "Health": "Critical"
            },
        }

        :param cdu_id: str
        """
        m = RfLeakDetectorModel(cdu_id=cdu_id)
        # m.Status = self._read_leak_detector_status()
        return m.to_dict()


    def _read_reading_value_by_sensor_id(self, sensor_id: str) -> float:
        """
        @return Reading & ReadingUnits
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
            sensor_value_json = self._read_components_chassis_summary_from_cache()
            reading_info["Reading"] = self._calc_delta_value(sensor_value_json, reading_info["fieldNameToFetchSensorValue"])
        else:
            reading_info["Reading"] = 0.0
        return reading_info["Reading"]
    
    def _read_leak_detector_status(self) -> RfStatusModel:
        """
        目前的設計：UI會讀web app的/get_data，js判斷如下
            if (data["error"]["leakage1_broken"]) {
                $("#leakage1")
                    .css("color", "red")
                    .text("Broken");
            } else if (
                !data["error"]["leakage1_broken"] &&
                data["error"]["leakage1_leak"]
            ) {
                $("#leakage1").css("color", "red").text("Leak");
            } else {
                $("#leakage1").css("color", "black").text("OK");
            }
        以上直接去讀 {project_root}/webUI/web/json/sensor_data.json的`error`欄位
        (註) 20250505 如果未來webUI和redfish佈署在不同機器，直接讀json檔是不通的。
        (註) 20250509 改統一由RestAPI取資料
        """
        ret_status_model = None
        try:
            summary_json = self._read_components_thermal_equipment_summary_from_cache()
            leak_detector_info = summary_json["leak_detector"]
            ret_status_model = RfStatusModel.from_dict(leak_detector_info["status"])
        except Exception as e:
            print(e)
            ret_status_model = RfStatusModel.from_dict({"State": "Disabled", "Health": "Critical"})
        return ret_status_model
            
    def _read_oem_by_cdu_id(self, cdu_id: str):
        return self._read_components_thermal_equipment_summary_from_cache().get("Oem")
        
    
    def fetch_CDUs_PrimaryCoolantConnectors(self, cdu_id: str) -> dict:
        """
        對應 "/ThermalEquipment/CDUs/1/PrimaryCoolantConnectors"

        :param cdu_id: str
        :return: dict
        """
        m = RfPrimaryCoolantConnectorCollectionModel(cdu_id=cdu_id)
        return m.to_dict()