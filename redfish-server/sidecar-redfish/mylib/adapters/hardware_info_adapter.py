import os
from typing import Dict
import copy
from cachetools import cached, TTLCache
from load_env import hardware_info
from mylib.utils.HttpRequestUtil import HttpRequestUtil
from mylib.common.proj_error import ProjError
from mylib.adapters.webapp_api_adapter import WebAppAPIAdapter

"""
讀取 Hardware 資訊
"""
class HardwareInfoAdapter:
    @classmethod
    def load_info(cls) -> Dict:
        """Get hardware info"""
        info = copy.deepcopy(hardware_info)
        info["CDU"]["SerialNumber"] = cls._load_serial_number()
        return info

    @classmethod
    @cached(cache=TTLCache(maxsize=1, ttl=5))
    def _load_serial_number(cls) -> Dict:
        """Get serial number from webapp api
        @note api: /read_version
        """
        try:
            response = WebAppAPIAdapter().read_version()
            resp_json = response.json()
            return resp_json["FW_Info"]["SN"]
        except Exception as e:
            print(f"HardwareInfoAdapter _load_serial_number error: {e}")
            return "TBD"
    