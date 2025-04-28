from dotenv import load_dotenv
from flask import Flask, request,Response
from flask_restx import Api, Resource, fields, Namespace, reqparse
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Endian
from collections import OrderedDict
from pymodbus.payload import BinaryPayloadDecoder
import os
from concurrent_log_handler import ConcurrentTimedRotatingFileHandler
import logging
from pymodbus.payload import BinaryPayloadBuilder
import struct
import json
import zipfile
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
import requests
import time
log_path = os.path.dirname(os.getcwd())
json_path = f"{log_path}/webUI/web/json"
from functools import wraps
from typing import Any, Dict
from mylib.services.rf_chassis_service import RfChassisService



# -------------- 取得資料 --------------
def load_raw_from_api(
    url: str,
    params: Dict[str, Any] = None,
    timeout: float = 5.0
) -> Dict:
    """
    從本機 API 拿回整張 JSON 並轉成 dict
    """
    resp = requests.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

# curl資料
CDU_BASE = "http://192.168.3.137:5001"
sensor_value = f"{CDU_BASE}/api/v1/cdu/status/sensor_value"
sensor_value_all = load_raw_from_api(sensor_value)


app = Flask(__name__)
api = Api(app, version="0.6.6", title="CDU API", description="API for CDU system")


# limiter = Limiter(
#     key_func=get_remote_address,
#     default_limits=["10 per second"],
#     app=app,
# )

# default_ns = Namespace("api/v1", description="api for CDU system")
redfish_ns = Namespace("redfish/v1", description="redfish api for CDU system")
log_dir = f"{log_path}/RestAPI/logs/operation"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)



def check_auth(username, password):
    """檢查是否為有效的用戶名和密碼"""
    return username == "admin" and password == "admin"


def authenticate():
    """請求身份驗證"""
    return Response(
        "Authentication required.",
        401,
        {"WWW-Authenticate": "Basic realm='Login Required'"},
    )


def requires_auth(f):
    """裝飾器，要求路由使用基本驗證"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated_function

file_name = "oplog_api.log"
log_file = os.path.join(log_dir, file_name)

oplog_handler = ConcurrentTimedRotatingFileHandler(
    log_file,
    when="midnight",
    backupCount=1100,
    encoding="UTF-8",
    delay=False,
)
oplog_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
oplog_handler.setFormatter(formatter)
op_logger = logging.getLogger("custom_restapi")
op_logger.setLevel(logging.INFO)
op_logger.addHandler(oplog_handler)

modbus_host = "192.168.3.250"
# modbus_host = "127.0.0.1"
modbus_port = 502
modbus_slave_id = 1

op_mode = {"mode": "stop"}
pump_speed_set = {"pump1_speed": 0, "pump2_speed": 0, "pump3_speed": 0}
fan_speed_set = {
    "fan1_speed": 0,
    "fan2_speed": 0,
    "fan3_speed": 0,
    "fan4_speed": 0,
    "fan5_speed": 0,
    "fan6_speed": 0,
    "fan7_speed": 0,
    "fan8_speed": 0,
}
temp_set = {"temp_set": 0}
pressure_set = {"pressure_set": 0}
fan_set = {"fan_set": 0}
pump_swap_time = {"pump_swap_time": 0}
unit_set = {"unit": "Metric"}
thrshd = {}
ctr_data = {}
measure_data = {}

data = {
    "sensor_value": {
        "temp_clntSply": 0,
        "temp_clntSplySpare": 0,
        "temp_clntRtn": 0,
        "temp_clntRtnSpare": 0,
        "prsr_clntSply": 0,
        "prsr_clntSplySpare": 0,
        "prsr_clntRtn": 0,
        "prsr_clntRtnSpare": 0,
        "prsr_fltIn": 0,
        "prsr_fltOut": 0,
        "clnt_flow": 0,
        "ambient_temp": 0,
        "relative_humid": 0,
        "dew_point": 0,
        "pH": 0,
        "cdct": 0,
        "tbd": 0,
        "power": 0,
        "AC": 0,
        "inv1_freq": 0,
        "inv2_freq": 0,
        "inv3_freq": 0,
        "heat_capacity": 0,
        "fan_freq1": 0,
        "fan_freq2": 0,
        "fan_freq3": 0,
        "fan_freq4": 0,
        "fan_freq5": 0,
        "fan_freq6": 0,
        "fan_freq7": 0,
        "fan_freq8": 0,
    },
    "unit": {
        "temperature": "celcius",
        "pressure": "bar",
        "flow": "LPM",
        "power": "kW",
        "heat_capacity": "kW",
    },
    "fan_speed": {
        "fan1_speed": 0,
        "fan2_speed": 0,
        "fan3_speed": 0,
        "fan4_speed": 0,
        "fan5_speed": 0,
        "fan6_speed": 0,
        "fan7_speed": 0,
        "fan8_speed": 0,
    },
    "pump_speed": {
        "pump1_speed": 0, 
        "pump2_speed": 0, 
        "pump3_speed": 0,
    },
    "pump_service_hours": {
        "pump1_service_hours": 0,
        "pump2_service_hours": 0,
        "pump3_service_hours": 0,
    },
    "pump_state": {
        "pump1_state": "Enable",
        "pump2_state": "Disable",
        "pump3_state": "Disable",
    },
    "pump_health": {
        "pump1_health": "OK",
        "pump2_health": "Critical",
        "pump3_health": "Critical",
    },
}

messages = {
    "warning": {
        "M100": ["Coolant Supply Temperature Over Range (High) Warning (T1)", False],
        "M101": [
            "Coolant Supply Temperature Spare Over Range (High) Warning (T1sp)",
            False,
        ],
        "M102": ["Coolant Return Temperature Over Range (High) Warning (T2)", False],
        "M103": [
            "Coolant Return Temperature Over Range Spare (High) Warning (T2sp)",
            False,
        ],
        "M104": ["Coolant Supply Pressure Over Range (High) Warning (P1)", False],
        "M105": [
            "Coolant Supply Pressure Spare Over Range (High) Warning (P1sp)",
            False,
        ],
        "M106": ["Coolant Return Pressure Over Range (High) Warning (P2)", False],
        "M107": [
            "Coolant Return Pressure Spare Over Range (High) Warning (P2sp)",
            False,
        ],
        "M108": ["Filter Inlet Pressure Over Range (Low) Warning (P3)", False],
        "M109": ["Filter Inlet Pressure Over Range (High) Warning (P3)", False],
        "M110": ["Filter Outlet Pressure Over Range (High) Warning (P4)", False],
        "M111": ["Coolant Flow Rate (Low) Warning (F1)", False],
        "M112": ["Ambient Temperature Over Range (Low) Warning (T a)", False],
        "M113": ["Ambient Temperature Over Range (High) Warning (T a)", False],
        "M114": ["Relative Humidity Over Range (Low) Warning (RH)", False],
        "M115": ["Relative Humidity Over Range (High) Warning (RH)", False],
        "M116": ["Condensation Warning (T Dp)", False],
        "M117": ["pH Over Range (Low) Warning (PH)", False],
        "M118": ["pH Over Range (High) Warning (PH)", False],
        "M119": ["Conductivity Over Range (Low) Warning (CON)", False],
        "M120": ["Conductivity Over Range (High) Warning (CON)", False],
        "M121": ["Turbidity Over Range (Low) Warning (Tur)", False],
        "M122": ["Turbidity Over Range (High) Warning (Tur)", False],
        "M123": ["Average Current Over Range (High) Warning", False],
    },
    "alert": {
        "M200": ["Coolant Supply Temperature Over Range (High) Alert (T1)", False],
        "M201": [
            "Coolant Supply Temperature Spare Over Range (High) Alert (T1sp)",
            False,
        ],
        "M202": ["Coolant Return Temperature Over Range (High) Alert (T2)", False],
        "M203": [
            "Coolant Return Temperature Over Range Spare (High) Alert (T2sp)",
            False,
        ],
        "M204": ["Coolant Supply Pressure Over Range (High) Alert (P1)", False],
        "M205": ["Coolant Supply Pressure Spare Over Range (High) Alert (P1sp)", False],
        "M206": ["Coolant Return Pressure Over Range (High) Alert (P2)", False],
        "M207": ["Coolant Return Pressure Spare Over Range (High) Alert (P2sp)", False],
        "M208": ["Filter Inlet Pressure Over Range (Low) Alert (P3)", False],
        "M209": ["Filter Inlet Pressure Over Range (High) Alert (P3)", False],
        "M210": ["Filter Outlet Pressure Over Range (High) Alert (P4)", False],
        "M211": ["Coolant Flow Rate (Low) Alert (F1)", False],
        "M212": ["Ambient Temperature Over Range (Low) Alert (T a)", False],
        "M213": ["Ambient Temperature Over Range (High) Alert (T a)", False],
        "M214": ["Relative Humidity Over Range (Low) Alert (RH)", False],
        "M215": ["Relative Humidity Over Range (High) Alert (RH)", False],
        "M216": ["Condensation Alert (T Dp)", False],
        "M217": ["pH Over Range (Low) Alert (PH)", False],
        "M218": ["pH Over Range (High) Alert (PH)", False],
        "M219": ["Conductivity Over Range (Low) Alert (CON)", False],
        "M220": ["Conductivity Over Range (High) Alert (CON)", False],
        "M221": ["Turbidity Over Range (Low) Alert (Tur)", False],
        "M222": ["Turbidity Over Range (High) Alert (Tur)", False],
        "M223": ["Average Current Over Range (High) Alert", False],
    },
    "error": {
        "M300": ["Coolant Pump1 Inverter Overload", False],
        "M301": ["Coolant Pump2 Inverter Overload", False],
        "M302": ["Coolant Pump3 Inverter Overload", False],
        "M303": ["Fan1 Inverter Overload", False],
        "M304": ["Fan2 Inverter Overload", False],
        "M305": ["Coolant Pump1 Inverter Error", False],
        "M306": ["Coolant Pump2 Inverter Error", False],
        "M307": ["Coolant Pump3 Inverter Error", False],
        "M308": ["Factory Power Status", False],
        "M309": ["Inverter1 Communication Error", False],
        "M310": ["Inverter2 Communication Error", False],
        "M311": ["Inverter3 Communication Error", False],
        "M312": ["Coolant Flow (F1) Meter Communication Error", False],
        "M313": ["Ambient Sensor (Ta) Communication Error", False],
        "M314": ["Relative Humidity (RH) Communication Error", False],
        "M315": ["Dew Point Temperature (TDp) Communication Error", False],
        "M316": ["pH (PH) Sensor Communication Error", False],
        "M317": ["Conductivity (CON) Sensor Communication Error", False],
        "M318": ["Turbidity (Tur) Sensor Communication Error", False],
        "M319": ["ATS 1 Communication Error", False],
        "M320": ["ATS 2 Communication Error", False],
        "M321": ["Power Meter Communication Error", False],
        "M322": ["Average Current Communication Error", False],
        "M323": ["Fan 1 Communication Error", False],
        "M324": ["Fan 2 Communication Error", False],
        "M325": ["Fan 3 Communication Error", False],
        "M326": ["Fan 4 Communication Error", False],
        "M327": ["Fan 5 Communication Error", False],
        "M328": ["Fan 6 Communication Error", False],
        "M329": ["Fan 7 Communication Error", False],
        "M330": ["Fan 8 Communication Error", False],
        "M331": ["Coolant Supply Temperature (T1) Broken Error", False],
        "M332": ["Coolant Supply Temperature Spare (T1sp) Broken Error", False],
        "M333": ["Coolant Return Temperature (T2) Broken Error", False],
        "M334": ["Coolant Return Temperature Spare (T2sp) Broken Error", False],
        "M335": ["Coolant Supply Pressure (P1) Broken Error", False],
        "M336": ["Coolant Supply Pressure Spare (P1sp) Broken Error", False],
        "M337": ["Coolant Return Pressure (P2) Broken Error", False],
        "M338": ["Coolant Return Pressure Spare (P2sp) Broken Error", False],
        "M339": ["Filter Inlet Pressure (P3) Broken Error", False],
        "M340": ["Filter Outlet Pressure (P4) Broken Error", False],
        "M341": ["Coolant Flow Rate (F1) Broken Error", False],
        "M342": ["PC1 Error", False],
        "M343": ["PC2 Error", False],
        "M344": ["Leakage 1 Leak Error", False],
        "M345": ["Leakage 1 Broken Error", False],
        "M346": ["Coolant Level 1 Error", False],
        "M347": ["Coolant Level 2 Error", False],
        "M348": ["Coolant Level 3 Error", False],
        "M349": ["24V Power Supply 1 Error", False],
        "M350": ["24V Power Supply 2 Error", False],
        "M351": ["12V Power Supply 1 Error", False],
        "M352": ["12V Power Supply 2 Error", False],
        "M353": ["Main MC Status Error", False],
        "M354": ["FAN 1 Alarm Status Error", False],
        "M355": ["FAN 2 Alarm Status Error", False],
        "M356": ["FAN 3 Alarm Status Error", False],
        "M357": ["FAN 4 Alarm Status Error", False],
        "M358": ["FAN 5 Alarm Status Error", False],
        "M359": ["FAN 6 Alarm Status Error", False],
        "M360": ["FAN 7 Alarm Status Error", False],
        "M361": ["FAN 8 Alarm Status Error", False],
        "M362": ["Stop Due to Low Coolant Level", False],
        "M363": ["PLC Communication Broken Error", False],
    },
    "rack": {
        "M400": ["Rack1 broken", False],
        "M401": ["Rack2 broken", False],
        "M402": ["Rack3 broken", False],
        "M403": ["Rack4 broken", False],
        "M404": ["Rack5 broken", False],
        "M405": ["Rack6 broken", False],
        "M406": ["Rack7 broken", False],
        "M407": ["Rack8 broken", False],
        "M408": ["Rack9 broken", False],
        "M409": ["Rack10 broken", False],
        "M410": ["Rack1 leakage", False],
        "M411": ["Rack2 leakage", False],
        "M412": ["Rack3 leakage", False],
        "M413": ["Rack4 leakage", False],
        "M414": ["Rack5 leakage", False],
        "M415": ["Rack6 leakage", False],
        "M416": ["Rack7 leakage", False],
        "M417": ["Rack8 leakage", False],
        "M418": ["Rack9 leakage", False],
        "M419": ["Rack10 leakage", False],
        "M420": ["Rack1 error", False],
        "M421": ["Rack2 error", False],
        "M422": ["Rack3 error", False],
        "M423": ["Rack4 error", False],
        "M424": ["Rack5 error", False],
        "M425": ["Rack6 error", False],
        "M426": ["Rack7 error", False],
        "M427": ["Rack8 error", False],
        "M428": ["Rack9 error", False],
        "M429": ["Rack10 error", False],
    },
}

system_data = {
    "value": {
        "unit": "metric",
        "last_unit": "metric",
    }
}

sensor_thrshd = {
    "Thr_W_CoolantSupplyTemperature_H": 0,
    "Thr_W_Rst_CoolantSupplyTemperature_H": 0,
    "Thr_A_CoolantSupplyTemperature_H": 0,
    "Thr_A_Rst_CoolantSupplyTemperature_H": 0,
    "Thr_W_CoolantSupplyTemperatureSpare_H": 0,
    "Thr_W_Rst_CoolantSupplyTemperatureSpare_H": 0,
    "Thr_A_CoolantSupplyTemperatureSpare_H": 0,
    "Thr_A_Rst_CoolantSupplyTemperatureSpare_H": 0,
    "Thr_W_CoolantReturnTemperature_H": 0,
    "Thr_W_Rst_CoolantReturnTemperature_H": 0,
    "Thr_A_CoolantReturnTemperature_H": 0,
    "Thr_A_Rst_CoolantReturnTemperature_H": 0,
    "Thr_W_CoolantReturnTemperatureSpare_H": 0,
    "Thr_W_Rst_CoolantReturnTemperatureSpare_H": 0,
    "Thr_A_CoolantReturnTemperatureSpare_H": 0,
    "Thr_A_Rst_CoolantReturnTemperatureSpare_H": 0,
    "Thr_W_CoolantSupplyPressure_H": 0,
    "Thr_W_Rst_CoolantSupplyPressure_H": 0,
    "Thr_A_CoolantSupplyPressure_H": 0,
    "Thr_A_Rst_CoolantSupplyPressure_H": 0,
    "Thr_W_CoolantSupplyPressureSpare_H": 0,
    "Thr_W_Rst_CoolantSupplyPressureSpare_H": 0,
    "Thr_A_CoolantSupplyPressureSpare_H": 0,
    "Thr_A_Rst_CoolantSupplyPressureSpare_H": 0,
    "Thr_W_CoolantReturnPressure_H": 0,
    "Thr_W_Rst_CoolantReturnPressure_H": 0,
    "Thr_A_CoolantReturnPressure_H": 0,
    "Thr_A_Rst_CoolantReturnPressure_H": 0,
    "Thr_W_CoolantReturnPressureSpare_H": 0,
    "Thr_W_Rst_CoolantReturnPressureSpare_H": 0,
    "Thr_A_CoolantReturnPressureSpare_H": 0,
    "Thr_A_Rst_CoolantReturnPressureSpare_H": 0,
    "Thr_W_FilterInletPressure_L": 0,
    "Thr_W_Rst_FilterInletPressure_L": 0,
    "Thr_A_FilterInletPressure_L": 0,
    "Thr_A_Rst_FilterInletPressure_L": 0,
    "Thr_W_FilterInletPressure_H": 0,
    "Thr_W_Rst_FilterInletPressure_H": 0,
    "Thr_A_FilterInletPressure_H": 0,
    "Thr_A_Rst_FilterInletPressure_H": 0,
    "Thr_W_FilterOutletPressure_H": 0,
    "Thr_W_Rst_FilterOutletPressure_H": 0,
    "Thr_A_FilterOutletPressure_H": 0,
    "Thr_A_Rst_FilterOutletPressure_H": 0,
    "Thr_W_CoolantFlowRate_L": 0,
    "Thr_W_Rst_CoolantFlowRate_L": 0,
    "Thr_A_CoolantFlowRate_L": 0,
    "Thr_A_Rst_CoolantFlowRate_L": 0,
    "Thr_W_AmbientTemp_L": 0,
    "Thr_W_Rst_AmbientTemp_L": 0,
    "Thr_A_AmbientTemp_L": 0,
    "Thr_A_Rst_AmbientTemp_L": 0,
    "Thr_W_AmbientTemp_H": 0,
    "Thr_W_Rst_AmbientTemp_H": 0,
    "Thr_A_AmbientTemp_H": 0,
    "Thr_A_Rst_AmbientTemp_H": 0,
    "Thr_W_RelativeHumid_L": 0,
    "Thr_W_Rst_RelativeHumid_L": 0,
    "Thr_A_RelativeHumid_L": 0,
    "Thr_A_Rst_RelativeHumid_L": 0,
    "Thr_W_RelativeHumid_H": 0,
    "Thr_W_Rst_RelativeHumid_H": 0,
    "Thr_A_RelativeHumid_H": 0,
    "Thr_A_Rst_RelativeHumid_H": 0,
    "Thr_W_DewPoint_L": 0,
    "Thr_W_Rst_DewPoint_L": 0,
    "Thr_A_DewPoint_L": 0,
    "Thr_A_Rst_DewPoint_L": 0,
    "Thr_W_pH_L": 0,
    "Thr_W_Rst_pH_L": 0,
    "Thr_A_pH_L": 0,
    "Thr_A_Rst_pH_L": 0,
    "Thr_W_pH_H": 0,
    "Thr_W_Rst_pH_H": 0,
    "Thr_A_pH_H": 0,
    "Thr_A_Rst_pH_H": 0,
    "Thr_W_Conductivity_L": 0,
    "Thr_W_Rst_Conductivity_L": 0,
    "Thr_A_Conductivity_L": 0,
    "Thr_A_Rst_Conductivity_L": 0,
    "Thr_W_Conductivity_H": 0,
    "Thr_W_Rst_Conductivity_H": 0,
    "Thr_A_Conductivity_H": 0,
    "Thr_A_Rst_Conductivity_H": 0,
    "Thr_W_Turbidity_L": 0,
    "Thr_W_Rst_Turbidity_L": 0,
    "Thr_A_Turbidity_L": 0,
    "Thr_A_Rst_Turbidity_L": 0,
    "Thr_W_Turbidity_H": 0,
    "Thr_W_Rst_Turbidity_H": 0,
    "Thr_A_Turbidity_H": 0,
    "Thr_A_Rst_Turbidity_H": 0,
    "Thr_W_AverageCurrent_H": 0,
    "Thr_W_Rst_AverageCurrent_H": 0,
    "Thr_A_AverageCurrent_H": 0,
    "Thr_A_Rst_AverageCurrent_H": 0,
}

# fan_speed_model = default_ns.model(
#     "FanSpeed",
#     {
#         "fan_speed": fields.Integer(
#             description="Fan speed", example=50, min=0, max=100
#         ),
#     },
# )

# pressure_set_model = default_ns.model(
#     "PressureSet",
#     {
#         "pressure_set": fields.Float(
#             required=True, description="The pressure setting", example=1.2
#         )
#     },
# )

# pump1_speed_model = default_ns.model(
#     "PumpSpeed",
#     {
#         "pump_speed": fields.Integer(
#             description="Pump speed", example=50, min=0, max=100
#         ),
#         "pump_switch": fields.Boolean(description="Pump switch", example=True),
#     },
# )

# pump2_speed_model = default_ns.model(
#     "PumpSpeed",
#     {
#         "pump_speed": fields.Integer(
#             description="Pump speed", example=50, min=0, max=100
#         ),
#         "pump_switch": fields.Boolean(description="Pump switch", example=True),
#     },
# )

# pump3_speed_model = default_ns.model(
#     "PumpSpeed",
#     {
#         "pump_speed": fields.Integer(
#             description="Pump speed", example=50, min=0, max=100
#         ),
#         "pump_switch": fields.Boolean(description="Pump switch", example=True),
#     },
# )

# pump_swap_time_model = default_ns.model(
#     "PumpSwapTime",
#     {
#         "pump_swap_time": fields.Integer(
#             description="Time interval for pump swapping in minutes",
#             example=60,
#             min=0,
#             max=30000,
#         )
#     },
# )

# temp_set_model = default_ns.model(
#     "TempSet",
#     {
#         "temp_set": fields.Integer(
#             required=True,
#             description="The temperature setting 35-55 deg celcius",
#             example=40,
#         )
#     },
# )

# op_mode_model = default_ns.model(
#     "OpMode",
#     {
#         # auto
#         "mode": fields.String(required=True, description="The operational mode", example="stop", enum=["stop", "manual", "auto"]),
#         "temp_set": fields.Float(required=False, description="set temperature (manual only)", example="50"),
#         "pressure_set": fields.Float(required=False, description="set pressure (manual only)", example="10"),
#         "pump_swap_time": fields.Integer(required=False, description="set pump_swap_time (manual only)", example="100"),
#         # manual
#         "pump_speed": fields.Integer(required=False, description="set pump speed (manual only)", example="50"),
#         "pump1_switch": fields.Boolean(required=False, description="set pump1 switch (manual only)", example="true"),
#         "pump2_switch": fields.Boolean(required=False, description="set pump2 switch (manual only)", example="true"),
#         "pump3_switch": fields.Boolean(required=False, description="set pump3 switch (manual only)", example="true"),
#         "fan_speed": fields.Integer(required=False, description="set fan speed (manual only)", example="30"),
#         "fan1_switch": fields.Boolean(required=False, description="set fan1 switch (manual only)", example="true"),
#         "fan2_switch": fields.Boolean(required=False, description="set fan2 switch (manual only)", example="true"),
#         "fan3_switch": fields.Boolean(required=False, description="set fan3 switch (manual only)", example="true"),
#         "fan4_switch": fields.Boolean(required=False, description="set fan4 switch (manual only)", example="true"),
#         "fan5_switch": fields.Boolean(required=False, description="set fan5 switch (manual only)", example="true"),
#         "fan6_switch": fields.Boolean(required=False, description="set fan6 switch (manual only)", example="true"),
#         "fan7_switch": fields.Boolean(required=False, description="set fan7 switch (manual only)", example="true"),
#         "fan8_switch": fields.Boolean(required=False, description="set fan8 switch (manual only)", example="true"),
#     },
# )

# unit_set_model = default_ns.model(
#     "UnitSet",
#     {
#         "unit_set": fields.String(
#             required=True,
#             description="The unit setting",
#             example="metric",
#             enum=["metric", "imperial"],
#         )
#     },
# )

# # set temp
# def set_temperature():
#     temp_set = api.payload.get("temp_set")
#     # 檢查輸入
#     if not isinstance(temp_set, (int, float, type(None))):
#         return False, invalid_type()
#     unit = read_unit()
#     upLmt = 131 if unit == "imperial" else 55
#     lowLmt = 95 if unit == "imperial" else 35
#     try:
#         with ModbusTcpClient(host=modbus_host, port=modbus_port, unit=modbus_slave_id) as client:

#             if temp_set is None:
#                 read_data = client.read_holding_registers(226, 2)
#                 temp_set = cvt_registers_to_float(read_data.registers[0], read_data.registers[1])
#                 return True, temp_set

#             if lowLmt <= temp_set <= upLmt:
#                 word1, word2 = cvt_float_byte(float(temp_set))
#                 client.write_registers(993, [word2, word1])
#                 client.write_registers(226, [word2, word1])
#                 op_logger.info(f"Temperature updated successfully.{temp_set}")
#                 return True, temp_set
#             else:
#                 return False, f"Invalid temperature range: {lowLmt}~{upLmt}"
            
        
#     except Exception as e:
#         print(f"[Modbus Error] {e}")
#         return False, "Modbus write failed"
                


# # set prsr
# def set_pressure_value():
#     pressure_set = api.payload.get("pressure_set")
#     # 檢查輸入
#     if not isinstance(pressure_set, (int, float, type(None))):
#         return False, invalid_type()
#     unit = read_unit()
#     if unit == "imperial":
#         upLmt = 108.75
#         lowLmt = 0
#     else:
#         upLmt = 750
#         lowLmt = 0
        
#     try:
#         with ModbusTcpClient(host=modbus_host, port=modbus_port, unit=modbus_slave_id) as client:
#             if pressure_set is None:
#                 read_data = client.read_holding_registers(224, 2)
#                 pressure_set = cvt_registers_to_float(read_data.registers[0], read_data.registers[1])
#                 return True, pressure_set
            
#             if not (lowLmt <= pressure_set <= upLmt):
#                 if unit == "imperial":
#                     return False, ("Invalid pressure. Pressure must be between 0 and 108.")
#                 else:
#                     return False, ("Invalid pressure. Pressure must be between 0 and 750.")
#             else:
#                 word1, word2 = cvt_float_byte(float(pressure_set))
#                 client.write_registers(991, [word2, word1])
#                 client.write_registers(224, [word2, word1])
#                 op_logger.info(f"Pressure update successfully. {pressure_set}")
#                 return True, round(pressure_set, 2)

#     except Exception as e:
#         print(f"write pressure_set: {e}")
#         return False, plc_error()

# # set pump swap time
# def set_pump_swap_time():
#     pump_swap_time = api.payload.get("pump_swap_time")
#     if not isinstance(pump_swap_time, (int, float, type(None))):
#         return False, invalid_type()
#     try:
#         with ModbusTcpClient(host=modbus_host, port=modbus_port, unit=modbus_slave_id) as client:
#             if pump_swap_time is None:
#                 read_data = client.read_holding_registers(303, 2)
#                 pump_swap_time = cvt_registers_to_float(read_data.registers[0], read_data.registers[1])
#                 return True, pump_swap_time
#             if 0 < pump_swap_time <= 30000:
#                 word1, word2 = cvt_float_byte(pump_swap_time)
#                 client.write_registers(303, [word2, word1])
#                 op_logger.info(f"Pump swap time updated successfully. {pump_swap_time}")
#                 return True, pump_swap_time
#             else:
#                 return False, ("Invalid value. Time interval must be between 0 and 30000.")
#     except Exception as e:
#         print(f"write pump swap: {e}")
#         return False, plc_error()    
   
# # set pump speed & switch
# def set_pump_speed():
#     data = api.payload
#     pump_speed = data.get("pump_speed")
#     pump1_switch = data.get("pump1_switch")
#     pump2_switch = data.get("pump2_switch")
#     pump3_switch = data.get("pump3_switch")

#     try:
#         # 檢查輸入
#         if not isinstance(pump_speed, (int, type(None))):
#             return False, invalid_type()
        
#         if not all(isinstance(x, (bool, type(None))) for x in [pump1_switch, pump2_switch, pump3_switch]):
#             return False, invalid_type()

#         sensor = read_sensor_data()
#         ctr = read_ctr_data()
#         with ModbusTcpClient(host=modbus_host, port=modbus_port, unit=modbus_slave_id) as client:
#             # 判斷是否有更改(無的話讀原本的值)
#             if pump_speed is None:
#                 read_data = client.read_holding_registers(246, 2)
#                 if read_data.isError():
#                     return False, {"message": "Failed to read pump speed from Modbus."}
#                 pump_speed = cvt_registers_to_float(read_data.registers[0], read_data.registers[1])
#             # 區域判斷
#             if (0 < pump_speed < 25) or (pump_speed > 100):
#                 op_logger.info(f"Invalid pump speed input. Accepted values are 25-100 or 0.")
#                 return False, ({
#                     "message": "Invalid pump speed input. Accepted values are 25-100 or 0."
#                 }, 400)
#             result = {
#                 "pump_speed": pump_speed,
#                 "pump1_switch": pump1_switch,
#                 "pump2_switch": pump2_switch,
#                 "pump3_switch": pump3_switch,
#             }
#             # 輪流檢查
#             for pump_id, switch in zip([1, 2, 3], [pump1_switch, pump2_switch, pump3_switch]):
#                 error = sensor["error"].get(f"Inv{pump_id}_Error", False)
#                 overload = sensor["error"].get(f"Inv{pump_id}_OverLoad", False)
#                 mc = ctr["mc"].get(f"resultMC{pump_id}", False)
#                 # local test
#                 # error = True
#                 # overload = False
#                 # mc = True
                
#                 if switch: # 檢查(inv, overload)
#                     if error: # fail
#                         op_logger.info(f"Failed to activate due to Inverter{pump_id} error.")
#                         return False,{
#                             "message": f"Failed to activate due to Inverter{pump_id} error.",
#                         } 
#                     elif overload:
#                         op_logger.info(f"Failed to activate due to Inverter{pump_id} overload.")
#                         return False,{
#                             "message": f"Failed to activate due to Inverter{pump_id} overload.",
#                         } 
#                     elif not mc:
#                         op_logger.info(f"Failed to activate due to Inverter MC{pump_id}.")
#                         return False,{
#                             "message": f"Failed to activate due to Inverter MC{pump_id}.",
#                         } 
#                     else: # success
#                         set_p_check(pump_id - 1, [switch])
#                         op_logger.info(f"switch{pump_id} updated successfully. switch{pump_id}{switch}")
#                 elif switch is None:
#                         read_data = client.read_coils((8192 + 820 + pump_id - 1), 1, unit=modbus_slave_id)
#                         switch = read_data.bits[0]
#                         result[f"pump{pump_id}_switch"] = switch
#                 else: # 0
#                     set_p_check(pump_id- 1, [switch])    
#                     op_logger.info(f"switch{pump_id} updated successfully. switch{pump_id}{switch}") 
            
#                 # pump_speed存入
#                 if pump_speed > 0:
#                         set_ps(pump_speed)
#                         op_logger.info(f"pump{pump_id} speed updated successfully. pump speed {pump_speed}")
#                 else:
#                     set_ps(0)
#                     op_logger.info(f"pump{pump_id} speed updated successfully. pump speed {pump_speed}")
#             return True, result

#     except Exception as e:
#         print(f"write pump speed error: {e}")
#         return False, plc_error()
   
# # set fan speed & switch
# def set_fan_speed():
#     data = api.payload
#     fan_speed = data.get("fan_speed")
#     fan1_switch = data.get("fan1_switch")
#     fan2_switch = data.get("fan2_switch")
#     fan3_switch = data.get("fan3_switch")
#     fan4_switch = data.get("fan4_switch")
#     fan5_switch = data.get("fan5_switch")
#     fan6_switch = data.get("fan6_switch")
#     fan7_switch = data.get("fan7_switch")
#     fan8_switch = data.get("fan8_switch")

#     # 初始化回傳資料
#     fan_switch_result = {
#         "fan_speed": fan_speed,
#         "fan1_switch": fan1_switch,
#         "fan2_switch": fan2_switch,
#         "fan3_switch": fan3_switch,
#         "fan4_switch": fan4_switch,
#         "fan5_switch": fan5_switch,
#         "fan6_switch": fan6_switch,
#         "fan7_switch": fan7_switch,
#         "fan8_switch": fan8_switch
#     }
#     # 檢查輸入
#     if not isinstance(fan_speed, (int, type(None))):
#         return False, invalid_type()

#     if not all(isinstance(x, (bool, type(None))) for x in [fan1_switch, fan2_switch, fan3_switch, fan4_switch, fan5_switch, fan6_switch, fan7_switch, fan8_switch]):
#         return False, invalid_type()
    
#     try:
#         with ModbusTcpClient(host=modbus_host, port=modbus_port, unit=modbus_slave_id) as client:

#             # fan_error1 = True
#             # fan_error2 = False
#             sensor = read_sensor_data()
#             fan_error1 = sensor["error"].get("Fan_OverLoad1", False)
#             fan_error2 = sensor["error"].get("Fan_OverLoad2", False)


#             # 關閉錯誤範圍內的 switch
#             if fan_error1:
#                 # fan1_switch = fan2_switch = fan3_switch = fan4_switch = False
#                 fan_switch_result["fan1_switch"] = False
#                 fan_switch_result["fan2_switch"] = False
#                 fan_switch_result["fan3_switch"] = False
#                 fan_switch_result["fan4_switch"] = False
#             if fan_error2:
#                 # fan5_switch = fan6_switch = fan7_switch = fan8_switch = False
#                 fan_switch_result["fan5_switch"] = False
#                 fan_switch_result["fan6_switch"] = False
#                 fan_switch_result["fan7_switch"] = False
#                 fan_switch_result["fan8_switch"] = False    
                
#             # 設定 switch
#             for num in range(8):
#                 key = f"fan{num + 1}_switch"
#                 switch = fan_switch_result.get(key)
#                 # 判斷switch有無更改
#                 if switch is None:
#                     read_data = client.read_coils((8192 + 850 + num), 1, unit=modbus_slave_id)
#                     switch = read_data.bits[0]
#                     fan_switch_result[f"fan{num + 1}_switch"] = switch
#                 else:    
#                     set_fan_switch(num, [switch])
#                     op_logger.info(f"Fan switch{num + 1} updated successfully: {switch}")
#             # 判斷fan_speed有無更改
#             if fan_speed is None:
#                 read_data = client.read_holding_registers(470, 2)
#                 fan_speed = cvt_registers_to_float(read_data.registers[0], read_data.registers[1])
#                 fan_switch_result["fan_speed"] = fan_speed
#             else: 
#                 if not 25 <= fan_speed <= 100:
#                     return False, {
#                         "message": "Invalid fan speed. The fan speed must be within the range of 25 to 100."
#                     }  
                   
#                 set_fan(fan_speed)
#                 # fan_set["fan_set"] = fan_speed
#                 op_logger.info(f"Fan speed updated successfully: {fan_speed}")

            
#             return True, fan_switch_result

#     except Exception as e:
#         print(f"write fan_set: {e}")
#         return False, plc_error()

   

# def set_p_check(num, p_check):
#     try:
#         with ModbusTcpClient(
#             host=modbus_host, port=modbus_port, unit=modbus_slave_id
#         ) as client:
#             client.write_coils((8192 + 820 + num), p_check)
#     except Exception as e:
#         print(f"Pump speed setting error:{e}")


# def set_ps(speed):
#     speed1, speed2 = cvt_float_byte(speed)
#     try:
#         with ModbusTcpClient(
#             host=modbus_host, port=modbus_port, unit=modbus_slave_id
#         ) as client:
#             client.write_registers(246, [speed2, speed1])
#     except Exception as e:
#         print(f"pump speed setting error:{e}")


# def set_fan(speed):
#     speed1, speed2 = cvt_float_byte(speed)
#     try:
#         with ModbusTcpClient(
#             host=modbus_host, port=modbus_port, unit=modbus_slave_id
#         ) as client:
#             client.write_registers(470, [speed2, speed1])
#     except Exception as e:
#         print(f"pump speed setting error:{e}")

# def set_fan_switch(num, fan_switch):
#     try:
#         with ModbusTcpClient(
#             host=modbus_host, port=modbus_port, unit=modbus_slave_id
#         ) as client:
#             client.write_coils((8192 + 850 + num), fan_switch)
#     except Exception as e:
#         print(f"Pump speed setting error:{e}")            


# def set_swap(swap):
#     swap1, swap2 = cvt_float_byte(swap)
#     try:
#         with ModbusTcpClient(
#             host=modbus_host, port=modbus_port, unit=modbus_slave_id
#         ) as client:
#             client.write_registers(303, [swap2, swap1])
#     except Exception as e:
#         print(f"pump swap setting error:{e}")


# def combine_bits(lower, upper):
#     value = (upper << 16) | lower
#     return value


# def read_split_register(r, i):
#     lower_16 = r[i]
#     upper_16 = r[i + 1]
#     value = combine_bits(lower_16, upper_16)
#     return value


# def cvt_float_byte(value):
#     float_as_bytes = struct.pack(">f", float(value))
#     word1, word2 = struct.unpack(">HH", float_as_bytes)
#     return word1, word2


# def cvt_registers_to_float(reg1, reg2):
#     temp1 = [reg1, reg2]
#     decoder_big_endian = BinaryPayloadDecoder.fromRegisters(
#         temp1, byteorder=Endian.Big, wordorder=Endian.Little
#     )
#     decoded_value_big_endian = decoder_big_endian.decode_32bit_float()
#     return decoded_value_big_endian


# def read_data_from_json():
#     global thrshd, ctr_data, measure_data

#     with open(f"{json_path}/thrshd.json", "r") as file:
#         thrshd = json.load(file)

#     with open(f"{json_path}/ctr_data.json", "r") as file:
#         ctr_data = json.load(file)

#     with open(f"{json_path}/measure_data.json", "r") as file:
#         measure_data = json.load(file)


# def change_to_metric():
#     read_data_from_json()

#     for key in thrshd:
#         if not key.endswith("_trap") and not key.startswith("Delay_"):
#             if "Temp" in key:
#                 thrshd[key] = (thrshd[key] - 32) * 5.0 / 9.0

#             if "DewPoint" in key:
#                 thrshd[key] = (thrshd[key]) * 5.0 / 9.0

#             if "Prsr" in key:
#                 thrshd[key] = thrshd[key] * 6.89476

#             if "Flow" in key:
#                 thrshd[key] = thrshd[key] / 0.2642

#     registers = []
#     index = 0
#     thr_count = len(sensor_thrshd) * 2

#     for key in thrshd:
#         value = thrshd[key]
#         if index < int(thr_count / 2):
#             word1, word2 = cvt_float_byte(value)
#             registers.append(word2)
#             registers.append(word1)
#         index += 1

#     grouped_register = [registers[i : i + 64] for i in range(0, len(registers), 64)]

#     i = 0
#     for group in grouped_register:
#         try:
#             with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
#                 client.write_registers(1000 + i * 64, group)
#         except Exception as e:
#             print(f"write register thrshd issue:{e}")

#         i += 1

#     key_list = list(ctr_data["value"].keys())
#     for key in key_list:
#         if key == "oil_temp_set":
#             ctr_data["value"]["oil_temp_set"] = (
#                 (ctr_data["value"]["oil_temp_set"] - 32) / 9.0 * 5.0
#             )

#         if key == "oil_pressure_set":
#             ctr_data["value"]["oil_pressure_set"] = (
#                 ctr_data["value"]["oil_pressure_set"] * 6.89476
#             )

#     temp1, temp2 = cvt_float_byte(ctr_data["value"]["oil_temp_set"])
#     try:
#         with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
#             client.write_registers(993, [temp2, temp1])
#             client.write_registers(226, [temp2, temp1])
#     except Exception as e:
#         print(f"write oil temp error:{e}")

#     prsr1, prsr2 = cvt_float_byte(ctr_data["value"]["oil_pressure_set"])
#     try:
#         with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
#             client.write_registers(991, [prsr2, prsr1])
#             client.write_registers(224, [prsr2, prsr1])
#     except Exception as e:
#         print(f"write oil pressure error:{e}")

#     key_list = list(measure_data.keys())
#     for key in key_list:
#         if "Temp" in key:
#             measure_data[key] = (measure_data[key] - 32) * 5.0 / 9.0

#         if "Prsr" in key:
#             measure_data[key] = measure_data[key] * 6.89476

#         if "f1" in key or "f2" in key:
#             measure_data[key] = measure_data[key] / 0.2642
#     try:
#         with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
#             for i, (key, value) in enumerate(measure_data.items()):
#                 word1, word2 = cvt_float_byte(value)
#                 registers = [word2, word1]
#                 client.write_registers(901 + i * 2, registers)
#     except Exception as e:
#         print(f"measure data input error:{e}")


# def change_to_imperial():
#     read_data_from_json()

#     for key in thrshd:
#         if not key.endswith("_trap") and not key.startswith("Delay_"):
#             if "Temp" in key:
#                 thrshd[key] = thrshd[key] * 9.0 / 5.0 + 32.0

#             if "DewPoint" in key:
#                 thrshd[key] = thrshd[key] * 9.0 / 5.0

#             if "Prsr" in key:
#                 thrshd[key] = thrshd[key] * 0.145038

#             if "Flow" in key:
#                 thrshd[key] = thrshd[key] * 0.2642

#     registers = []
#     index = 0
#     thr_count = len(sensor_thrshd) * 2

#     for key in thrshd:
#         value = thrshd[key]
#         if index < int(thr_count / 2):
#             word1, word2 = cvt_float_byte(value)
#             registers.append(word2)
#             registers.append(word1)
#         index += 1

#     grouped_register = [registers[i : i + 64] for i in range(0, len(registers), 64)]

#     i = 0
#     for group in grouped_register:
#         try:
#             with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
#                 client.write_registers(1000 + i * 64, group)
#         except Exception as e:
#             print(f"write register thrshd issue:{e}")
#         i += 1

#     try:
#         word1, word2 = cvt_float_byte(ctr_data["value"]["oil_pressure_set"])
#         with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
#             client.write_registers(224, [word2, word1])
#     except Exception as e:
#         print(f"write oil pressure error:{e}")

#     try:
#         word1, word2 = cvt_float_byte(ctr_data["value"]["oil_temp_set"])
#         with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
#             client.write_registers(226, [word2, word1])
#     except Exception as e:
#         print(f"write oil pressure error:{e}")

#     key_list = list(ctr_data["value"].keys())
#     for key in key_list:
#         if key == "oil_temp_set":
#             ctr_data["value"]["oil_temp_set"] = (
#                 ctr_data["value"]["oil_temp_set"] * 9.0 / 5.0 + 32.0
#             )

#         if key == "oil_pressure_set":
#             ctr_data["value"]["oil_pressure_set"] = (
#                 ctr_data["value"]["oil_pressure_set"] * 0.145038
#             )

#     temp1, temp2 = cvt_float_byte(ctr_data["value"]["oil_temp_set"])
#     try:
#         with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
#             client.write_registers(993, [temp2, temp1])
#     except Exception as e:
#         print(f"write oil temp error:{e}")

#     pressure1, pressure2 = cvt_float_byte(ctr_data["value"]["oil_pressure_set"])
#     try:
#         with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
#             client.write_registers(991, [pressure2, pressure1])
#     except Exception as e:
#         print(f"write oil pressure error:{e}")

#     key_list = list(measure_data.keys())
#     for key in key_list:
#         if "Temp" in key:
#             measure_data[key] = measure_data[key] * 9.0 / 5.0 + 32.0

#         if "Prsr" in key:
#             measure_data[key] = measure_data[key] * 0.145038

#         if "f1" in key or "f2" in key:
#             measure_data[key] = measure_data[key] * 0.2642

#     try:
#         with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
#             for i, (key, value) in enumerate(measure_data.items()):
#                 word1, word2 = cvt_float_byte(value)
#                 registers = [word2, word1]
#                 client.write_registers(901 + i * 2, registers)
#     except Exception as e:
#         print(f"measure data input error:{e}")


# def change_data_by_unit():
#     try:
#         with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
#             last_unit = client.read_coils((8192 + 501), 1, unit=modbus_slave_id)
#             current_unit = client.read_coils((8192 + 500), 1, unit=modbus_slave_id)
#             client.close()

#             last_unit = last_unit.bits[0]
#             current_unit = current_unit.bits[0]

#             if current_unit:
#                 system_data["value"]["unit"] = "imperial"
#             else:
#                 system_data["value"]["unit"] = "metric"

#             if last_unit:
#                 system_data["value"]["last_unit"] = "imperial"
#             else:
#                 system_data["value"]["last_unit"] = "metric"

#             if current_unit and current_unit != last_unit:
#                 change_to_imperial()
#             elif not current_unit and current_unit != last_unit:
#                 change_to_metric()

#             client.write_coils((8192 + 501), [current_unit])

#             client.close()

#     except Exception as e:
#         print(f"unit set error:{e}")


# def read_ctr_data():
#     try:
#         with open(f"{json_path}/ctr_data.json", "r") as json_file:
#             data = json.load(json_file)
#             return data

#     except Exception as e:
#         print(f"read ctr_data error: {e}")
#         return plc_error()


def read_sensor_data():
    try:
        with open(f"{json_path}/sensor_data.json", "r") as json_file:
            data = json.load(json_file)
            return data

    except Exception as e:
        print(f"read sensor_data error: {e}")
        return plc_error()


# def read_unit():
#     try:
#         with open(f"{json_path}/system_data.json", "r") as json_file:
#             data = json.load(json_file)
#             unit = data["value"]["unit"]
#             return unit
#     except Exception as e:
#         print(f"read unit error: {e}")
#         return plc_error()


def plc_error():
    return {"message": "PLC Communication Error"}, 500


# def invalid_type():
#     return {"message": "Invalid input type"}, 400

# # set fan speed
# @default_ns.route("/cdu/control/fan_speed")
# class FanSpeed(Resource):
#     @default_ns.doc("get_fan_speed")
#     def get(self):
#         """Get fan setting"""
#         try:
#             ctr = read_ctr_data()
#             fan_set["fan_set"] = round(ctr["value"]["resultFan"])
#         except Exception as e:
#             print(f"read pressure_set: {e}")
#             return plc_error()

#         return fan_set

#     @default_ns.expect(fan_speed_model)
#     @default_ns.doc("patch_fan_set")
#     def patch(self):
#         """Update fan setting"""
#         try:
#             fan = api.payload["fan_speed"]
#             if not isinstance(fan, int):
#                 return invalid_type()

#             sensor = read_sensor_data()
#             ctr = read_ctr_data()
#             fan_error1 = sensor["error"]["Fan_OverLoad1"]
#             fan_error2 = sensor["error"]["Fan_OverLoad2"]
#             current_mode = ctr["value"]["resultMode"]

#             if current_mode in ["Stop", "Auto"]:
#                 return (
#                     {"message": "Fan speed can only be adjusted in manual mode."},
#                 ), 400

#             if not 0 <= fan <= 100:
#                 return {
#                     "message": "Invalid fan speed. The fan speed must be within the range of 0 to 100."
#                 }, 400
#             elif fan_error1 or fan_error2:
#                 word = ""
#                 if fan_error1 and fan_error2:
#                     word = "fan1 and fan2"
#                 elif fan_error1:
#                     word = "fan1"
#                 elif fan_error2:
#                     word = "fan2"

#                 return {
#                     "message": f"Unable to set the malfunctioning {word} due to overload error."
#                 }, 400
#             else:
#                 set_fan(fan)
#                 fan_set["fan_set"] = fan

#         except Exception as e:
#             print(f"write fan_set: {e}")
#             return plc_error()

#         op_logger.info(f"Fan update successfully. {fan_set}")
#         return {
#             "message": "Fan updated successfully",
#             "new_fan_set": fan_set["fan_set"],
#         }, 200


# # set prsr
# @default_ns.route("/cdu/control/pressure_set")
# class PressureSet(Resource):
#     @default_ns.expect(pressure_set_model)
#     @default_ns.doc("patch_pressure_set")
#     def patch(self):
#         """Update pressure setting: 0-750 kpa (0-108.75 psi)"""
#         prsr = api.payload.get("pressure_set")
#         try:
#             ctr = read_ctr_data()
#             current_mode = ctr["value"]["resultMode"]

#             if not isinstance(prsr, (int, float)):
#                 return False, invalid_type()

#             if current_mode in ["Stop", "Manual"]:
#                 return False, ("Pressure can only be adjusted in auto mode.", 400)
#             else:
#                 success, result = set_pressure_value()

#             if success:                
#                 op_logger.info(f"Pressure update successfully. {result}")
#                 return {
#                     "message": "Pressure updated successfully",
#                     "new_pressure_set": result
#                 }, 200
                
#             else:
#                 return {"message": result}, 400
        

                
#         except Exception as e:
#             print(f"temp_set_limit: {e}")
#             return plc_error()


# @default_ns.route("/cdu/control/pump_speed")
# class PumpSpeed(Resource):
#     @default_ns.doc("get_pump_speed")
#     def get(self):
#         """Get the current pump speeds"""

#         try:
#             data = read_ctr_data()
#             pump_speed_set["pump1_speed"] = (
#                 data["value"]["resultPS"] if data["value"]["resultP1"] else 0
#             )
#             pump_speed_set["pump2_speed"] = (
#                 data["value"]["resultPS"] if data["value"]["resultP2"] else 0
#             )
#             pump_speed_set["pump3_speed"] = (
#                 data["value"]["resultPS"] if data["value"]["resultP3"] else 0
#             )
#         except Exception as e:
#             print(f"get pump speed error:{e}")
#             return plc_error()

#         return pump_speed_set


# @default_ns.route("/cdu/control/pump1_speed")
# class Pump1Speed(Resource):
#     @default_ns.expect(pump1_speed_model)
#     @default_ns.doc("update_pump_speed")
#     def patch(self):
#         """Update the pump speeds in percentage(0-100) in manual mode"""

#         try:
#             ps = api.payload["pump_speed"]
#             p1 = api.payload["pump_switch"]

#             if not isinstance(ps, (int)):
#                 return invalid_type()

#             if not isinstance(p1, (bool)):
#                 return invalid_type()

#             sensor = read_sensor_data()
#             ctr = read_ctr_data()

#             current_mode = ctr["value"]["resultMode"]
#             error1 = sensor["error"]["Inv1_Error"]
#             ol1 = sensor["error"]["Inv1_OverLoad"]
#             mc1 = ctr["mc"]["resultMC1"]
#             # current_mode = "manual"
#             # error1 = False
#             # ol1 = False
#             # mc1 = True
#             if current_mode in ["Stop", "Auto"]:
#                 return (
#                     {"message": "Pump speed can only be adjusted in manual mode."},
#                 ), 400

#             if 0 < ps < 25 or ps > 100:
#                 return (
#                     {
#                         "message": "Invalid pump speed input. Accepted values are 25-100 or 0."
#                     },
#                 ), 400

#             if ps == 0:
#                 pump_speed_set["pump1_speed"] = 0
#             elif ps > 0:
#                 if p1:
#                     if error1 or ol1 or not mc1:
#                         pump_speed_set["pump1_speed"] = 0
#                         filter_data = {}
#                         filter_data = pump_speed_set.copy()
#                         exclude_key = ["pump2_speed", "pump3_speed"]
#                         for key in exclude_key:
#                             filter_data.pop(key, None)
#                         op_logger.info(
#                             f"Failed to activate pump1 due to error, overload or closed MC. {filter_data}"
#                         )
#                         return {
#                             "message": "Failed to activate pump1 due to error, overload or closed MC.",
#                             "pump_speed": filter_data,
#                         }, 400
#                     else:
#                         pump_speed_set["pump1_speed"] = ps
#                 else:
#                     pump_speed_set["pump1_speed"] = 0
#         except Exception as e:
#             print(f"write pump speed: {e}")
#             return plc_error()

#         set_ps(ps)
#         set_p_check(0, [p1])


#         filter_data = {}
#         filter_data = pump_speed_set.copy()
#         exclude_key = ["pump2_speed", "pump3_speed"]
#         for key in exclude_key:
#             filter_data.pop(key, None)

#         op_logger.info(f"Pump1 speed updated successfully. pump speed {filter_data}")
#         return {
#             "message": "Pump1 speed updated successfully",
#             "pump_speed": filter_data,
#         }, 200


# @default_ns.route("/cdu/control/pump2_speed")
# class Pump2Speed(Resource):
#     @default_ns.expect(pump2_speed_model)
#     @default_ns.doc("update_pump_speed")
#     def patch(self):
#         """Update the pump speeds in percentage(0-100) in manual mode"""

#         try:
#             ps = api.payload["pump_speed"]
#             p2 = api.payload["pump_switch"]

#             if not isinstance(ps, (int)):
#                 return invalid_type()

#             if not isinstance(p2, (bool)):
#                 return invalid_type()

#             sensor = read_sensor_data()
#             ctr = read_ctr_data()

#             current_mode = ctr["value"]["resultMode"]
#             error2 = sensor["error"]["Inv2_Error"]
#             ol2 = sensor["error"]["Inv2_OverLoad"]
#             mc2 = ctr["mc"]["resultMC2"]

#             if current_mode in ["Stop", "Auto"]:
#                 return "Pump speed can only be adjusted in manual mode.", 400

#             if 0 < ps < 25 or ps > 100:
#                 return (
#                     {
#                         "message": "Invalid pump speed input. Accepted values are 25-100 or 0."
#                     },
#                 ), 400

#             if ps == 0:
#                 pump_speed_set["pump2_speed"] = 0
#             elif ps > 0:
#                 if p2:
#                     if error2 or ol2 or not mc2:
#                         pump_speed_set["pump2_speed"] = 0

#                         filter_data = {}
#                         filter_data = pump_speed_set.copy()
#                         exclude_key = ["pump1_speed", "pump3_speed"]
#                         for key in exclude_key:
#                             filter_data.pop(key, None)

#                         op_logger.info(
#                             f"Failed to activate pump2 due to error, overload or closed MC. {filter_data}"
#                         )
#                         return {
#                             "message": "Failed to activate pump2 due to error, overload or closed MC.",
#                             "pump_speed": filter_data,
#                         }, 400
#                     else:
#                         pump_speed_set["pump2_speed"] = ps
#                 else:
#                     pump_speed_set["pump2_speed"] = 0

#         except Exception as e:
#             print(f"write pump speed: {e}")
#             return plc_error()

#         set_ps(ps)
#         set_p_check(1, [p2])

#         filter_data = {}
#         filter_data = pump_speed_set.copy()
#         exclude_key = ["pump1_speed", "pump3_speed"]
#         for key in exclude_key:
#             filter_data.pop(key, None)

#         op_logger.info(f"Pump2 speed updated successfully. pump speed {filter_data}")
#         return {
#             "message": "Pump2 speed updated successfully",
#             "pump_speed": filter_data,
#         }, 200


# @default_ns.route("/cdu/control/pump3_speed")
# class Pump3Speed(Resource):
#     @default_ns.expect(pump3_speed_model)
#     @default_ns.doc("update_pump_speed")
#     def patch(self):
#         """Update the pump speeds in percentage(0-100) in manual mode"""

#         try:
#             ps = api.payload["pump_speed"]
#             p3 = api.payload["pump_switch"]

#             if not isinstance(ps, (int)):
#                 return invalid_type()

#             if not isinstance(p3, (bool)):
#                 return invalid_type()

#             sensor = read_sensor_data()
#             ctr = read_ctr_data()

#             current_mode = ctr["value"]["resultMode"]
#             error3 = sensor["error"]["Inv3_Error"]
#             ol3 = sensor["error"]["Inv3_OverLoad"]
#             mc3 = ctr["mc"]["resultMC3"]

#             if current_mode in ["Stop", "Auto"]:
#                 return "Pump speed can only be adjusted in manual mode.", 400

#             if 0 < ps < 25 or ps > 100:
#                 return (
#                     {
#                         "message": "Invalid pump speed input. Accepted values are 25-100 or 0."
#                     },
#                 ), 400

#             if ps == 0:
#                 pump_speed_set["pump3_speed"] = 0
#             elif ps > 0:
#                 if p3:
#                     if error3 or ol3 or not mc3:
#                         pump_speed_set["pump3_speed"] = 0
#                         filter_data = {}
#                         filter_data = pump_speed_set.copy()
#                         exclude_key = ["pump1_speed", "pump2_speed"]
#                         for key in exclude_key:
#                             filter_data.pop(key, None)
#                         op_logger.info(
#                             f"Failed to activate pump3 due to error, overload or closed MC. {filter_data}"
#                         )
#                         return {
#                             "message": "Failed to activate pump3 due to error, overload or closed MC.",
#                             "pump_speed": filter_data,
#                         }, 400
#                     else:
#                         pump_speed_set["pump3_speed"] = ps
#                 else:
#                     pump_speed_set["pump3_speed"] = 0
#         except Exception as e:
#             print(f"write pump speed: {e}")
#             return plc_error()

#         set_ps(ps)
#         set_p_check(2, [p3])

#         filter_data = {}
#         filter_data = pump_speed_set.copy()
#         exclude_key = ["pump1_speed", "pump2_speed"]
#         for key in exclude_key:
#             filter_data.pop(key, None)

#         op_logger.info(f"Pump3 speed updated successfully. pump speed {filter_data}")
#         return {
#             "message": "Pump3 speed updated successfully",
#             "pump_speed": filter_data,
#         }, 200

# # set pump swap time
# @default_ns.route("/cdu/control/pump_swap_time")
# class PumpSwapTime(Resource):
#     @default_ns.doc("get_pump_swap_time")
#     def get(self):
#         """Get the time interval for pump swapping in minutes"""
#         try:
#             data = read_ctr_data()
#             pump_swap_time = {"pump_swap_time": data["value"]["resultSwap"]}
#         except Exception as e:
#             print(f"pump swap time error:{e}")
#             return plc_error()

#         return pump_swap_time

#     @default_ns.expect(pump_swap_time_model)
#     @default_ns.doc("update_pump_swap_time")
#     def patch(self):
#         """Update the time interval for pump swapping in minutes"""
#         new_time = api.payload.get("pump_swap_time")
        
#         ctr = read_ctr_data()
#         current_mode = ctr["value"]["resultMode"]

#         if not isinstance(new_time, int):
#             return False, invalid_type()

#         if current_mode in ["Stop", "Manual"]:
#             return False, ("Pump swap time can only be adjusted in auto mode.", 400)
#         else:
#             success, result = set_pump_swap_time(new_time)

#         if  success:
#             op_logger.info(f"Pump swap time updated successfully. {result}")
#             return {
#                 "message": "Pump swap time updated successfully",
#                 "new_pump_swap_time": result
#             }, 200
#         else:
#             return {"message": result}, 400


# # set temp
# @default_ns.route("/cdu/control/temp_set")
# class TempSet(Resource):

#     @default_ns.expect(temp_set_model)
#     @default_ns.doc("patch_temp_set")
#     def patch(self):
#         try:
#             ctr = read_ctr_data()
#             current_mode = ctr["value"]["resultMode"]
#             # current_mode = "auto"
#             if not isinstance(temp, int):
#                 return False, "Invalid type. Temperature must be integer."

#             if current_mode in ["Stop", "Manual"]:
#                 return False, "Temperature can only be adjusted in auto mode."
            
#             else:
#                 temp = api.payload["temp_set"]
#                 success, result = set_temperature()

#             if success:
#                 op_logger.info(f"Temperature updated successfully.{temp_set}")
#                 return {
#                     "message": "Temperature updated successfully",
#                     "new_temp_set": temp_set["temp_set"],
#                 }, 200
#             else:
#                 return {"message": result}, 400

#         except Exception as e:
#             print(f"temp_set_limit: {e}")
#             return plc_error()


# @default_ns.route("/cdu/status/fan_speed")
# class fan_speed(Resource):
#     @default_ns.doc("get_fan_speed")
#     def get(self):
#         """Get speed of fans"""
#         try:
#             sensor = read_sensor_data()

#             for k, v in sensor["value"].items():
#                 if k.startswith("fan_freq"):
#                     i = k[-1]
#                     fan_key = f"fan{i}_speed"
#                     data["fan_speed"][fan_key] = round(v)
#         except Exception as e:
#             print(f"fan speed error:{e}")
#             return plc_error()

#         return data["fan_speed"]


# @default_ns.route("/cdu/status/op_mode")
# class CduOpMode(Resource): 
#     @default_ns.doc("get_op_mode")
#     def get(self):
#         """Get the current operational mode stop, auto, or manual"""
#         try:
#             data = read_ctr_data()
#             op_mode["mode"] = data["value"]["opMod"]    
#             mode = data["value"]["resultMode"].lower()
#             temp_set=data["value"]["oil_temp_set"]
#             pressure_set=data["value"]["oil_pressure_set"]
#             pump_swap_time=data["value"]["resultSwap"]
#             if mode == "stop":
#                 return {"mode": mode} 
#             elif mode == "auto":
#                 return {"mode": mode,"temp_set": temp_set,
#                         "pressure_set": pressure_set,
#                         "pump_swap_time": pump_swap_time }
                
#             elif mode == "manual":
#                 pump_speed = data["value"]["pump_speed"]
#                 pump1_switch = data["value"]["resultP1"]
#                 pump2_switch = data["value"]["resultP2"]
#                 pump3_switch = data["value"]["resultP3"]
#                 fan_speed = data["value"]["fan_speed"]
#                 fan1_switch= data["value"]["resultFan1"]
#                 fan2_switch= data["value"]["resultFan2"]
#                 fan3_switch= data["value"]["resultFan3"]
#                 fan4_switch= data["value"]["resultFan4"]
#                 fan5_switch= data["value"]["resultFan5"]
#                 fan6_switch= data["value"]["resultFan6"]
#                 fan7_switch= data["value"]["resultFan7"]
#                 fan8_switch= data["value"]["resultFan8"]
#                 return {"mode": mode ,"pump_speed":pump_speed,
#                         "pump1_switch":pump1_switch,
#                         "pump2_switch": pump2_switch,
#                         "pump3_switch": pump3_switch,
#                         "fan_speed": fan_speed,
#                         "fan1_switch": fan1_switch,
#                         "fan2_switch": fan2_switch,
#                         "fan3_switch": fan3_switch,
#                         "fan4_switch": fan4_switch,
#                         "fan5_switch": fan5_switch,
#                         "fan6_switch": fan6_switch,
#                         "fan7_switch": fan7_switch,
#                         "fan8_switch": fan8_switch, }
#             else:
#                 return plc_error()
                
                
#         except Exception as e:
#             print(f"get mode error: {e}")
#             return plc_error()


#     @default_ns.expect(op_mode_model)
#     @default_ns.doc("set_op_mode")
#     def patch(self):
#         """Set the operational mode auto, stop, or manual"""

#         try:
#             # 引入資料
#             mode = api.payload["mode"]

#             if mode not in ["auto", "stop", "manual"]:
#                 return {
#                     "message": "Invalid operational mode. The allowed values are ‘auto’, ‘stop’, and ‘manual’."
#                 }, 400

#             with ModbusTcpClient(port=modbus_port, host=modbus_host) as client:
#                 if mode == "stop":
#                     client.write_coils((8192 + 514), [False])
#                     op_logger.info(f"mode updated successfully {mode}")
#                     return {
#                         "message": "mode updated successfully",
#                         "new_mode": mode
#                     }, 200
#                 elif mode == "manual":
#                     client.write_coils((8192 + 505), [True])
#                     client.write_coils((8192 + 514), [True])
#                     client.write_coils((8192 + 516), [False])
#                     # pump & fan設定
#                     pump_success, pump_result = set_pump_speed()
#                     fan_success, fan_result = set_fan_speed()
#                     # pump & fan錯誤判斷
#                     if not pump_success:
#                         return {
#                             "message": pump_result
#                         }, 400
#                     if not fan_success:   
#                         return {
#                             "message": fan_result
#                         }, 400                    
                        
#                     op_logger.info(f"mode updated successfully {mode}")
#                     return {
#                         "message": "mode updated successfully",
#                         "new_mode": mode,
#                         "pump_speed": pump_result["pump_speed"],
#                         "pump1_switch": pump_result["pump1_switch"],
#                         "pump2_switch": pump_result["pump2_switch"],
#                         "pump3_switch": pump_result["pump3_switch"],
#                         "fan_speed": fan_result["fan_speed"],
#                         "fan1_switch": fan_result["fan1_switch"],
#                         "fan2_switch": fan_result["fan2_switch"],
#                         "fan3_switch": fan_result["fan3_switch"],
#                         "fan4_switch": fan_result["fan4_switch"],
#                         "fan5_switch": fan_result["fan5_switch"],
#                         "fan6_switch": fan_result["fan6_switch"],
#                         "fan7_switch": fan_result["fan7_switch"],
#                         "fan8_switch": fan_result["fan8_switch"],
#                     }, 200
#                 else:
#                     client.write_coils((8192 + 505), [False])
#                     client.write_coils((8192 + 514), [True])
#                     client.write_coils((8192 + 516), [False])
#                     # temp, prsr, swap設定
#                     temp_success, temp_set = set_temperature() 
#                     prsr_success, pressure_set = set_pressure_value()
#                     swap_success, pump_swap_time = set_pump_swap_time()
#                     # temp, prsr, swap錯誤判斷 
#                     if not(temp_success): 
#                         return {
#                             "message": temp_set
#                         }, 400
#                     if not(prsr_success): 
#                         return {
#                             "message": pressure_set
#                         }, 400
#                     if not(swap_success): 
#                         return {
#                             "message": pump_swap_time
#                         }, 400
                    
                    
#                     op_logger.info(f"mode updated successfully {mode}")
#                     return {
#                         "message": "mode updated successfully",
#                         "new_mode": mode,
#                         "temp_set": temp_set,
#                         "pressure_set": pressure_set,
#                         "pump_swap_time": pump_swap_time
#                     }, 200
                    
                    
                
#         except Exception as e:
#             print(f"write mode error:{e}")
#             return plc_error()


# @default_ns.route("/cdu/status/pump_health")
# class pump_health(Resource):
#     @default_ns.doc("get_pump_health")
#     def get(self):
#         """Get health of pumps"""
#         try:
#             sensor = read_sensor_data()

#             data["pump_health"]["pump1_health"] = (
#                 "Overload"
#                 if sensor["error"]["Inv1_OverLoad"]
#                 else "Error"
#                 if sensor["error"]["Inv1_Error"]
#                 else "OK"
#             )
#             data["pump_health"]["pump2_health"] = (
#                 "Overload"
#                 if sensor["error"]["Inv2_OverLoad"]
#                 else "Error"
#                 if sensor["error"]["Inv2_Error"]
#                 else "OK"
#             )
#             data["pump_health"]["pump3_health"] = (
#                 "Overload"
#                 if sensor["error"]["Inv3_OverLoad"]
#                 else "Error"
#                 if sensor["error"]["Inv3_Error"]
#                 else "OK"
#             )

#         except Exception as e:
#             print(f"pump health error:{e}")
#             return plc_error()

#         return data["pump_health"]


# @default_ns.route("/cdu/status/pump_service_hours")
# class pump_Service_hours(Resource):
#     @default_ns.doc("get_pump_service_hours")
#     def get(self):
#         """Get service hours of pumps"""
#         try:
#             ctr = read_ctr_data()

#             data["pump_service_hours"]["pump1_service_hours"] = ctr["text"][
#                 "Pump1_run_time"
#             ]
#             data["pump_service_hours"]["pump2_service_hours"] = ctr["text"][
#                 "Pump2_run_time"
#             ]
#             data["pump_service_hours"]["pump3_service_hours"] = ctr["text"][
#                 "Pump3_run_time"
#             ]
#         except Exception as e:
#             print(f"pump speed time error:{e}")
#             return plc_error()

#         return data["pump_service_hours"]


# @default_ns.route("/cdu/status/pump_speed")
# class pump_speed(Resource):
#     @default_ns.doc("get_pump_status")
#     def get(self):
#         """Get speed of pumps"""
#         try:
#             sensor = read_sensor_data()
#             data["pump_speed"]["pump1_speed"] = round(sensor["value"]["inv1_freq"])
#             data["pump_speed"]["pump2_speed"] = round(sensor["value"]["inv2_freq"])
#             data["pump_speed"]["pump3_speed"] = round(sensor["value"]["inv3_freq"])
#         except Exception as e:
#             print(f"pump speed error:{e}")
#             return plc_error()

#         return data["pump_speed"]


# @default_ns.route("/cdu/status/pump_state")
# class pump_state(Resource):
#     @default_ns.doc("get_pump_state")
#     def get(self):
#         """Get state of pumps"""
#         try:
#             sensor = read_sensor_data()
#             data["pump_state"]["pump1_state"] = (
#                 "Enable" if round(sensor["value"]["inv1_freq"]) >= 25 else "Disable"
#             )
#             data["pump_state"]["pump2_state"] = (
#                 "Enable" if round(sensor["value"]["inv2_freq"]) >= 25 else "Disable"
#             )
#             data["pump_state"]["pump3_state"] = (
#                 "Enable" if round(sensor["value"]["inv3_freq"]) >= 25 else "Disable"
#             )
#         except Exception as e:
#             print(f"pump speed error:{e}")
#             return plc_error()

#         return data["pump_state"]


# sensor_mapping = {
#     "temp_clntSply": "temp_coolant_supply",
#     "temp_clntSplySpare": " temp_coolant_supply_spare",
#     "temp_clntRtn": "temp_coolant_return",
#     "temp_clntRtnSpare": "temp_coolant_return_spare",
#     "prsr_clntSply": "pressure_coolant_supply",
#     "prsr_clntSplySpare": "pressure_coolant_supply_spare",
#     "prsr_clntRtn": "pressure_coolant_return",
#     "prsr_clntRtnSpare": "pressure_coolant_return_spare",
#     "prsr_fltIn": "pressure_filter_in",
#     "prsr_fltOut": "pressure_filter_out",
#     "clnt_flow": "coolant_flow_rate",
#     "ambient_temp": "temperature_ambient",
#     "relative_humid": "humidity_relative",
#     "dew_point": "temperature_dew_point",
#     "pH": "ph_level",
#     "cdct": "conductivity",
#     "tbd": "turbidity",
#     "power": "power_total",
#     "AC": "cooling_capacity",
#     "inv1_freq": "pump1_speed",
#     "inv2_freq": "pump2_speed",
#     "inv3_freq": "pump3_speed",
#     "heat_capacity": "heat_capacity",
#     "fan_freq1": "fan1_speed",
#     "fan_freq2": "fan2_speed",
#     "fan_freq3": "fan3_speed",
#     "fan_freq4": "fan4_speed",
#     "fan_freq5": "fan5_speed",
#     "fan_freq6": "fan6_speed",
#     "fan_freq7": "fan7_speed",
#     "fan_freq8": "fan8_speed",  
# }

# @default_ns.route("/cdu/status/sensor_value")
# class CduSensorValue(Resource):
#     @default_ns.doc("get_sensor_value")
#     def get(self):
#         """Get the current sensor values of CDU"""
#         try:
#             sensor = read_sensor_data()
#             for key in data["sensor_value"]:
#                 if key != "clnt_flow":
#                     data["sensor_value"][key] = round(sensor["value"][key], 2)
#                 else:
#                     data["sensor_value"][key] = round(sensor["value"][key])
#         except Exception as e:
#             print(f"get mode error: {e}")
#             return plc_error()

#         exclude_keys = ["inv1_freq", "inv2_freq", "inv3_freq", "fan_freq"]
#         filter_data = {}
#         filter_data = data["sensor_value"].copy()

#         for key in exclude_keys:
#             filter_data.pop(key, None)
#         result = {sensor_mapping[key]: value for key, value in filter_data.items()}
#         return result
# @default_ns.route("/cdu/status/device")
# class CduDevice(Resource):
#     @default_ns.doc("get_device")
#     def get(self):
#         """Get the current device values of CDU"""
#         try:
#             with open(f"{json_path}/scc_device.json", "r") as file:
#                 device = json.load(file)
#         except Exception as e:
#             return plc_error()
           
#         return device


# @default_ns.route("/error_messages")
# class ErrorMessages(Resource):
#     @default_ns.doc("get_error_messages")
#     def get(self):
#         """Get the list of error messages happening in the system"""

#         try:
#             sensor = read_sensor_data()

#             key_mapping = {
#                 "M100": "temp_clntSply_high",
#                 "M101": "temp_clntSplySpare_high",
#                 "M102": "temp_clntRtn_high",
#                 "M103": "temp_clntRtnSpare_high",
#                 "M104": "prsr_clntSply_high",
#                 "M105": "prsr_clntSplySpare_high",
#                 "M106": "prsr_clntRtn_high",
#                 "M107": "prsr_clntRtnSpare_high",
#                 "M108": "Prsr_FltIn_low",
#                 "M109": "Prsr_FltIn_high",
#                 "M110": "Prsr_FltOut_high",
#                 "M111": "clnt_flow_low",
#                 "M112": "Ambient_Temp_low",
#                 "M113": "Ambient_Temp_high",
#                 "M114": "Relative_Humid_low",
#                 "M115": "Relative_Humid_high",
#                 "M116": "Dew_Point_low",
#                 "M117": "pH_low",
#                 "M118": "pH_high",
#                 "M119": "cdct_low",
#                 "M120": "cdct_high",
#                 "M121": "tbd_low",
#                 "M122": "tbd_high",
#                 "M123": "AC_high",
#             }

#             for msg_key, sensor_key in key_mapping.items():
#                 messages["warning"][msg_key][1] = sensor["warning"][sensor_key]

#             key_mapping = {
#                 "M200": "temp_clntSply_high",
#                 "M201": "temp_clntSplySpare_high",
#                 "M202": "temp_clntRtn_high",
#                 "M203": "temp_clntRtnSpare_high",
#                 "M204": "prsr_clntSply_high",
#                 "M205": "prsr_clntSplySpare_high",
#                 "M206": "prsr_clntRtn_high",
#                 "M207": "prsr_clntRtnSpare_high",
#                 "M208": "Prsr_FltIn_low",
#                 "M209": "Prsr_FltIn_high",
#                 "M210": "Prsr_FltOut_high",
#                 "M211": "clnt_flow_low",
#                 "M212": "Ambient_Temp_low",
#                 "M213": "Ambient_Temp_high",
#                 "M214": "Relative_Humid_low",
#                 "M215": "Relative_Humid_high",
#                 "M216": "Dew_Point_low",
#                 "M217": "pH_low",
#                 "M218": "pH_high",
#                 "M219": "cdct_low",
#                 "M220": "cdct_high",
#                 "M221": "tbd_low",
#                 "M222": "tbd_high",
#                 "M223": "AC_high",
#             }

#             for msg_key, sensor_key in key_mapping.items():
#                 messages["alert"][msg_key][1] = sensor["alert"][sensor_key]

#             key_mapping = {
#                 "M300": "Inv1_OverLoad",
#                 "M301": "Inv2_OverLoad",
#                 "M302": "Inv3_OverLoad",
#                 "M303": "Fan_OverLoad1",
#                 "M304": "Fan_OverLoad2",
#                 "M305": "Inv1_Error",
#                 "M306": "Inv2_Error",
#                 "M307": "Inv3_Error",
#                 "M308": "ATS1",
#                 "M309": "Inv1_Com",
#                 "M310": "Inv2_Com",
#                 "M311": "Inv3_Com",
#                 "M312": "Clnt_Flow_Com",
#                 "M313": "Ambient_Temp_Com",
#                 "M314": "Relative_Humid_Com",
#                 "M315": "Dew_Point_Com",
#                 "M316": "Cdct_Sensor_Com",
#                 "M317": "pH_Com",
#                 "M318": "Tbd_Com",
#                 "M319": "ATS1_Com",
#                 "M320": "ATS2_Com",
#                 "M321": "Power_Meter_Com",
#                 "M322": "Average_Current_Com",
#                 "M323": "Fan1_Com",
#                 "M324": "Fan2_Com",
#                 "M325": "Fan3_Com",
#                 "M326": "Fan4_Com",
#                 "M327": "Fan5_Com",
#                 "M328": "Fan6_Com",
#                 "M329": "Fan7_Com",
#                 "M330": "Fan8_Com",
#                 "M331": "TempClntSply_broken",
#                 "M332": "TempClntSplySpare_broken",
#                 "M333": "TempClntRtn_broken",
#                 "M334": "TempClntRtnSpare_broken",
#                 "M335": "PrsrClntSply_broken",
#                 "M336": "PrsrClntSplySpare_broken",
#                 "M337": "PrsrClntRtn_broken",
#                 "M338": "PrsrClntRtnSpare_broken",
#                 "M339": "PrsrFltIn_broken",
#                 "M340": "PrsrFltOut_broken",
#                 "M341": "Clnt_Flow_broken",
#                 "M342": "pc1_error",
#                 "M343": "pc2_error",
#                 "M344": "leakage1_leak",
#                 "M345": "leakage1_broken",
#                 "M346": "level1",
#                 "M347": "level2",
#                 "M348": "level3",
#                 "M349": "power24v1",
#                 "M350": "power24v2",
#                 "M351": "power12v1",
#                 "M352": "power12v2",
#                 "M353": "main_mc_error",
#                 "M354": "fan1_error",
#                 "M355": "fan2_error",
#                 "M356": "fan3_error",
#                 "M357": "fan4_error",
#                 "M358": "fan5_error",
#                 "M359": "fan6_error",
#                 "M360": "fan7_error",
#                 "M361": "fan8_error",
#                 "M362": "Low_Coolant_Level_Warning",
#                 "M363": "PLC",
#             }
#             for msg_key, sensor_key in key_mapping.items():
#                 messages["error"][msg_key][1] = sensor["error"][sensor_key]

#             rack_mapping = {
#                 "M400": "rack1_broken",
#                 "M401": "rack2_broken",
#                 "M402": "rack3_broken",
#                 "M403": "rack4_broken",
#                 "M404": "rack5_broken",
#                 "M405": "rack6_broken",
#                 "M406": "rack7_broken",
#                 "M407": "rack8_broken",
#                 "M408": "rack9_broken",
#                 "M409": "rack10_broken",
#                 "M410": "rack1_leak",
#                 "M411": "rack2_leak",
#                 "M412": "rack3_leak",
#                 "M413": "rack4_leak",
#                 "M414": "rack5_leak",
#                 "M415": "rack6_leak",
#                 "M416": "rack7_leak",
#                 "M417": "rack8_leak",
#                 "M418": "rack9_leak",
#                 "M419": "rack10_leak",
#                 "M420": "rack1_error",
#                 "M421": "rack2_error",
#                 "M422": "rack3_error",
#                 "M423": "rack4_error",
#                 "M424": "rack5_error",
#                 "M425": "rack6_error",
#                 "M426": "rack7_error",
#                 "M427": "rack8_error",
#                 "M428": "rack9_error",
#                 "M429": "rack10_error",
#             }

#             for msg_key, sensor_key in rack_mapping.items():
#                 messages["rack"][msg_key][1] = sensor["rack"][sensor_key]
#         except Exception as e:
#             print(f"error message issue:{e}")
#             return plc_error()

#         error_messages = []
#         for category in ["warning", "alert", "error", "rack"]:
#             for code, message in messages[category].items():
#                 if message[1]:
#                     error_messages.append({"error_code": code, "message": message[0]})

#         return error_messages


# @default_ns.route("/unit_set")
# class Unit(Resource):
#     @default_ns.doc("get_unit_set")
#     def get(self):
#         """Get the current unit setting"""
#         try:
#             unit = read_unit()
#             unit_set["unit"] = unit
#         except Exception as e:
#             print(f"unit set error:{e}")
#             return plc_error()

#         return unit_set

#     @default_ns.expect(unit_set_model)
#     @default_ns.doc("update_unit_set")
#     def patch(self):
#         """Update the unit setting to metric or imperial"""

#         try:
#             unit = api.payload["unit_set"].lower()
#             if unit not in ["metric", "imperial"]:
#                 return {
#                     "message": "Invalid unit. The unit must be either 'metric' or 'imperial'."
#                 }, 400
#             else:
#                 unit_set["unit"] = unit
#                 coil_value = True if unit == "imperial" else False

#                 with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
#                     client.write_coil(address=(8192 + 500), value=coil_value)
#                 change_data_by_unit()
#         except Exception as e:
#             print(f"write unit: {e}")
#             return plc_error()

#         op_logger.info(f"Unit updated successfully {unit_set}")
#         return {
#             "message": "Unit updated successfully",
#             "new_unit": unit_set["unit"],
#         }, 200

# # 設定 reqparse 處理檔案上傳
# upload_parser = reqparse.RequestParser()
# upload_parser.add_argument("file", location="files", required=True, help="請上傳 ZIP 檔案")

# # 目標 API 端點
# TARGET_SERVERS = {
#     "upload/main/service.zip": "http://192.168.3.100:5501/api/v1/upload_zip",
#     "upload/spare/service.zip": "http://192.168.3.101:5501/api/v1/upload_zip",
# }

# # 定義上傳 API
# @default_ns.route("/update_firmware")
# #curl -X POST "http://127.0.0.1:5001/api/v1/update_firmware" -F "file=@/path/to/upload.zip"

# class UploadZipFile(Resource):
#     @default_ns.expect(upload_parser)
#     def post(self):
#         """上傳 ZIP 並分發到目標伺服器"""
#         args = upload_parser.parse_args()
#         file = request.files.get("file")

#         # 驗證檔案是否存在
#         if not file:
#             return {"message": "No File Part"}, 400
#         if file.filename == "":
#             return {"message": "No File Selected"}, 400
#         if file.filename != "upload.zip":
#             return {"message": "Please upload correct file name"}, 400
#         if not file.filename.endswith(".zip"):
#             return {"message": "Wrong File Type"}, 400

#         # 定義暫存解壓縮目錄
#         temp_dir = "/tmp/uploaded_zip"
#         os.makedirs(temp_dir, exist_ok=True)

#         # 存到本機暫存區
#         local_zip_path = os.path.join(temp_dir, file.filename)
#         file.save(local_zip_path)

#         # 解壓縮 ZIP
#         try:
#             with zipfile.ZipFile(local_zip_path, "r") as zip_ref:
#                 zip_ref.extractall(temp_dir)
#         except zipfile.BadZipFile:
#             return {"message": "Invalid ZIP file"}, 400

#         upload_results = {}

#         # 上傳解壓縮的 ZIP 檔案到不同伺服器
#         for file_path, target_url in TARGET_SERVERS.items():
#             full_file_path = os.path.join(temp_dir, file_path)  # 修正檔案路徑
#             if os.path.exists(full_file_path):
#                 try:
#                     with open(full_file_path, "rb") as f:
#                         files = {"file": (os.path.basename(file_path), f, "application/zip")}
#                         response = requests.post(target_url, files=files, auth=("admin", "Supermicro12729477"), verify=False)

#                     upload_results[file_path] = {
#                         "status": response.status_code,
#                         "response": response.text
#                     }
#                 except Exception as e:
#                     upload_results[file_path] = {"status": "error", "error": str(e)}
#             else:
#                 upload_results[file_path] = {"status": "error", "error": "File not found"}

#         # 清理暫存檔案
#         os.remove(local_zip_path)
#         for file_path in TARGET_SERVERS.keys():
#             full_file_path = os.path.join(temp_dir, file_path)
#             if os.path.exists(full_file_path):
#                 os.remove(full_file_path)

#         try:
#             # 發送 GET 請求到該 API
#             response = requests.get("http://192.168.3.101/api/v1/reboot", auth=("admin", "Supermicro12729477"), verify=False)

#             # 檢查回應狀態
#             if response.status_code == 200:
#                 print("System reboot initiated successfully.")
#             else:
#                 print(f"Failed to initiate reboot. Status code: {response.status_code}")

#         except requests.RequestException as e:
#             print(f"An error occurred: {e}")
#         time.sleep(5)
#         try:
#             # 發送 GET 請求到該 API
#             response = requests.get("http://192.168.3.100/api/v1/reboot", auth=("admin", "Supermicro12729477"), verify=False)

#             # 檢查回應狀態
#             if response.status_code == 200:
#                 print("System reboot initiated successfully.")
#             else:
#                 print(f"Failed to initiate reboot. Status code: {response.status_code}")

#         except requests.RequestException as e:
#             print(f"An error occurred: {e}")         
#         return {"message": "Upload Completed, Please Restart PC", "results": upload_results}, 200
Sensors_data = {
    "PrimaryFlowLitersPerMinute": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimaryFlowLitersPerMinute",
        "Name": "Primary Flow Liters Per Minute",
        "Reading": "1",
        "ReadingUnits": "L/min",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryFlowLitersPerMinute",
    },
    "PrimaryHeatRemovedkW": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimaryHeatRemovedkW",
        "Name": "Primary Heat Removed kW",
        "Reading": 0.2,
        "ReadingUnits": "kW",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryHeatRemovedkW",
    },
    "PrimarySupplyTemperatureCelsius": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimarySupplyTemperatureCelsius",
        "Name": "Primary Supply Temperature Celsius",
        "Reading": 23.32,
        "ReadingUnits": "Celsius",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimarySupplyTemperatureCelsius",
    },
    "PrimaryReturnTemperatureCelsius": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimaryReturnTemperatureCelsius",
        "Name": "Primary Return Temperature Celsius",
        "Reading": 23.45,
        "ReadingUnits": "Celsius",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryReturnTemperatureCelsius",
    },
    "PrimaryDeltaTemperatureCelsius": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimaryDeltaTemperatureCelsius",
        "Name": "Primary Delta Temperature Celsius",
        "Reading": 0.13,
        "ReadingUnits": "Celsius",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryDeltaTemperatureCelsius",
    },
    "PrimarySupplyPressurekPa": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimarySupplyPressurekPa",
        "Name": "Primary Supply Pressure kPa",
        "Reading": 220.0,
        "ReadingUnits": "kPa",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimarySupplyPressurekPa",
    },
    "PrimaryReturnPressurekPa": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimaryReturnPressurekPa",
        "Name": "Primary Return Pressure kPa",
        "Reading": 85.0,
        "ReadingUnits": "kPa",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryReturnPressurekPa",
    },
    "PrimaryDeltaPressurekPa": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimaryDeltaPressurekPa",
        "Name": "Primary Delta Pressure kPa",
        "Reading": 0,
        "ReadingUnits": "kPa",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryDeltaPressurekPa",
    },
    "TemperatureCelsius": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "TemperatureCelsius",
        "Name": "Temperature Celsius",
        "Reading": 23.98,
        "ReadingUnits": "Celsius",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/TemperatureCelsius",
    },
    "DewPointCelsius": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "DewPointCelsius",
        "Name": "Dew Point Celsius",
        "Reading": 14.87,
        "ReadingUnits": "Celsius",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/DewPointCelsius",
    },
    "HumidityPercent": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "HumidityPercent",
        "Name": "Humidity Percent",
        "Reading": 56.73,
        "ReadingUnits": "Percent",
        "Status": {
            "Health": "OK", 
            "State": "Enabled"
        },
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/HumidityPercent",
    },
}

ThermalEquipment_data= {
    "@odata.type": "#ThermalEquipment.v1_0_0.ThermalEquipment",
    "Name": "Thermal Equipment",
    "Id": "ThermalEquipment",
    "CDUs": {
        "@odata.id": "/redfish/v1/ThermalEquipment/CDUs"   
    },
    "@odata.id": "/redfish/v1/ThermalEquipment"
}
CDUs_data = {
    "@odata.type": "#CoolingUnitCollection.CoolingUnitCollection",
    "Name": "CDU Collection",
    "Members@odata.count": 1,
    "Members": [{"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1"}],
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs"
}
CDUs_data_1 = {
    "@odata.type": "#CoolingUnit.v1_1_0.CoolingUnit",
    "Name": "#1 Cooling Distribution Unit",
    "Id": "1",
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
    "Coolant": {
        "CoolantType": "Water",
        "DensityKgPerCubicMeter": 1000,
        "SpecificHeatkJoulesPerKgK": 4180
    },
    "LeakDetection": {
        "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection"
    },
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
            ]
        }
    },
    # "Oem": {
    #     "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Oem"
    # },
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
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1"
}

PrimaryCoolantConnectors_data = {
    "@odata.type": "#CoolantConnectorCollection.CoolantConnectorCollection",
    "Name": "Primary (supply side) Cooling Loop Connection Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/PrimaryCoolantConnectors/1"
        }
    ],
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/PrimaryCoolantConnectors"
}

PrimaryCoolantConnectors_data_1 ={
    "@odata.type": "#CoolantConnector.v1_1_0.CoolantConnector",
    "Id": "1",
    "Name": "Mains Input from Chiller",
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "Coolant": {
        "CoolantType": "Water",
        "DensityKgPerCubicMeter": 1000,
        "SpecificHeatkJoulesPerKgK": 4180
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
    "Oem": {},
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/PrimaryCoolantConnectors/1"
}

cdus_pumps={
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
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps"
}

# -------------------------------------
# pumpspeed patch設置
pumpspeed_patch = redfish_ns.model('PumpSpeedControlPatch', {
    'pump_speed': fields.Integer(
        required=True,
        description='pump轉速百分比 (0–100)',
        default=50,
    ),
    "pump_switch": fields.Boolean(
        required=True,
        description='pump switch',
    ),
})

cdus_pumps_1={
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
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/1"
}

cdus_pumps_2 = {
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
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/2"
}

cdus_pumps_3 = {
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
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/3"
}

cdus_filters={
    "@odata.type": "#FilterCollection.FilterCollection",
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Filters",
    "Name": "Filter Collection",
    "Members@odata.count": 0,
    "Members": [
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Filters/1"
        }
    ]
}

cdus_filters_1 = {
  "@odata.type": "#Filter.v1_0_0.Filter",
  "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Filters/1",
  "Id": "1",
  "Name": "Cooling Loop Filter",
#   "FilterType": "Cartridge",
  "ServicedDate": "2020-12-24T08:00:00Z",
  "ServiceHours": 5791,
  "RatedServiceHours": 10000,
  "Manufacturer": "Contoso",
  "Model": "MrCoffee",
  "PartNumber": "Cone4",
  "Status": {
    "State": "Enabled",
    "Health": "OK"
  },
  "Location": {
    "Placement": {
      "Row": "North 1"
    }
  },
}

environment_metrics = {
    "@odata.type": "#EnvironmentMetrics.v1_3_2.EnvironmentMetrics",
    "Id": "EnvironmentMetrics",
    "Name": "CDU Environment Metrics",
    # "AbsoluteHumidity": {
    #     "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/AbsoluteHumidity",
    #     "Reading": 11.46
    # },
    "TemperatureCelsius": {
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/TemperatureCelsius",
        "Reading": 19.81
    },
    "DewPointCelsius": {
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/DewPointCelsius",
        "Reading": 13.53
    },
    "HumidityPercent": {
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/HumidityPercent",
        "Reading": 67.11
    },
    "Oem": {
    },
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/EnvironmentMetrics"
}

reservoirs = {
    "@odata.type": "#ReservoirCollection.ReservoirCollection",
    "Name": "Reservoir Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Reservoirs/1"
        },
    ],
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Reservoirs"
}
reservoirs_1 = {
    "@odata.type": "#Reservoir.v1_0_0.Reservoir",
    "Id": "1",
    "ReservoirType": "Reserve",
    "Name": "Liquid Level",
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "CapacityLiters": 100.0,
    "FluidLevelStatus": "OK",
    "Location": {
        "PartLocation": {
            "ServiceLabel": "Reservoir 1",
            "LocationType": "Bay"
        }
    },
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Reservoirs/1"
}

root_data={
    "@odata.type": "#ServiceRoot.v1_17_0.ServiceRoot",
    "Id": "RootService",
    "Name": "Redfish Service",
    "RedfishVersion": "1.14.0",
    "UUID": "00000000-0000-0000-0000-e45f013e98f8",
    "ProtocolFeaturesSupported": {
        "FilterQuery": False,
        "SelectQuery": False,
        "ExcerptQuery": False,
        "OnlyMemberQuery": False,
        "ExpandQuery": {
            "Links": False,
            "NoLinks": False,
            "ExpandAll": False,
            "Levels": False,
            "MaxLevels": 3
        }
    },
    "ThermalEquipment": {
        "@odata.id": "/redfish/v1/ThermalEquipment"
    },
    "Managers": {
        "@odata.id": "/redfish/v1/Managers"
    },
    "Chassis": {
        "@odata.id": "/redfish/v1/Chassis"
    },
    "SessionService": {
        "@odata.id": "/redfish/v1/SessionService"
    },
    "AccountService": {
        "@odata.id": "/redfish/v1/AccountService"
    },
    # "EventService": {
    #     "@odata.id": "/redfish/v1/EventService"
    # },
    # "CertificateService": {
    #     "@odata.id": "/redfish/v1/CertificateService"
    # },
    "TelemetryService": {
        "@odata.id": "/redfish/v1/TelemetryService"
    },
    "UpdateService": {
    "@odata.id": "/redfish/v1/UpdateService"
    },
    # "MessageRegistry": {
    #     "@odata.id": "/redfish/v1/Registries"
    # },
    "Links": {
        "Sessions": {
            "@odata.id": "/redfish/v1/SessionService/Sessions"
        }
    },
    "ServiceIdentification": "ServiceRoot",
    "Vendor": "Supermicro",
    "@odata.id": "/redfish/v1/"
}

managers_data = {
    "@odata.type": "#ManagerCollection.ManagerCollection",
    "Name": "Manager Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/Managers/CDU"
        }
    ],
    "Oem": {
    },
    "@odata.id": "/redfish/v1/Managers"
}

managers_cdu_data =    {
    "@odata.type": "#Manager.v1_15_0.Manager",
    "Id": "CDU",
    "Name": "CDU Network Interface Module",
    "ManagerType": "ManagementController",
    "ServiceEntryPointUUID": "92384634-2938-2342-8820-489239905423",
    "UUID": "00000000-0000-0000-0000-e45f013e98f8",
    "Model": "Joo Janta 200",
    "DateTime": "2025/02/21T06:02:08Z", # 有規範怎麼寫
    "DateTimeLocalOffset": "+00:00", # 有規範怎麼寫
    "LastResetTime": "2025-01-24T07:08:48Z",
    "AutoDSTEnabled": False,
    "AutoDSTEnabled@Redfish.AllowableValues": [
        "False"
    ],
    "TimeZoneName": "test_1",
    "TimeZoneName@Redfish.AllowableValues": [
    "(UTC+00:00) Coordinated Universal Time",
    "(UTC+00:00) Dublin, Edinburgh, Lisbon, London",
    "(UTC+00:00) Monrovia, Reykjavik",
        "(UTC+00:00) Sao Tome",
        "(UTC+01:00) Amsterdam, Berlin, Bern, Rome, Stockholm, Vienna",
        "(UTC+01:00) Belgrade, Bratislava, Budapest, Ljubljana, Prague",
        "(UTC+01:00) Brussels, Copenhagen, Madrid, Paris",
        "(UTC+01:00) Casablanca",
        "(UTC+01:00) Sarajevo, Skopje, Warsaw, Zagreb",
        "(UTC+01:00) West Central Africa",
        "(UTC+02:00) Amman",
        "(UTC+02:00) Athens, Bucharest",
        "(UTC+02:00) Beirut",
        "(UTC+02:00) Cairo",
        "(UTC+02:00) Chisinau",
        "(UTC+02:00) Damascus",
        "(UTC+02:00) Gaza, Hebron",
        "(UTC+02:00) Harare, Pretoria",
        "(UTC+02:00) Helsinki, Kyiv, Riga, Sofia, Tallinn, Vilnius",
        "(UTC+02:00) Jerusalem",
        "(UTC+02:00) Juba",
        "(UTC+02:00) Kaliningrad",
        "(UTC+02:00) Khartoum",
        "(UTC+02:00) Tripoli",
        "(UTC+02:00) Windhoek",
        "(UTC+03:00) Baghdad",
        "(UTC+03:00) Istanbul",
        "(UTC+03:00) Kuwait, Riyadh",
        "(UTC+03:00) Minsk",
        "(UTC+03:00) Moscow, St. Petersburg",
        "(UTC+03:00) Nairobi",
        "(UTC+03:00) Volgograd",
        "(UTC+03:30) Tehran",
        "(UTC+04:00) Abu Dhabi, Muscat",
        "(UTC+04:00) Astrakhan, Ulyanovsk",
        "(UTC+04:00) Baku",
        "(UTC+04:00) Izhevsk, Samara",
        "(UTC+04:00) Port Louis",
        "(UTC+04:00) Saratov",
        "(UTC+04:00) Tbilisi",
        "(UTC+04:00) Yerevan",
        "(UTC+04:30) Kabul",
        "(UTC+05:00) Ashgabat, Tashkent",
        "(UTC+05:00) Ekaterinburg",
        "(UTC+05:00) Islamabad, Karachi",
        "(UTC+05:00) Qyzylorda",
        "(UTC+05:30) Chennai, Kolkata, Mumbai, New Delhi",
        "(UTC+05:30) Sri Jayawardenepura",
        "(UTC+05:45) Kathmandu",
        "(UTC+06:00) Astana",
        "(UTC+06:00) Dhaka",
        "(UTC+06:00) Omsk",
        "(UTC+06:30) Yangon (Rangoon)",
        "(UTC+07:00) Bangkok, Hanoi, Jakarta",
        "(UTC+07:00) Barnaul, Gorno-Altaysk",
        "(UTC+07:00) Hovd",
        "(UTC+07:00) Krasnoyarsk",
        "(UTC+07:00) Novosibirsk",
        "(UTC+07:00) Tomsk",
        "(UTC+08:00) Beijing, Chongqing, Hong Kong, Urumqi",
        "(UTC+08:00) Irkutsk",
        "(UTC+08:00) Kuala Lumpur, Singapore",
        "(UTC+08:00) Perth",
        "(UTC+08:00) Taipei",
        "(UTC+08:00) Ulaanbaatar",
        "(UTC+08:45) Eucla",
        "(UTC+09:00) Chita",
        "(UTC+09:00) Osaka, Sapporo, Tokyo",
        "(UTC+09:00) Pyongyang",
        "(UTC+09:00) Seoul",
        "(UTC+09:00) Yakutsk",
        "(UTC+09:30) Adelaide",
        "(UTC+09:30) Darwin",
        "(UTC+10:00) Brisbane",
        "(UTC+10:00) Canberra, Melbourne, Sydney",
        "(UTC+10:00) Guam, Port Moresby",
        "(UTC+10:00) Hobart",
        "(UTC+10:00) Vladivostok",
        "(UTC+10:30) Lord Howe Island",
        "(UTC+11:00) Bougainville Island",
        "(UTC+11:00) Chokurdakh",
        "(UTC+11:00) Magadan",
        "(UTC+11:00) Norfolk Island",
        "(UTC+11:00) Sakhalin",
        "(UTC+11:00) Solomon Is., New Caledonia",
        "(UTC+12:00) Anadyr, Petropavlovsk-Kamchatsky",
        "(UTC+12:00) Auckland, Wellington",
        "(UTC+12:00) Coordinated Universal Time+12",
        "(UTC+12:00) Fiji",
        "(UTC+12:45) Chatham Islands",
        "(UTC+13:00) Coordinated Universal Time+13",
        "(UTC+13:00) Nuku'alofa",
        "(UTC+13:00) Samoa",
        "(UTC+14:00) Kiritimati Island",
        "(UTC-01:00) Azores",
        "(UTC-01:00) Cabo Verde Is.",
        "(UTC-02:00) Coordinated Universal Time-02",
        "(UTC-03:00) Araguaina",
        "(UTC-03:00) Brasilia",
        "(UTC-03:00) Cayenne, Fortaleza",
        "(UTC-03:00) City of Buenos Aires",
        "(UTC-03:00) Greenland",
        "(UTC-03:00) Montevideo",
        "(UTC-03:00) Punta Arenas",
        "(UTC-03:00) Saint Pierre and Miquelon",
        "(UTC-03:00) Salvador",
        "(UTC-03:30) Newfoundland",
        "(UTC-04:00) Asuncion",
        "(UTC-04:00) Atlantic Time (Canada)",
        "(UTC-04:00) Caracas",
        "(UTC-04:00) Cuiaba",
        "(UTC-04:00) Georgetown, La Paz, Manaus, San Juan",
        "(UTC-04:00) Santiago",
        "(UTC-05:00) Bogota, Lima, Quito, Rio Branco",
        "(UTC-05:00) Chetumal",
        "(UTC-05:00) Eastern Time (US & Canada)",
        "(UTC-05:00) Haiti",
        "(UTC-05:00) Havana",
        "(UTC-05:00) Indiana (East)",
        "(UTC-05:00) Turks and Caicos",
        "(UTC-06:00) Central America",
        "(UTC-06:00) Central Time (US & Canada)",
        "(UTC-06:00) Easter Island",
        "(UTC-06:00) Guadalajara, Mexico City, Monterrey",
        "(UTC-06:00) Saskatchewan",
        "(UTC-07:00) Arizona",
        "(UTC-07:00) Chihuahua, La Paz, Mazatlan",
        "(UTC-07:00) Mountain Time (US & Canada)",
        "(UTC-07:00) Yukon",
        "(UTC-08:00) Baja California",
        "(UTC-08:00) Coordinated Universal Time-08",
        "(UTC-08:00) Pacific Time (US & Canada)",
        "(UTC-09:00) Alaska",
        "(UTC-09:00) Coordinated Universal Time-09",
        "(UTC-09:30) Marquesas Islands",
        "(UTC-10:00) Aleutian Islands",
        "(UTC-10:00) Hawaii",
        "(UTC-11:00) Coordinated Universal Time-11",
        "(UTC-12:00) International Date Line West"
    ],
    "Status": {
        "State": "Enabled",
        "Health": "Critical"
    },
    "PowerState": "On",
    "SerialConsole": {
        "ServiceEnabled": False
    },
    "FirmwareVersion": "1502",
    "ServiceIdentification": None,
    "NetworkProtocol": {
        "@odata.id": "/redfish/v1/Managers/CDU/NetworkProtocol"
    },
    "EthernetInterfaces": {
        "@odata.id": "/redfish/v1/Managers/CDU/EthernetInterfaces"
    },
    "Links": {
        "Oem": {
        }
    },
    "Actions": {
        "#Manager.ResetToDefaults": {
            "target": "/redfish/v1/Managers/CDU/Actions/Manager.ResetToDefaults",
            "ResetType@Redfish.AllowableValues": [
                "PreserveNetwork",
                "ResetAll",
                "PreserveNetworkAndUsers",
                "ClearLogs"
            ]
        },
        "#Manager.Reset": {
            "target": "/redfish/v1/Managers/CDU/Actions/Manager.Reset",
            "ResetType@Redfish.AllowableValues": [
                "ForceRestart",
                "GracefulRestart"
            ]
        },
        "Oem": {
        }
    },
    # "Oem": {
    #     "Supermicro": {
    #         "@odata.id": "/redfish/v1/Managers/CDU/Oem/Supermicro"
    #     }
    # },
    "@odata.id": "/redfish/v1/Managers/CDU"
}


managers_cdu_network_protocoldata ={
    "@odata.type": "#ManagerNetworkProtocol.v1_10_1.ManagerNetworkProtocol",
    "Id": "NetworkProtocol",
    "Name": "Manager Network Protocol",
    "Description": "Manager Network Service",
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "HostName": "aaaa",
    "HTTP": {
        "ProtocolEnabled": True,
        "Port": 80
    },
    "HTTPS": {
        "ProtocolEnabled": True,
        "Port": 443
    },
    "SSH": {
        "ProtocolEnabled": False,
        "Port": None
    },
    "SNMP": {
        "ProtocolEnabled": True,
        "Port": 161
    },
    "NTP": {
        "ProtocolEnabled": False,
        "NTPServers": [
            "time.google.com",
            "time1.google.com"
        ]
    },
    "SSDP": {
        "ProtocolEnabled": False,
        "Port": None,
        "NotifyMulticastIntervalSeconds": None,
        "NotifyTTL": None,
        "NotifyIPv6Scope": None
    },
    "Telnet": {
        "ProtocolEnabled": False,
        "Port": None
    },
    "DHCP": {
        "ProtocolEnabled": True,
        "Port": 67
    },
    "IPMI": {
        "ProtocolEnabled": False,
        "Port": 623
    },
    "Oem": {
    },
    "@odata.id": "/redfish/v1/Managers/CDU/NetworkProtocol"
}


ethernet_interfaces_data = {
    "@odata.type": "#EthernetInterfaceCollection.EthernetInterfaceCollection",
    "Name": "Ethernet Network Interface Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/Managers/CDU/EthernetInterfaces/Main"
        }
    ],
    "Oem": {
    },
    "@odata.id": "/redfish/v1/Managers/CDU/EthernetInterfaces"
}

ethernet_interfaces_main_data ={
    "@odata.type": "#EthernetInterface.v1_8_0.EthernetInterface",
    "Id": "Main",
    "Name": "Manager Ethernet Interface",
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "LinkStatus": "LinkUp",
    "InterfaceEnabled": True,
    "PermanentMACAddress": "e4-5f-01-3e-98-f8",
    "MACAddress": "e4-5f-01-3e-98-f8",
    "SpeedMbps": 1000,
    "AutoNeg": True,
    "FullDuplex": True,
    "MTUSize": 1500,
    "HostName": "aaaa",
    "FQDN": None,
    "MaxIPv6StaticAddresses": 1,
    "VLAN": {
        "VLANEnable": False,
        "VLANId": None
    },
    "IPv4Addresses": [
        {
            "Address": "10.163.65.58",
            "SubnetMask": "255.255.248.0",
            "AddressOrigin": "DHCP",
            "Gateway": "10.163.71.254",
            "Oem": {
            }
        }
    ],
    "IPv6AddressPolicyTable": [
        {
            "Prefix": "::1/128",
            "Precedence": 50,
            "Label": 0
        }
    ],
    "IPv6StaticAddresses": [
    ],
    "IPv6DefaultGateway": None,
    "IPv6Addresses": [
        {
            "Address": "fe80::e65f:1ff:fe3e:98f8",
            "PrefixLength": 64,
            "AddressOrigin": "DHCPv6",
            "AddressState": "Preferred",
            "Oem": {
            }
        }
    ],
    "NameServers": [
        "aaaa.dmtf.org"
    ],
    "Oem": {
    },
    "@odata.id": "/redfish/v1/Managers/CDU/EthernetInterfaces/Main"
}
redfish_data ={
    "v1": "/redfish/v1/"
}

LeakDetection_data = {
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection",
    "@odata.type": "#LeakDetection.LeakDetection",
    "Id": "LeakDetection",
    "Name": "Leak Detection",
    "Description": "LeakDetection",
    "Members@odata.count": 1,
    "Oem": {}
    # "Members": [
    #     {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection/LeakDetectors"}
    # ],   
}

LeakDetectionLeakDetectors_data = {
    "@odata.type": "#LeakDetectors.v1_6_0.LeakDetectors",
    "Id": "1",
    "Name": "LeakDetectors",
    "Status": {
        "State": "Enabled",
        "Health": "Critical"
    },
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection/LeakDetectors"  
}

odata_data = {
  "@odata.context": "/redfish/v1/$metadata",
  "value": [
    { "@odata.id": "/redfish/v1/AccountService" },
    { "@odata.id": "/redfish/v1/Chassis" },
    { "@odata.id": "/redfish/v1/Managers" },
    { "@odata.id": "/redfish/v1/SessionService" },
    { "@odata.id": "/redfish/v1/TelemetryService" },
    { "@odata.id": "/redfish/v1/ThermalEquipment" },
    { "@odata.id": "/redfish/v1/UpdateService" },
  ]    
}

@app.route("/redfish")
def redfish():
    return redfish_data
    

    
@redfish_ns.route("/")
class Root(Resource):
    # @requires_auth
    def get(self):
        odata_ver = request.headers.get('OData-Version')
        if odata_ver is not None and odata_ver != '4.0':
            return Response(status=412)
        
        resp = make_response(jsonify(root_data), 200)
        resp.headers['Allow'] = 'OPTIONS, GET, HEAD'
        resp.headers['Cache-Control'] = 'no-cache'
        return resp
        # return root_data

    # def head(self):
    #     resp = Response(status=200)
    #     resp.headers['Allow'] = 'OPTIONS, GET, HEAD'
    #     return resp
    
    
@redfish_ns.route('/odata')
class odata(Resource):
    def get(self):
        return odata_data

@redfish_ns.route('/$metadata')
class metadata(Resource):
    def get(self):
        with open('metadata.xml', 'rb') as f:
            xml = f.read()
        return Response(
            xml,
            status=200,
            mimetype='application/xml; charset=utf-8'
        )
   

# @redfish_ns.route("/redfish")
# class redfish(Resource):
#     def get(self):
#         return "redfish"
    
# @redfish_ns.route("/redfish/v1")
# class redfishv1(Resource):
#     def get(self):
#         return redfish_data
    
  
# --------------------------------------------
# thermal equipment
# -------------------------------------------- 

@redfish_ns.route("/ThermalEquipment")
class ThermalEquipment(Resource):
    # @requires_auth
    @redfish_ns.doc("thermal_equipment")
    def get(self):
        """get thermal equipment"""
        return ThermalEquipment_data
            
@redfish_ns.route("/ThermalEquipment/CDUs")
class ThermalEquipmentCdus(Resource):
    # @requires_auth
    @redfish_ns.doc("thermal_equipment_cdus")
    def get(self):
        return CDUs_data
    
@redfish_ns.route("/ThermalEquipment/CDUs/1")
class ThermalEquipmentCdus1(Resource):
    # @requires_auth
    @redfish_ns.doc("thermal_equipment_cdus")
    def get(self):
        
        return CDUs_data_1
    
@redfish_ns.route("/ThermalEquipment/CDUs/1/PrimaryCoolantConnectors")
class PrimaryCoolantConnectors(Resource):
    # @requires_auth
    @redfish_ns.doc("primary_coolant_connectors")
    def get(self):
        
        return PrimaryCoolantConnectors_data
    
@redfish_ns.route("/ThermalEquipment/CDUs/1/PrimaryCoolantConnectors/1")
class PrimaryCoolantConnectors1(Resource):
    # @requires_auth
    @redfish_ns.doc("primary_coolant_connectors_1")
    def get(self):
        
        return PrimaryCoolantConnectors_data_1

@redfish_ns.route("/ThermalEquipment/CDUs/1/Pumps")
class ThermalEquipmentCdus1Pumps(Resource):
    # @requires_auth
    @redfish_ns.doc("thermal_equipment_cdus_1_pumps")
    def get(self):    
        return cdus_pumps
    
#--------------------------pump1---------------------------------------- 
@redfish_ns.route("/ThermalEquipment/CDUs/1/Pumps/1")
class ThermalEquipmentCdus1Pumps1(Resource):
    # @requires_auth
    @redfish_ns.doc("thermal_equipment_cdus_1_pumps_1")
    def get(self):
        
        return cdus_pumps_1
        
    @requires_auth
    @redfish_ns.expect(pumpspeed_patch, validate=True)
    def patch(self):
        body = request.get_json(force=True)
        new_sp = body['pump_speed']
        new_sw = body['pump_switch']
        
        # 驗證範圍
        scp = cdus_pumps_1["SpeedControlPercent"]
        if not (scp["AllowableMin"] <= new_sp <= scp["AllowableMax"]):
            return {
                "error": f"pump_speed 必須介於 {scp['AllowableMin']} 和 {scp['AllowableMax']}"
            }, 400

        # 轉發到內部控制 API
        try:
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/control/pump1_speed",
                json={"pump_speed": new_sp, "pump_switch": new_sw},
                timeout=3
            )
            r.raise_for_status()
        except requests.RequestException as e:
            return {"error":"CDU 控制服務失敗","details":str(e)}, 502

        # 更新內存資料
        scp["SetPoint"] = new_sp
        # pump_switch 控制 State
        cdus_pumps_1["Status"]["State"] = "Enabled" if new_sw else "Disabled"

        # 回傳整個 Pump 資源
        return cdus_pumps_1, 200

#--------------------------pump2---------------------------------------- 
@redfish_ns.route("/ThermalEquipment/CDUs/1/Pumps/2")
class ThermalEquipmentCdus1Pumps2(Resource):
    # @requires_auth
    @redfish_ns.doc("thermal_equipment_cdus_1_pumps_2")
    def get(self):
        
        return cdus_pumps_2
        
    @requires_auth
    @redfish_ns.expect(pumpspeed_patch, validate=True)
    def patch(self):
        body = request.get_json(force=True)
        new_sp = body['pump_speed']
        new_sw = body['pump_switch']
        
        # 驗證範圍
        scp = cdus_pumps_2["SpeedControlPercent"]
        if not (scp["AllowableMin"] <= new_sp <= scp["AllowableMax"]):
            return {
                "error": f"pump_speed 必須介於 {scp['AllowableMin']} 和 {scp['AllowableMax']}"
            }, 400

        # 轉發到內部控制 API
        try:
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/control/pump2_speed",
                json={"pump_speed": new_sp, "pump_switch": new_sw},
                timeout=3
            )
            r.raise_for_status()
        except requests.RequestException as e:
            return {"error":"CDU 控制服務失敗","details":str(e)}, 502

        # 更新內存資料
        scp["SetPoint"] = new_sp
        # pump_switch 控制 State
        cdus_pumps_2["Status"]["State"] = "Enabled" if new_sw else "Disabled"

        # 回傳整個 Pump 資源
        return cdus_pumps_2, 200


#--------------------------pump3---------------------------------------- 
@redfish_ns.route("/ThermalEquipment/CDUs/1/Pumps/3")
class ThermalEquipmentCdus1Pumps3(Resource):
    # @requires_auth
    @redfish_ns.doc("thermal_equipment_cdus_1_pumps_3")
    def get(self):
        
        return cdus_pumps_3
        
    @requires_auth
    @redfish_ns.expect(pumpspeed_patch, validate=True)
    def patch(self):
        body = request.get_json(force=True)
        new_sp = body['pump_speed']
        new_sw = body['pump_switch']
        
        # 驗證範圍
        scp = cdus_pumps_3["SpeedControlPercent"]
        if not (scp["AllowableMin"] <= new_sp <= scp["AllowableMax"]):
            return {
                "error": f"pump_speed 必須介於 {scp['AllowableMin']} 和 {scp['AllowableMax']}"
            }, 400

        # 轉發到內部控制 API
        try:
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/control/pump3_speed",
                json={"pump_speed": new_sp, "pump_switch": new_sw},
                timeout=3
            )
            r.raise_for_status()
        except requests.RequestException as e:
            return {"error":"CDU 控制服務失敗","details":str(e)}, 502

        # 更新內存資料
        scp["SetPoint"] = new_sp
        # pump_switch 控制 State
        cdus_pumps_3["Status"]["State"] = "Enabled" if new_sw else "Disabled"

        # 回傳整個 Pump 資源
        return cdus_pumps_3, 200

    
    
@redfish_ns.route("/ThermalEquipment/CDUs/1/Filters")
class ThermalEquipmentCdus1Filters(Resource):
    # @requires_auth
    @redfish_ns.doc("thermal_equipment_cdus_1_filters")
    def get(self):
        
        return cdus_filters
    
@redfish_ns.route("/ThermalEquipment/CDUs/1/Filters/1")
class ThermalEquipmentCdus1Filters1(Resource):
    # @requires_auth
    @redfish_ns.doc("thermal_equipment_cdus_1_filters_1")
    def get(self):
        
        return cdus_filters_1
    
@redfish_ns.route("/ThermalEquipment/CDUs/1/EnvironmentMetrics")
class ThermalEquipmentCdus1EnvironmentMetrics(Resource):
    # @requires_auth
    @redfish_ns.doc("thermal_equipment_cdus_1_environment_metrics")
    def get(self):
        
        return environment_metrics
    
@redfish_ns.route("/ThermalEquipment/CDUs/1/Reservoirs")
class ThermalEquipmentCdus1Reservoirs(Resource):
    # @requires_auth
    @redfish_ns.doc("thermal_equipment_cdus_1_reservoirs")
    def get(self):
        
        return reservoirs
    
    
@redfish_ns.route("/ThermalEquipment/CDUs/1/Reservoirs/1")
class ThermalEquipmentCdus1Reservoirs1(Resource):
    # @requires_auth
    @redfish_ns.doc("thermal_equipment_cdus_1_reservoirs_1")
    def get(self):
        
        return reservoirs_1

@redfish_ns.route("/ThermalEquipment/CDUs/1/LeakDetection")
class LeakDetection(Resource):
    # @requires_auth
    @redfish_ns.doc("thermal_equipment_cdus_1_LeakDetection")
    def get(self):
        
        return LeakDetection_data    

@redfish_ns.route("/ThermalEquipment/CDUs/1/LeakDetection/LeakDetectors")
class LeakDetectionLeakDetectors(Resource):
    # @requires_auth
    @redfish_ns.doc("thermal_equipment_cdus_1_LeakDetection_LeakDetectors")
    def get(self):
        
        return LeakDetectionLeakDetectors_data    
 
 
 
# --------------------------------------------
# managers
# -------------------------------------------- 
@redfish_ns.route("/Managers")
class Managers(Resource):
    # @requires_auth
    @redfish_ns.doc("managers")
    def get(self):
        
        return managers_data
       
@redfish_ns.route("/Managers/CDU")
class ManagersCDU(Resource):
    # @requires_auth
    @redfish_ns.doc("managers_cdu")
    def get(self):
        
        return managers_cdu_data

@redfish_ns.route("/Managers/CDU/NetworkProtocol")
class ManagersCDUNetworkProtocol(Resource):
    # @requires_auth
    @redfish_ns.doc("managers_cdu_network_protocol")
    def get(self):
        
        return managers_cdu_network_protocoldata
        
@redfish_ns.route("/Managers/CDU/EthernetInterfaces")
class ManagersCDUEthernetInterfaces(Resource):
    # @requires_auth
    @redfish_ns.doc("managers_cdu_ethernet_interfaces")
    def get(self):
        
        return ethernet_interfaces_data
    
@redfish_ns.route("/Managers/CDU/EthernetInterfaces/Main")
class ManagersCDUEthernetInterfacesMain(Resource):
    # @requires_auth
    @redfish_ns.doc("managers_cdu_ethernet_interfaces")
    def get(self):
        
        return ethernet_interfaces_main_data
    
           


# --------------------------------------------
# chassis
# -------------------------------------------- 
Chassis_data = {
    "@odata.type": "#ChassisCollection.ChassisCollection",
    "Name": "Chassis Collection",
    "Members@odata.count": 1,
    "Members": [{"@odata.id": "/redfish/v1/Chassis/1"}],
    "@odata.id": "/redfish/v1/Chassis",
}

Chassis_data_1 = {
    "@odata.type": "#Chassis.v1_25_2.Chassis",
    "Id": "1",
    "Name": "Catfish System Chassis",
    "ChassisType": "RackMount",
    "Manufacturer": "Supermicro",
    "Model": "YellowCat1000",
    "SerialNumber": "24701 011001",
    "PartNumber": "test_1",
    "AssetTag": "CATFISHASSETTAG",
    "LocationIndicatorActive": True,
    "PowerState": "On",
    "Status": {"State": "Enabled", "Health": "OK"},
    "PowerSubsystem": {"@odata.id": "/redfish/v1/Chassis/1/PowerSubsystem"},
    "ThermalSubsystem": {"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem"},
    "EnvironmentMetrics": {
        "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/EnvironmentMetrics"
    },
    "Sensors": {"@odata.id": "/redfish/v1/Chassis/1/Sensors"},
    "Oem": {
        "LeakDetection": {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection"},
        "Pumps": {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps"},
        "PrimaryCoolantConnectors": {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/PrimaryCoolantConnectors"},
        "Reservoirs": {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Reservoirs"},
    },
    # "LeakDetection": {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection"},
    # "Pumps": {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps"},
    # "PrimaryCoolantConnectors": {
    #     "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/PrimaryCoolantConnectors"
    # },
    # "SecondaryCoolantConnectors": {
    #     "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/SecondaryCoolantConnectors"
    # },
    # "Reservoirs": {"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Reservoirs"},
    "Controls": {"@odata.id": "/redfish/v1/Chassis/1/Controls"},
    "Links": {
        "ManagedBy": [{"@odata.id": "/redfish/v1/Managers/CDU"}],
        "CoolingUnits": [{"@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1"}],
    },
    "@Redfish.WriteableProperties": ["LocationIndicatorActive"],
    "@odata.id": "/redfish/v1/Chassis/1",
}

PowerSubsystem_data = {
    "@odata.id": "/redfish/v1/Chassis/1/PowerSubsystem",
    "@odata.type": "#PowerSubsystem.v1_1_2.PowerSubsystem",
    "Id": "PowerSubsystem",
    "Name": "Chassis Power Subsystem",
    "CapacityWatts": 92.0,
    "PowerSupplies": {
        "@odata.id": "/redfish/v1/Chassis/1/PowerSubsystem/PowerSupplies"
    },
    "Status": {"State": "Enabled", "Health": "OK"},
}

PowerSupplies_data = {
    "@odata.id": "/redfish/v1/Chassis/1/PowerSubsystem/PowerSupplies",
    "@odata.type": "#PowerSupplyCollection.PowerSupplyCollection",
    "Name": "Power Supply Collection",
    "Members@odata.count": 2,
    "Members": [
        {"@odata.id": "/redfish/v1/Chassis/1/PowerSubsystem/PowerSupplies/1"},
        {"@odata.id": "/redfish/v1/Chassis/1/PowerSubsystem/PowerSupplies/2"},
    ],
}

PowerSupplies_data_1 = {
    "@odata.type": "#PowerSupply.v1_6_0.PowerSupply",
    "Id": "1",
    "Name": "System Power Control",
    "Status": {"State": "Enabled", "Health": "OK"},
    "@odata.id": "/redfish/v1/Chassis/1/PowerSubsystem/PowerSupplies/1",
}

PowerSupplies_data_2 = {
    "@odata.type": "#PowerSupply.v1_6_0.PowerSupply",
    "Id": "2",
    "Name": "System Power Control",
    "Status": {"State": "Enabled", "Health": "OK"},
    "@odata.id": "/redfish/v1/Chassis/1/PowerSubsystem/PowerSupplies/2",
}

ThermalSubsystem_data = {
    "@odata.context": "/redfish/v1/$metadata#ThermalSubsystem.ThermalSubsystem",
    "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem",
    "@odata.type": "#ThermalSubsystem.v1_3_2.ThermalSubsystem",
    "Id": "ThermalSubsystem",
    "Name": "Thermal Subsystem",
    "Fans": {"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans"},
    "Status": {"State": "Enabled", "Health": "OK"},
    "Oem": {},
}

ThermalSubsystem_Fans_data = {
    "@odata.context": "/redfish/v1/$metadata#Fans.FanCollection",
    "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans",
    "@odata.type": "#FanCollection.FanCollection",
    "Name": "Fans Collection",
    "Members@odata.count": 8,
    "Members": [
        {"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/1"},
        {"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/2"},
        {"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/3"},
        {"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/4"},
        {"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/5"},
        {"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/6"},
        {"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/7"},
        {"@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/8"},
    ],
}

Fans_data = {
    "Fan1": {
        "@odata.type": "#Fan.v1_5_0.Fan",
        "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/1",
        "Id": "1",
        "Name": "Fan Right 1",
        "PhysicalContext": "Chassis",
        "Status": {"State": "Enabled", "Health": "OK"},
        "FanSpeedPercent": {"@odata.id": "/redfish/v1/Chassis/1/Sensors_data_all/fan1"},
        # "FirmwareVersion": "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/1/1",
        # "ServiceHours": 3833.48,
        "Location": {"PartLocation": {"ServiceLabel": "Fan 2", "LocationType": "Bay"}},
        # "SpeedControlPercent": {
        #     "SetPoint": 44,
        #     "AllowableMax": 100,
        #     "AllowableMin": 0,
        #     "ControlMode": "Disabled",
        # },
    },
    "Fan2": {
        "@odata.type": "#Fan.v1_5_0.Fan",
        "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/2",
        "Id": "2",
        "Name": "Fan Right 2",
        "PhysicalContext": "Chassis",
        "Status": {"State": "Enabled", "Health": "OK"},
        # "FanSpeedPercent": {"Reading": 0, "SpeedRPM": 0},
        # "FirmwareVersion": "1100",
        # "ServiceHours": 3833.48,
        "Location": {"PartLocation": {"ServiceLabel": "Fan 2", "LocationType": "Bay"}},
        # "SpeedControlPercent": {
        #     "SetPoint": 44,
        #     "AllowableMax": 100,
        #     "AllowableMin": 0,
        #     "ControlMode": "Disabled",
        # },
    },
    "Fan3": {
        "@odata.type": "#Fan.v1_5_0.Fan",
        "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/3",
        "Id": "3",
        "Name": "Fan Right 3",
        "PhysicalContext": "Chassis",
        "Status": {"State": "Enabled", "Health": "OK"},
        # "FanSpeedPercent": {"Reading": 0, "SpeedRPM": 0},
        # "FirmwareVersion": "1100",
        # "ServiceHours": 3833.48,
        "Location": {"PartLocation": {"ServiceLabel": "Fan 2", "LocationType": "Bay"}},
        # "SpeedControlPercent": {
        #     "SetPoint": 44,
        #     "AllowableMax": 100,
        #     "AllowableMin": 0,
        #     "ControlMode": "Disabled",
        # },
    },
    "Fan4": {
        "@odata.type": "#Fan.v1_5_0.Fan",
        "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/4",
        "Id": "4",
        "Name": "Fan Right 4",
        "PhysicalContext": "Chassis",
        "Status": {"State": "Enabled", "Health": "OK"},
        # "FanSpeedPercent": {"Reading": 0, "SpeedRPM": 0},
        # "FirmwareVersion": "1100",
        # "ServiceHours": 3833.48,
        "Location": {"PartLocation": {"ServiceLabel": "Fan 2", "LocationType": "Bay"}},
        # "SpeedControlPercent": {
        #     "SetPoint": 44,
        #     "AllowableMax": 100,
        #     "AllowableMin": 0,
        #     "ControlMode": "Disabled",
        # },
    },
    "Fan5": {
        "@odata.type": "#Fan.v1_5_0.Fan",
        "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/5",
        "Id": "5",
        "Name": "Fan Left 1",
        "PhysicalContext": "Chassis",
        "Status": {"State": "Enabled", "Health": "OK"},
        # "FanSpeedPercent": {"Reading": 0, "SpeedRPM": 0},
        # "FirmwareVersion": "1100",
        # "ServiceHours": 3833.48,
        "Location": {"PartLocation": {"ServiceLabel": "Fan 2", "LocationType": "Bay"}},
        # "SpeedControlPercent": {
        #     "SetPoint": 44,
        #     "AllowableMax": 100,
        #     "AllowableMin": 0,
        #     "ControlMode": "Disabled",
        # },
    },
    "Fan6": {
        "@odata.type": "#Fan.v1_5_0.Fan",
        "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/6",
        "Id": "6",
        "Name": "Fan Left 2",
        "PhysicalContext": "Chassis",
        "Status": {"State": "Enabled", "Health": "OK"},
        # "FanSpeedPercent": {"Reading": 0, "SpeedRPM": 0},
        # "FirmwareVersion": "1100",
        # "ServiceHours": 3833.48,
        "Location": {"PartLocation": {"ServiceLabel": "Fan 2", "LocationType": "Bay"}},
        # "SpeedControlPercent": {
        #     "SetPoint": 44,
        #     "AllowableMax": 100,
        #     "AllowableMin": 0,
        #     "ControlMode": "Disabled",
        # },
    },
    "Fan7": {
        "@odata.type": "#Fan.v1_5_0.Fan",
        "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/7",
        "Id": "7",
        "Name": "Fan Left 3",
        "PhysicalContext": "Chassis",
        "Status": {"State": "Enabled", "Health": "OK"},
        # "FanSpeedPercent": {"Reading": 0, "SpeedRPM": 0},
        # "FirmwareVersion": "1100",
        # "ServiceHours": 3833.48,
        "Location": {"PartLocation": {"ServiceLabel": "Fan 2", "LocationType": "Bay"}},
        # "SpeedControlPercent": {
        #     "SetPoint": 44,
        #     "AllowableMax": 100,
        #     "AllowableMin": 0,
        #     "ControlMode": "Disabled",
        # },
    },
    "Fan8": {
        "@odata.type": "#Fan.v1_5_0.Fan",
        "@odata.id": "/redfish/v1/Chassis/1/ThermalSubsystem/Fans/8",
        "Id": "8",
        "Name": "Fan Left 4",
        "PhysicalContext": "Chassis",
        "Status": {"State": "Enabled", "Health": "OK"},
        # "FanSpeedPercent": {"Reading": 0, "SpeedRPM": 0},
        # "FirmwareVersion": "1100",
        # "ServiceHours": 3833.48,
        "Location": {"PartLocation": {"ServiceLabel": "Fan 2", "LocationType": "Bay"}},
        # "SpeedControlPercent": {
        #     "SetPoint": 44,
        #     "AllowableMax": 100,
        #     "AllowableMin": 0,
        #     "ControlMode": "Disabled",
        # },
    },
}

## 
# move to rf_chassis_service.py
##
# sensor_collection_data = {
#     "@odata.type": "#SensorCollection.SensorCollection",
#     "Name": "Sensor Collection",
#     "Members@odata.count": 11,
#     "Members": [
#         {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryFlowLitersPerMinute"},
#         {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryHeatRemovedkW"},
#         {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimarySupplyTemperatureCelsius"},
#         {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryReturnTemperatureCelsius"},
#         {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryDeltaTemperatureCelsius"},
#         {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimarySupplyPressurekPa"},
#         {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryReturnPressurekPa"},
#         {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryDeltaPressurekPa"},
#         {"@odata.id": "/redfish/v1/Chassis/1/Sensors/TemperatureCelsius"},
#         {"@odata.id": "/redfish/v1/Chassis/1/Sensors/DewPointCelsius"},
#         {"@odata.id": "/redfish/v1/Chassis/1/Sensors/HumidityPercent"},
#         {"@odata.id": "/redfish/v1/Chassis/1/Sensors/WaterPH"},
#         {"@odata.id": "/redfish/v1/Chassis/1/Sensors/Conductivity"},
#         {"@odata.id": "/redfish/v1/Chassis/1/Sensors/Turbidity"},
#         {"@odata.id": "/redfish/v1/Chassis/1/Sensors/PowerConsume"},
#     ],
#     "Oem": {},
#     "@odata.id": "/redfish/v1/Chassis/1/Sensors",
# }

Sensors_data_all = {
    "PrimaryFlowLitersPerMinute": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimaryFlowLitersPerMinute",
        "Name": "Primary Flow Liters Per Minute",
        "Reading": 0.1,
        "ReadingUnits": "L/min",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryFlowLitersPerMinute",
    },
    "PrimaryHeatRemovedkW": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimaryHeatRemovedkW",
        "Name": "Primary Heat Removed kW",
        "Reading": 0.2,
        "ReadingUnits": "kW",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryHeatRemovedkW",
    },
    "PrimarySupplyTemperatureCelsius": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimarySupplyTemperatureCelsius",
        "Name": "Primary Supply Temperature Celsius",
        "Reading": 23.32,
        "ReadingUnits": "Celsius",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimarySupplyTemperatureCelsius",
    },
    "PrimaryReturnTemperatureCelsius": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimaryReturnTemperatureCelsius",
        "Name": "Primary Return Temperature Celsius",
        "Reading": 23.45,
        "ReadingUnits": "Celsius",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryReturnTemperatureCelsius",
    },
    "PrimaryDeltaTemperatureCelsius": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimaryDeltaTemperatureCelsius",
        "Name": "Primary Delta Temperature Celsius",
        "Reading": 0.13,
        "ReadingUnits": "Celsius",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryDeltaTemperatureCelsius",
    },
    "PrimarySupplyPressurekPa": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimarySupplyPressurekPa",
        "Name": "Primary Supply Pressure kPa",
        "Reading": 220.0,
        "ReadingUnits": "kPa",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimarySupplyPressurekPa",
    },
    "PrimaryReturnPressurekPa": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimaryReturnPressurekPa",
        "Name": "Primary Return Pressure kPa",
        "Reading": 85.0,
        "ReadingUnits": "kPa",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryReturnPressurekPa",
    },
    "PrimaryDeltaPressurekPa": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PrimaryDeltaPressurekPa",
        "Name": "Primary Delta Pressure kPa",
        "Reading": 0,
        "ReadingUnits": "kPa",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryDeltaPressurekPa",
    },
    "TemperatureCelsius": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "TemperatureCelsius",
        "Name": "Temperature Celsius",
        "Reading": 23.98,
        "ReadingUnits": "Celsius",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/TemperatureCelsius",
    },
    "DewPointCelsius": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "DewPointCelsius",
        "Name": "Dew Point Celsius",
        "Reading": 14.87,
        "ReadingUnits": "Celsius",
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/DewPointCelsius",
    },
    "HumidityPercent": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "HumidityPercent",
        "Name": "Humidity Percent",
        "Reading": 56.73,
        "ReadingUnits": "Percent",
        "Status": {"Health": "OK", "State": "Enabled"},
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/HumidityPercent",
    },
    "WaterPH": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "WaterPH",
        "Name": "Water PH",
        "Reading": 7.5,
        "ReadingUnits": "pH",
        "Status": {"Health": "OK", "State": "Enabled"},
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/WaterPH",
    },
    "Conductivity": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "Conductivity",
        "Name": "Conductivity",
        "Reading": 8000.0,
        "ReadingUnits": "μs/cm",
        "Status": {"Health": "OK", "State": "Enabled"},
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/Conductivity",
    },
    "Turbidity": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "Turbidity",
        "Name": "Turbidity",
        "Reading": 9600.0,
        "ReadingUnits": "NTU",
        "Status": {"Health": "OK", "State": "Enabled"},
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/Turbidity",
    },
    "PowerConsume": {
        "@odata.type": "#Sensor.v1_1_0.Sensor",
        "Id": "PowerConsume",
        "Name": "PowerConsume",
        "Reading": 7.0,
        "ReadingUnits": "kW",
        "Status": {"Health": "OK", "State": "Enabled"},
        "@odata.id": "/redfish/v1/Chassis/1/Sensors/PowerConsume",
    },
}

Controls_data = {
    "@odata.type": "#ControlCollection.ControlCollection",
    "Name": "Control Collection",
    "Members@odata.count": 3,
    "Members": [
        {"@odata.id": "/redfish/v1/Chassis/1/Controls/OperationMode"},
        {"@odata.id": "/redfish/v1/Chassis/1/Controls/PumpsSpeedControl"},
        {"@odata.id": "/redfish/v1/Chassis/1/Controls/FansSpeedControl"},
    ],
    "@odata.id": "/redfish/v1/Chassis/1/Controls",
}

Controls_data_all = {
    "OperationMode": {
        "@odata.type": "#Control.v1_5_1.Control",
        "Id": "OperationMode",
        "Name": "OperationMode",
        "PhysicalContext": "Chassis",
        "ControlMode": "Manual",
        "@odata.id": "/redfish/v1/Chassis/1/Controls/OperationMode",
    },
    "PumpsSpeedControl": {
        "@odata.type": "#Control.v1_5_1.Control",
        "Id": "PumpsSpeedControl",
        "Name": "PumpsSpeed",
        "PhysicalContext": "Chassis",
        # "ControlType": "Valve",
        "ControlMode": "Manual",
        "SetPoint": 35,
        "SetPointUnits": "%",
        "AllowableMax": 100,
        "AllowableMin": 0,
        "@odata.id": "/redfish/v1/Chassis/1/Controls/PumpsSpeedControl",
    },
    "FansSpeedControl": {
        "@odata.type": "#Control.v1_5_1.Control",
        "Id": "FansSpeedControl",
        "Name": "FansSpeed",
        "PhysicalContext": "Chassis",
        # "ControlType": "Valve",
        "ControlMode": "Manual",
        "SetPoint": 35,
        "SetPointUnits": "%",
        "AllowableMax": 100,
        "AllowableMin": 0,
        "@odata.id": "/redfish/v1/Chassis/1/Controls/FansSpeedControl",
    },
}

# OperationMode patch設置
OperationMode_patch = redfish_ns.model('OperationModePatch', {
    'mode': fields.String(
        required=True,
        description='模式控制',
        default='auto',   # 這裡設定預設值
        example='auto',   # 也可加 example，讓 UI 顯示範例
        enum=['auto', 'manual', 'stop']  # 如果有固定選項，也可以列出
    ),
})

# fanspeed patch設置
fanspeed_patch = redfish_ns.model('FanSpeedControlPatch', {
    'fan_speed': fields.Integer(
        required=True,
        description='風扇轉速百分比 (0–100)',
        min=0, max=100
    ),
})




@redfish_ns.route("/Chassis")
class Chassis(Resource):
    @requires_auth
    def get(self):
        return Chassis_data


@redfish_ns.route("/Chassis/1")
class Chassis1(Resource):
    @requires_auth
    def get(self):
        return Chassis_data_1


@redfish_ns.route("/Chassis/1/PowerSubsystem")
class PowerSubsystem(Resource):
    @requires_auth
    def get(self):
        return PowerSubsystem_data


@redfish_ns.route("/Chassis/1/PowerSubsystem/PowerSupplies")
class PowerSupplies(Resource):
    @requires_auth
    def get(self):
        return PowerSupplies_data


@redfish_ns.route("/Chassis/1/PowerSubsystem/PowerSupplies/1")
class PowerSupplies1(Resource):
    @requires_auth
    def get(self):
        return PowerSupplies_data_1


@redfish_ns.route("/Chassis/1/PowerSubsystem/PowerSupplies/2")
class PowerSupplies2(Resource):
    @requires_auth
    def get(self):
        return PowerSupplies_data_2


@redfish_ns.route("/Chassis/1/ThermalSubsystem")
class ThermalSubsystem(Resource):
    @requires_auth
    def get(self):
        return ThermalSubsystem_data


@redfish_ns.route("/Chassis/1/ThermalSubsystem/Fans")
class ThermalSubsystem_Fans(Resource):
    @requires_auth
    def get(self):
        return ThermalSubsystem_Fans_data


@redfish_ns.route("/Chassis/1/ThermalSubsystem/Fans/1")
class ThermalSubsystem_Fans_1(Resource):
    @requires_auth
    def get(self):
        rep = Fans_data["Fan1"]
        
        return rep


@redfish_ns.route("/Chassis/1/ThermalSubsystem/Fans/2")
class ThermalSubsystem_Fans_2(Resource):
    @requires_auth
    def get(self):
        return Fans_data["Fan2"]


@redfish_ns.route("/Chassis/1/ThermalSubsystem/Fans/3")
class ThermalSubsystem_Fans_3(Resource):
    @requires_auth
    def get(self):
        return Fans_data["Fan3"]


@redfish_ns.route("/Chassis/1/ThermalSubsystem/Fans/4")
class ThermalSubsystem_Fans_4(Resource):
    @requires_auth
    def get(self):
        return Fans_data["Fan4"]


@redfish_ns.route("/Chassis/1/ThermalSubsystem/Fans/5")
class ThermalSubsystem_Fans_5(Resource):
    @requires_auth
    def get(self):
        return Fans_data["Fan5"]


@redfish_ns.route("/Chassis/1/ThermalSubsystem/Fans/6")
class ThermalSubsystem_Fans_6(Resource):
    @requires_auth
    def get(self):
        return Fans_data["Fan6"]


@redfish_ns.route("/Chassis/1/ThermalSubsystem/Fans/7")
class ThermalSubsystem_Fans_7(Resource):
    @requires_auth
    def get(self):
        return Fans_data["Fan7"]


@redfish_ns.route("/Chassis/1/ThermalSubsystem/Fans/8")
class ThermalSubsystem_Fans_8(Resource):
    @requires_auth
    def get(self):
        return Fans_data["Fan8"]


@redfish_ns.route("/Chassis/<chassis_id>/Sensors")
class Sensors(Resource):
    @requires_auth
    def get(self, chassis_id):
        chassis_service = RfChassisService()
        return chassis_service.fetch_sensors_collection(chassis_id)


@redfish_ns.route("/Chassis/<chassis_id>/Sensors/<sensor_id>")
class FetchSensorsById(Resource):
    @requires_auth
    def get(self, chassis_id, sensor_id):
        chassis_service = RfChassisService()
        return chassis_service.fetch_sensors_by_name(chassis_id, sensor_id)

# @redfish_ns.route("/Chassis/<chassis_id>/Sensors/PrimaryFlowLitersPerMinute")
# class Sensors_PrimaryFlowLitersPerMinute(Resource):
#     @requires_auth
#     def get(self, chassis_id):
#         # to be continue
#         # chassis_service = RfChassisService()
#         # return chassis_service.fetch_sensors_by_name(chassis_id, "PrimaryFlowLitersPerMinute")

#         return Sensors_data_all["PrimaryFlowLitersPerMinute"]

# @redfish_ns.route("/Chassis/1/Sensors/PrimaryHeatRemovedkW")
# class Sensors_PrimaryHeatRemovedkW(Resource):
#     @requires_auth
#     def get(self):
#         return Sensors_data_all["PrimaryHeatRemovedkW"]


# @redfish_ns.route("/Chassis/1/Sensors/PrimarySupplyTemperatureCelsius")
# class Sensors_PrimarySupplyTemperatureCelsius(Resource):
#     @requires_auth
#     def get(self):
#         return Sensors_data_all["PrimarySupplyTemperatureCelsius"]


# @redfish_ns.route("/Chassis/1/Sensors/PrimaryReturnTemperatureCelsius")
# class Sensors_PrimaryReturnTemperatureCelsius(Resource):
#     @requires_auth
#     def get(self):
#         return Sensors_data_all["PrimaryReturnTemperatureCelsius"]


# @redfish_ns.route("/Chassis/1/Sensors/PrimaryDeltaTemperatureCelsius")
# class Sensors_PrimaryDeltaTemperatureCelsius(Resource):
#     @requires_auth
#     def get(self):
#         return Sensors_data_all["PrimaryDeltaTemperatureCelsius"]


# @redfish_ns.route("/Chassis/1/Sensors/PrimarySupplyPressurekPa")
# class Sensors_PrimarySupplyPressurekPa(Resource):
#     @requires_auth
#     def get(self):
#         return Sensors_data_all["PrimarySupplyPressurekPa"]


# @redfish_ns.route("/Chassis/1/Sensors/PrimaryReturnPressurekPa")
# class Sensors_PrimaryReturnPressurekPa(Resource):
#     @requires_auth
#     def get(self):
#         return Sensors_data_all["PrimaryReturnPressurekPa"]


# @redfish_ns.route("/Chassis/1/Sensors/PrimaryDeltaPressurekPa")
# class Sensors_PrimaryDeltaPressurekPa(Resource):
#     @requires_auth
#     def get(self):
#         return Sensors_data_all["PrimaryDeltaPressurekPa"]


# @redfish_ns.route("/Chassis/1/Sensors/TemperatureCelsius")
# class Sensors_TemperatureCelsius(Resource):
#     @requires_auth
#     def get(self):
#         return Sensors_data_all["TemperatureCelsius"]


# @redfish_ns.route("/Chassis/1/Sensors/DewPointCelsius")
# class Sensors_DewPointCelsius(Resource):
#     @requires_auth
#     def get(self):
#         return Sensors_data_all["DewPointCelsius"]


# @redfish_ns.route("/Chassis/1/Sensors/HumidityPercent")
# class Sensors_HumidityPercent(Resource):
#     @requires_auth
#     def get(self):
#         return Sensors_data_all["HumidityPercent"]


# @redfish_ns.route("/Chassis/1/Sensors/WaterPH")
# class Sensors_WaterPH(Resource):
#     @requires_auth
#     def get(self):
        
#         return Sensors_data_all["WaterPH"]


# @redfish_ns.route("/Chassis/1/Sensors/Conductivity")
# class Sensors_Conductivity(Resource):
#     @requires_auth
#     def get(self):
#         return Sensors_data_all["Conductivity"]


# @redfish_ns.route("/Chassis/1/Sensors/Turbidity")
# class Sensors_Turbidity(Resource):
#     @requires_auth
#     def get(self):
#         return Sensors_data_all["Turbidity"]


# @redfish_ns.route("/Chassis/1/Sensors/PowerConsume")
# class Sensors_PowerConsume(Resource):
#     @requires_auth
#     def get(self):
#         return Sensors_data_all["PowerConsume"]


@redfish_ns.route("/Chassis/1/Controls")
class Controls(Resource):
    @requires_auth
    def get(self):
        return Controls_data


@redfish_ns.route("/Chassis/1/Controls/OperationMode")
class OperationMode(Resource):
    @requires_auth
    def get(self):
        return Controls_data_all["OperationMode"]
    
    @redfish_ns.expect(OperationMode_patch, validate=True)
    @requires_auth
    def patch(self):
        payload = request.get_json(force=True)
        new_sp = payload["mode"]

        try:
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/status/op_mode",
                json={"mode": new_sp},  
                timeout=3
            )
            r.raise_for_status()
        except requests.RequestException as e:
            # 如果轉發失敗，就回 502 Bad Gateway
            return {"error": "轉發到 CDU 控制服務失敗", "details": str(e)}, 502

        # 內部服務回傳 OK，更新 Redfish 內存資料
        Controls_data_all["PumpsSpeedControl"]["SetPoint"] = new_sp

        # 回傳更新後的 Redfish Control 資源
        return Controls_data_all["PumpsSpeedControl"], 200
    

@redfish_ns.route("/Chassis/1/Controls/PumpsSpeedControl")
class PumpsSpeedControl(Resource):
    @requires_auth
    def get(self):
        return Controls_data_all["PumpsSpeedControl"]



@redfish_ns.route("/Chassis/1/Controls/FansSpeedControl")
class FansSpeedControl(Resource):
    @requires_auth
    def get(self):
        return Controls_data_all["FansSpeedControl"]
    
    @redfish_ns.expect(fanspeed_patch, validate=True)
    @requires_auth
    def patch(self):
        payload = request.get_json(force=True)
        new_sp = payload["fan_speed"]

        try:
            r = requests.patch(
                f"{CDU_BASE}/api/v1/cdu/control/fan_speed",
                json={"fan_speed": new_sp},  
                timeout=3
            )
            r.raise_for_status()
        except requests.RequestException as e:
            # 如果轉發失敗，就回 502 Bad Gateway
            return {"error": "轉發到 CDU 控制服務失敗", "details": str(e)}, 502

        # 內部服務回傳 OK，更新 Redfish 內存資料
        Controls_data_all["FansSpeedControl"]["SetPoint"] = new_sp

        # 回傳更新後的 Redfish Control 資源
        return Controls_data_all["FansSpeedControl"], 200


# --------------------------------------------
# AccountService
# --------------------------------------------
AccountService_data= {
	"@odata.type": "#AccountService.v1_8_0.AccountService",
	"@odata.id": "/redfish/v1/AccountService",
	"Id": "AccountService",
	"Name": "Account Service",
	"Description": "Account Service",
	"Status": {
		"State": "Enabled",
		"Health": "OK"
	},
	"ServiceEnabled": True,
	"AuthFailureLoggingThreshold": 10,
	"MinPasswordLength": 1,
	"AccountLockoutThreshold": 10,
	"AccountLockoutDuration": 60,
	"AccountLockoutCounterResetAfter": 60,
	"Accounts": {
		"@odata.id": "/redfish/v1/AccountService/Accounts"
	},
	"Roles": {
		"@odata.id": "/redfish/v1/AccountService/Roles"
	}
}

Accounts_data = {
	"@odata.type": "#ManagerAccountCollection.ManagerAccountCollection",
	"Name": "Accounts Collection",
	"Members@odata.count": 1,
	"Members": [
		{
		    "@odata.id": "/redfish/v1/AccountService/Accounts/1",
		}
	],
	"@odata.id": "/redfish/v1/AccountService/Accounts"

}

Accounts_1_data = {
    "@odata.type": "#ManagerAccount.v1_7_0.ManagerAccount",
    "Id": "1",
    "Name": "UserAccount",
    "Description": "Standard User Account",
    "UserName": "admin",
    "Password": None,
    "RoleId": "Administrator",
    "Enabled": True,
    "Locked": False,
    "AccountTypes": [
        "Redfish"
    ],
    "Links": {
        "Role": {
            "@odata.id": "/redfish/v1/AccountService/Roles/Administrator"
        }
    },
    "@odata.id": "/redfish/v1/AccountService/Accounts/1"    
}

Roles_data = {
    "@odata.id": "/redfish/v1/AccountService/Roles",
    "@odata.type": "#RoleCollection.RoleCollection",
    "Name":"Roles",
    "Members@odata.count": 3,
    "Members": [
        {"@odata.id": "/redfish/v1/AccountService/Roles/Administrator"},
        {"@odata.id": "/redfish/v1/AccountService/Roles/Operator"},
        {"@odata.id": "/redfish/v1/AccountService/Roles/ReadOnly"}
    ]
}

# 規定必要三個user Administrator, Operator, ReadOnly
Roles_Administrator_data = {
    "@odata.id": "/redfish/v1/AccountService/Roles/Administrator",
    "@odata.type": "#Role.v1_2_4.Role",
    "Id": "Administrator",
    "Name": "Administrator Role",
    "RoleId": "Administrator",  # 權限
    "AssignedPrivileges": [
        "ConfigureManager",
        "Login",
        "ConfigureUsers",
        "ConfigureComponents",
        "ConfigureSelf"
    ],
    "OemPrivileges": []
}

Roles_Operator_data = {
    "@odata.id": "/redfish/v1/AccountService/Roles/Operator",
    "@odata.type": "#Role.v1_2_4.Role",
    "Id": "Operator",
    "Name": "Operator Role",
    "RoleId": "Operator",
    "AssignedPrivileges": [
        "Login",
        "ConfigureComponents",
        "ConfigureSelf"
    ],
    "OemPrivileges": []
}


Roles_ReadOnly_data = {
    "@odata.id": "/redfish/v1/AccountService/Roles/ReadOnly",
    "@odata.type": "#Role.v1_2_4.Role",
    "Id": "ReadOnly",
    "Name": "ReadOnly Role",
    "RoleId": "ReadOnly",
    "AssignedPrivileges": [
        "Login",
        "ConfigureSelf"
    ],
    "OemPrivileges": []
}

@redfish_ns.route("/AccountService")
class AccountSerivce(Resource):
    def get(self):

        return AccountService_data

@redfish_ns.route("/AccountService/Accounts")
class Accounts(Resource):
    def get(self):

        return Accounts_data  
    
# -------------------------------------------
import hashlib, json

def generate_etag(resource_dict):
    payload = json.dumps(resource_dict, sort_keys=True).encode('utf-8')
    return hashlib.md5(payload).hexdigest()

import hashlib, json
from flask import make_response, jsonify
from flask_restx import Resource
# -------------------------------------------
@redfish_ns.route("/AccountService/Accounts/1")
class Accounts1(Resource):
    def get(self):
        # 1. 您原本要回傳的 JSON 資料
        data = Accounts_1_data

        # 2. 計算 ETag：對 JSON 做雜湊（key 排序可避免欄位順序影響）
        payload = json.dumps(data, sort_keys=True).encode('utf-8')
        etag_value = hashlib.md5(payload).hexdigest()

        # 3. 包裝成 Response，並在標頭加上 ETag
        resp = make_response(jsonify(data), 200)
        resp.headers['ETag'] = f'"{etag_value}"'  # 加上雙引號符合 HTTP 規範
        return resp        
      
      
@redfish_ns.route("/AccountService/Roles")
class Roles(Resource):
    def get(self):

        return Roles_data, 200
    
@redfish_ns.route("/AccountService/Roles/Administrator")
class RolesAdministrator(Resource):
    def get(self):
        return Roles_Administrator_data  
    
@redfish_ns.route("/AccountService/Roles/Operator")
class RolesOperator(Resource):
    def get(self):
        return Roles_Operator_data  

@redfish_ns.route("/AccountService/Roles/ReadOnly")
class RolesReadOnly(Resource):
    def get(self):
        return Roles_ReadOnly_data          
# --------------------------------------------
# Update
# --------------------------------------------
UpdateService_data = {
    "@odata.type": "#UpdateService.v1_14_0.UpdateService",
    "Id": "UpdateService",
    "Name": "Update cdu",
    "ServiceEnabled": True,
    "FirmwareInventory": {
        "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory"
    },
    "Actions": {
        "#UpdateService.SimpleUpdate": {
            "target": "/redfish/v1/UpdateService/Actions/UpdateCdu.SimpleUpdate"
        }
    },
    "@odata.id": "/redfish/v1/UpdateService"    
}

FirmwareInventory_data = {
    "@odata.type": "#SoftwareInventoryCollection.SoftwareInventoryCollection",
    "Name": "Firmware Inventory",
    "Members@odata.count": 3,
    "Members": [{
        "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/WebInterface",
        # "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PLC",
        # "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PC"
    }],
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory"    
}

WebInterface_data = {
    "@odata.type": "#SoftwareInventory.v1_3_0.SoftwareInventory",
    "Id": "WebInterface",
    "Name": "Web Interface firmware",
    "Version": "1502",
    "SoftwareId": "WEB-INTERFACE",
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/WebInterface" 
}

FirmwareInventoryPC_data = {
    "@odata.type": "#PC.v0100.PC",
    "Id": "PC",
    "Name": "PC version",
    "Version": "0100",
    "SoftwareId": "PC-Version",
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PC"     
}

FirmwareInventoryPLC_data = {
    "@odata.type": "#PLC.v0107.PLC",
    "Id": "PLC",
    "Name": "PLC version",
    "Version": "0107",
    "SoftwareId": "PLC-Version",
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/PLC"     
}

@redfish_ns.route("/UpdateService")
class UpdateService(Resource):
    def get(self):

        return UpdateService_data  

@redfish_ns.route("/UpdateService/FirmwareInventory")
class FirmwareInventory(Resource):
    def get(self):

        return FirmwareInventory_data  

@redfish_ns.route("/UpdateService/FirmwareInventory/WebInterface")
class FirmwareInventoryWebInterface(Resource):
    def get(self):

        return WebInterface_data  

@redfish_ns.route("/UpdateService/Actions/UpdateCdu.SimpleUpdate")
class ActionsUpdateCduSimpleUpdatee(Resource):
    def get(self):

        return {"ok"}
    
@redfish_ns.route("/UpdateService/FirmwareInventory/PC")
class FirmwareInventoryPC(Resource):
    def get(self):

        return FirmwareInventoryPC_data   

@redfish_ns.route("/UpdateService/FirmwareInventory/PLC")
class FirmwareInventoryPLC(Resource):
    def get(self):

        return FirmwareInventoryPLC_data   
    
"""
Uris:
/redfish/v1/SessionService
    - uri: /redfish/v1/SessionService
      data: (Note1*)
    - uri: /redfish/v1/SessionService/Sessions
      data: (Note1*)

(Note1) https://docs.google.com/spreadsheets/d/1xZgYleg7HzWnugL_JKGC-6ATSXQK4KvR/edit?gid=1880258646#gid=1880258646
"""
sessionservice_example_data = {
    "@odata.type": "#SessionService.v1_1_8.SessionService",
    "Id": "SessionService",
    "Name": "Session Service",
    "Description": "Session Service",
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "ServiceEnabled": False, # we use basic auth, not session auth
    "SessionTimeout": 86400,
    "Sessions": {
        "@odata.id": "/redfish/v1/SessionService/Sessions"
    },
    "@odata.id": "/redfish/v1/SessionService"
}
sessionservice_sessions_example_data = {
    "@odata.type": "#SessionCollection.SessionCollection",
    "Name": "Session Collection",
    "Members@odata.count": 0,
    "Members": [
    ],
    "@odata.id": "/redfish/v1/SessionService/Sessions"
}

@redfish_ns.route("/SessionService")
class SessionService(Resource):
    @requires_auth
    def get(self):
        return sessionservice_example_data

@redfish_ns.route("/SessionService/Sessions")
class SessionServiceSessions(Resource):
    @requires_auth
    def get(self):
        return sessionservice_sessions_example_data

#--------Telemetry
TelemetryService_data = {
    "@odata.id": "/redfish/v1/TelemetryService",
    "@odata.type": "#TelemetryService.TelemetryService",
    "Id": "TelemetryService",
    "Name": "CDU Telemetry Service",
    # "ServiceEnabled": True,
    # "MetricReportDefinitions": {
    #     "@odata.id": "/redfish/v1/TelemetryService/MetricReportDefinitions"
    # },
    # "MetricReports": {"@odata.id": "/redfish/v1/TelemetryService/MetricReports"},
}
 

TelemetryService__MetricReports_data = {
    "@odata.id": "/redfish/v1/TelemetryService/MetricReports",
    "Name": "CDU Metric Reports Collection",
    "Members@odata.count": 3,
    "Members": [
        {"@odata.id": "/redfish/v1/TelemetryService/MetricReports/1"},
        {"@odata.id": "/redfish/v1/TelemetryService/MetricReports/2"},
        {"@odata.id": "/redfish/v1/TelemetryService/MetricReports/3"},
    ],
}

MetricReports_example_data = {
    "@odata.id": "/redfish/v1/TelemetryService/MetricReports/1",
    "Id": "CDU_Report_001",
    "Name": "CDU Report at 2025-03-31T08:00:00Z",
    "Timestamp": "2025-03-31T08:00:00Z",
    "MetricValues": [
        
    ],
}


@redfish_ns.route("/TelemetryService")
class TelemetryService(Resource):
    def get(self):
        return TelemetryService_data


@redfish_ns.route("/TelemetryService/MetricReports")
class TelemetryService_MetricReports(Resource):
    def get(self):
        return TelemetryService__MetricReports_data

expample_data = {
    "temp_clntSply": 0.0,
    "temp_clntSplySpare": 0.0,
    "temp_clntRtn": 0.0,
    "temp_clntRtnSpare": 0.0,
    "space": 0.0,
    "prsr_clntSply": -0.25,
    "prsr_clntSplySpare": -250.0,
    "prsr_clntRtn": -250.0,
    "prsr_clntRtnSpare": -250.0,
    "prsr_fltIn": -250.0,
    "prsr_fltOut": -250.0,
    "clnt_flow": -412500.0,
    "ambient_temp": 1000.0,
    "relative_humid": 2000.0,
    "dew_point": 0.0,
    "pH": 4000.0,
    "cdct": 8000.0,
    "tbd": 9600.0,
    "power": 7.0,
    "AC": 8.0,
    "inv1_freq": 1.5793999433517456,
    "inv2_freq": 0.0,
    "inv3_freq": 1.9121999740600586,
    "heat_capacity": 0.0,
    "fan_freq1": 12.0,
    "fan_freq2": 13.0,
    "fan_freq3": 14.0,
    "fan_freq4": 15.0,
    "fan_freq5": 16.0,
    "fan_freq6": 17.0,
    "fan_freq7": 18.0,
    "fan_freq8": 19.0
}

@redfish_ns.route("/TelemetryService/MetricReports/1")
class MetricReports_1(Resource):
    def get(self):
        for k,v in expample_data.items():
            MetricReports_example_data["MetricValues"].append({
                "MetricId":k,
                "MetricValue":v,
                "Timestamp": "2025-03-31T08:00:00Z"
            })
        return MetricReports_example_data

@redfish_ns.route("/TelemetryService/MetricReports/2")
class MetricReports_2(Resource):
    def get(self):
        for k,v in expample_data.items():
            MetricReports_example_data["MetricValues"].append({
                "MetricId":k,
                "MetricValue":v,
                "Timestamp": "2025-03-31T08:00:00Z"
            })
        return MetricReports_example_data
@redfish_ns.route("/TelemetryService/MetricReports/3")
class MetricReports_3(Resource):
    def get(self):
        for k,v in expample_data.items():
            MetricReports_example_data["MetricValues"].append({
                "MetricId":k,
                "MetricValue":v,
                "Timestamp": "2025-03-31T08:00:00Z"
            })
        return MetricReports_example_data
    
# 將要使用的 $ 放入
SUPPORTED_DOLLAR_PARAMS = {'$filter', '$select', '$expand', '$orderby', '$top', '$skip', '$count', '$format'} 
###------------------------------------------------------
@app.before_request
def require_auth_on_all_routes():
###----------------處理$--------------------------------------
    if not request.path.startswith('/'):
        return

    for param in request.args.keys():
        if param.startswith('$') and param not in SUPPORTED_DOLLAR_PARAMS:
            return Response(status=501)
###----------------移除Auth--------------------------------------
    p = request.path.rstrip('/')
    
    public = {
        '/redfish',
        '/redfish/v1',
        '/redfish/v1/$metadata',
        '/redfish/v1/odata'
    }
    
    if p in public:
        return
###----------------一般Auth--------------------------------------    
    auth = request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    
###----------------處理標頭--------------------------------------    
@app.after_request
def add_link_describedby(response):
    if request.method in ('GET', 'HEAD') and request.path.startswith('/redfish/v1'):
        response.headers['Link'] = '</redfish/v1/$metadata>; rel="describedby"'
        response.headers['OData-Version'] = '4.0'
    return response
    
# api.add_namespace(default_ns)
api.add_namespace(redfish_ns)

# if __name__ == "__main__":
    # app.run(debug=True, host="0.0.0.0", port=5000)
# 

if __name__ == '__main__':
    import sys
    import os
    dir_name = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(dir_name)

    dotenv_path = os.path.join(dir_name, '.env')
    cert_pem_path = os.path.join(dir_name, 'cert.pem')
    key_pem_path = os.path.join(dir_name, 'key.pem')
    
    load_dotenv(dotenv_path)
    print("os.environ['ITG_REST_HOST']:", os.environ['ITG_REST_HOST'])

    # ssl_context=(憑證檔, 私鑰檔)
    app.run(host='0.0.0.0', port=5018,
            ssl_context=(cert_pem_path, key_pem_path))