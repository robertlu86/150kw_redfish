import os
import json
import pytest
import sys
import logging
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mylib.adapters.hardware_info_adapter import HardwareInfoAdapter

def test_hardware_info_adapter_load_info(client):
    """[TestCase] 取得硬件資訊"""
    try: 
        info = HardwareInfoAdapter.load_info()
        logging.info(f"Hardware info: {info}")

        assert isinstance(info, dict) == True
        print("PASS: hardware info is a dict")
    
        assert info["CDU"]["SerialNumber"] != "TBD"
        print("PASS: SerialNumber is not TBD")
    except Exception as e:
        print(f"test_hardware_info_adapter_load_info error: {e}")
        raise e
    


