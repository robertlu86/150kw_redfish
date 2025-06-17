import os
import json
import pytest
import sys
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from .conftest import print_response_details
from mylib.services.base_service import BaseService


"""
sensor_ids = [
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
]
"""
base_service_testcases = [
    { "input": "PrimaryHeatRemovedkW", "expected": "Primary Heat Removed kW" },
    { "input": "PrimarySupplyTemperatureCelsius", "expected": "Primary Supply Temperature Celsius" },
    { "input": "PrimaryReturnTemperatureCelsius", "expected": "Primary Return Temperature Celsius" },
    { "input": "PrimaryDeltaTemperatureCelsius", "expected": "Primary Delta Temperature Celsius" },
    { "input": "PrimarySupplyPressurekPa", "expected": "Primary Supply Pressure kPa" },
    { "input": "PrimaryReturnPressurekPa", "expected": "Primary Return Pressure kPa" },
    { "input": "PrimaryDeltaPressurekPa", "expected": "Primary Delta Pressure kPa" },
    { "input": "TemperatureCelsius", "expected": "Temperature Celsius" },
    { "input": "DewPointCelsius", "expected": "Dew Point Celsius" },
    { "input": "HumidityPercent", "expected": "Humidity Percent" },
    { "input": "WaterPH", "expected": "Water PH" },
    { "input": "Conductivity", "expected": "Conductivity" },
    { "input": "Turbidity", "expected": "Turbidity" },
    { "input": "PowerConsume", "expected": "Power Consume" },
]

@pytest.mark.parametrize('testcase', base_service_testcases)
def test_base_service__camel_to_words(client, basic_auth_header, testcase):
    """[TestCase] camel_to_words"""
    # response = client.get('/redfish')
    # print_response_details(response)
    bs = BaseService()
    output = None
    try:
        output = bs._camel_to_words(testcase["input"])
        assert output == testcase["expected"]
        print(f"PASS: input={testcase['input']}, expected={testcase['expected']}")
    except Exception as e:
        print(f"FAIL: input={testcase['input']}, expected={testcase['expected']}, actual={output}")
        raise e
            
