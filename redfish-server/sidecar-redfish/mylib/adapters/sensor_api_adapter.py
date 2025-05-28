import os
from mylib.utils.HttpRequestUtil import HttpRequestUtil
from typing import Dict

"""
直接取得Sensor data資料的 (無cache)
@note: 以前的名字叫RestAPI，未來應該會改叫SensorAPI
"""
class SensorAPIAdapter:

    @classmethod
    def fetch_components_chassis_summary(cls) -> dict:
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
        url = f"{os.environ['ITG_REST_HOST']}/api/v1/cdu/components/chassis/summary"
        response = HttpRequestUtil.send_get(url, {})
        summary_json = response.json()
        return summary_json

    @classmethod
    def fetch_components_thermal_equipment_summary(cls) -> dict:
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
        url = f"{os.environ['ITG_REST_HOST']}/api/v1/cdu/components/thermal_equipment/summary"
        response = HttpRequestUtil.send_get(url, {})
        summary_json = response.json()
        return summary_json

    
    
    