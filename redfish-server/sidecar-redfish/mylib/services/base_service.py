import os, re
from cachetools import cached, LRUCache, TTLCache
from mylib.utils.HttpRequestUtil import HttpRequestUtil
from mylib.utils.StatusUtil import StatusUtil
from werkzeug.exceptions import HTTPException, BadRequest
from flask import abort
import subprocess
from typing import Dict, List
from mylib.adapters.sensor_api_adapter import SensorAPIAdapter

class BaseService:

    @classmethod
    def exec_command(cls, linux_cmd: str) -> Dict[str, List[str]]:
        """
        執行Linux命令
        """
        process = subprocess.Popen(linux_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        stdout = stdout.decode("utf-8")
        stderr = stderr.decode("utf-8")

        return {
            "command": linux_cmd,
            "stdout_lines": stdout.splitlines(),
            "stderr_lines": stderr.splitlines()
        }

    @classmethod
    def send_get(cls, url, params={}):
        return HttpRequestUtil.send_get(url, params)

    @classmethod
    def send_get_as_json(cls, url, params={}):
        return HttpRequestUtil.send_get_as_json(url, params)

    @classmethod
    def send_post(cls, url, req_body, opts={}):
        return HttpRequestUtil.send_post(url, req_body, opts)

    @classmethod
    def send_post_as_json(cls, url, req_body, opts={}):
        return HttpRequestUtil.send_post_as_json(url, req_body, opts)

    @classmethod
    @cached(cache=TTLCache(maxsize=30, ttl=5))
    def _read_components_chassis_summary_from_cache(cls) -> dict:
        """
        @note api response from /api/v1/cdu/components/chassis/summary
            {
                "fan1": {
                    "status": {
                    "state": "Absent",
                    "health": "Critical"
                    },
                    "reading": 0,
                    "ServiceHours": 100,
                    "ServiceDate": 100,
                    "HardWareInfo": {}
                },
                ...
                "power12v2": {
                    "status": {
                    "state": "Absent",
                    "health": "Critical"
                    },
                    "reading": 0,
                    "ServiceHours": 100,
                    "ServiceDate": 100,
                    "HardWareInfo": {}
                },
                ...
            }
        """
        return SensorAPIAdapter.fetch_components_chassis_summary()

    @classmethod
    @cached(cache=TTLCache(maxsize=30, ttl=5))
    def _read_components_thermal_equipment_summary_from_cache(cls) -> dict:
        """
        @note api response from /api/v1/cdu/components/thermal_equipment/summary
            {
                "temperature_dew_point": {
                    "status": {
                        "state": "Disabled",
                        "health": "OK"
                    },
                    "reading": 0,
                    "ServiceHours": 100,
                    "ServiceDate": 100,
                    "HardWareInfo": {}
                },
                "leak_detector": {
                    "status": {
                        "state": "Enabled",
                        "health": "OK"
                    },
                    "reading": null,
                    "ServiceHours": 100,
                    "ServiceDate": 100,
                    "HardWareInfo": {}
                }, 
                ...
            }
        """
        return SensorAPIAdapter.fetch_components_thermal_equipment_summary()

    @classmethod
    @cached(cache=TTLCache(maxsize=30, ttl=5))
    def _read_sensor_value_from_cache(cls) -> dict:
        """
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
        # url = f"{os.environ['ITG_REST_HOST']}/api/v1/cdu/components/chassis/summary"
        url = f"{os.environ['ITG_REST_HOST']}/api/v1/cdu/status/sensor_value"
        response = cls.send_get(url)
        sensor_value_json = response.json()
        return sensor_value_json
    
    @classmethod
    @cached(cache=TTLCache(maxsize=3, ttl=5))
    def _read_getdata_from_webapp(cls) -> dict:
        """
        讀取webapp ui的/get_data api
        格式可參考 webUI/web/json/sensor_data.json
        """
        url = f"{os.environ['ITG_WEBAPP_HOST']}/get_data"
        response = cls.send_get(url)
        data_json = response.json()
        return data_json

    def _calc_delta_value(self, sensor_value: dict, fieldNameToFetchSensorValue: str ) -> float:
        """
        如果有兩欄(欄位含',')，則計算兩個sensor value的差值
        """
        if "," in fieldNameToFetchSensorValue: 
            fieldNames = fieldNameToFetchSensorValue.split(",")
            return sensor_value[ fieldNames[0] ]["reading"] - sensor_value[ fieldNames[1] ]["reading"]
        else:
            return sensor_value[ fieldNameToFetchSensorValue ]["reading"]

    def _calc_delta_value_status(self, sensor_value: dict, fieldNameToFetchSensorValue: str ) -> float:
        """
        如果有兩欄(欄位含',')，則計算兩個sensor value的差值
        """
        if "," in fieldNameToFetchSensorValue: 
            fieldNames = fieldNameToFetchSensorValue.split(",")
            status_list = sensor_value[ fieldNames[0] ]["status"], sensor_value[ fieldNames[1] ]["status"]
            # print("status_list: ", status_list)
            status = StatusUtil.get_worst_health_dict(status_list)
            # print("status: ", status)
            return sensor_value[ fieldNames[0] ]["reading"] - sensor_value[ fieldNames[1] ]["reading"], status
        else:
            return sensor_value[ fieldNameToFetchSensorValue ]["reading"], sensor_value[ fieldNameToFetchSensorValue ]["status"]        

    
    
    def _camel_to_words(self, name: str) -> str:
        """
        將 camelCase 轉換為 words
        Example:
            "TemperatureCelsius" -> "Temperature Celsius"
        """
        return re.sub(r'(?<!^)(?=[A-Z])', ' ', name)