import threading
import time
import os
import logging
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.client.sync import ModbusSerialClient
import struct
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from concurrent_log_handler import ConcurrentTimedRotatingFileHandler
import statistics
from collections import deque
from dotenv import load_dotenv
import platform
import json


if platform.system() == "Linux":
    project_root = os.path.dirname(os.getcwd())
    env_path = os.path.join(project_root, "webUI/web/.env")
    onLinux = True

else:
    env_path = "webUI/web/.env"
    onLinux = False


load_dotenv(env_path)

modbus_ip = os.getenv("MODBUS_IP")


if onLinux:
    modbus_host = modbus_ip
else:
    modbus_host = "192.168.3.250"


modbus_port = 502
modbus_slave_id = 1
modbus_address = 0

port = "/dev/ttyS0"

switch_address = 0x0000

log_path = os.getcwd()


if onLinux:
    journal_dir = f"{log_path}/logs/journal"
else:
    journal_dir = f"{log_path}/PLC/logs/journal"

if not os.path.exists(journal_dir):
    os.makedirs(journal_dir)

max_bytes = 4 * 1024 * 1024 * 1024
backup_count = 1

file_name = "journal.log"
log_file = os.path.join(journal_dir, file_name)
journal_handler = ConcurrentTimedRotatingFileHandler(
    log_file,
    maxBytes=max_bytes,
    backupCount=backup_count,
    encoding="UTF-8",
    delay=False,
)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
journal_handler.setFormatter(formatter)

journal_logger = logging.getLogger("journal_logger")
journal_logger.setLevel(logging.INFO)
journal_logger.addHandler(journal_handler)

server1_count = 0
check_server2 = 0
pre_check_server2 = 0
server2_occur_stop = False


f1_data = []
p1_data = []
p2_data = []
p3_data = []
p1_error_box = []
p2_error_box = []
p3_error_box = []
pump_signial = ""
change_back_mode = ""
count_f1 = 0
previous_inv = 4
x = 0
water_pv_set = 0
count = 0
diff = 0
previous_inv1 = False
previous_inv2 = False
oc_issue = False
warning_light = False
zero_flag = False
auto_flag = False
rtu_flag = False
previous_ver = None
oc_trigger = False

bit_output_regs = {
    "mc1": False,
    "mc2": False,
    "led_err": False,
    "mc3": False,
    "space1": False,
    "space2": False,
    "space3": False,
    "space4": False,
    "mc_fan1": False,
    "mc_fan2": False,
}

inv = {
    "inv1": False,
    "inv2": False,
    "inv3": False,
}

color_light = {
    "red": True,
    "green": True,
}

word_regs = {
    "pump_speed": 0,
    "pid_pump_out": 0,
    "p1_check": 0,
    "p2_check": 0,
    "p3_check": 0,
    "fan_speed": 0,
    "f1_check": False,
    "f2_check": False,
    "f3_check": False,
    "f4_check": False,
    "f5_check": False,
    "f6_check": False,
    "f7_check": False,
    "f8_check": False,
}

bit_input_regs = {
    "Inv1_Error": None,
    "Inv2_Error": None,
    "Inv3_Error": None,
    "leakage1_leak": None,
    "leakage1_broken": None,
    "main_mc_error": None,
    "fan1_error": None,
    "fan2_error": None,
    "fan3_error": None,
    "fan4_error": None,
    "fan5_error": None,
    "fan6_error": None,
    "fan7_error": None,
    "fan8_error": None,
}

raw_485_data = {
    "AmbientTemp": 0,
    "RelativeHumid": 0,
    "DewPoint": 0,
    "pH": 0,
    "conductivity": 0,
    "turbidity": 0,
    "inst_power": 0,
    "average_current": 0,
    "Inv1_Freq": 0,
    "Inv2_Freq": 0,
    "Inv3_Freq": 0,
    "Fan1Com": 0,
    "Fan2Com": 0,
    "Fan3Com": 0,
    "Fan4Com": 0,
    "Fan5Com": 0,
    "Fan6Com": 0,
    "Fan7Com": 0,
    "Fan8Com": 0,
    "ATS1": False,
    "ATS2": False,
}

raw_485_comm = {
    "AmbientTemp": 0,
    "RelativeHumid": 0,
    "DewPoint": 0,
    "pH": False,
    "conductivity": False,
    "turbidity": False,
    "inst_power": False,
    "average_current": False,
    "Inv1_Freq": False,
    "Inv2_Freq": False,
    "Inv3_Freq": False,
    "ATS1": False,
    "ATS2": False,
    "Fan1Com": 0,
    "Fan2Com": 0,
    "Fan3Com": 0,
    "Fan4Com": 0,
    "Fan5Com": 0,
    "Fan6Com": 0,
    "Fan7Com": 0,
    "Fan8Com": 0,
}


sensor_raw = {
    "Temp_ClntSply": 0,
    "Temp_ClntSplySpare": 0,
    "Temp_ClntRtn": 0,
    "Temp_ClntRtnSpare": 0,
    "space": 0,
    "Prsr_ClntSply": 0,
    "Prsr_ClntSplySpare": 0,
    "Prsr_ClntRtn": 0,
    "Prsr_ClntRtnSpare": 0,
    "Prsr_FltIn": 0,
    "Prsr_FltOut": 0,
    "Clnt_Flow": 0,
    "AmbientTemp": 0,
    "RelativeHumid": 0,
    "DewPoint": 0,
    "pH": 0,
    "Cdct": 0,
    "Tbd": 0,
    "Power": 0,
    "AC": 0,
    "Inv1_Freq": 0,
    "Inv2_Freq": 0,
    "Inv3_Freq": 0,
    "Heat_Capacity": 0,
}

ad_sensor_value = {
    "Temp_ClntSply": 0,
    "Temp_ClntSplySpare": 0,
    "Temp_ClntRtn": 0,
    "Temp_ClntRtnSpare": 0,
    "space": 0,
    "Prsr_ClntSply": 0,
    "Prsr_ClntSplySpare": 0,
    "Prsr_ClntRtn": 0,
    "Prsr_ClntRtnSpare": 0,
    "Prsr_FltIn": 0,
    "Prsr_FltOut": 0,
    "Clnt_Flow": 0,
}

serial_sensor_value = {
    "AmbientTemp": 0,
    "RelativeHumid": 0,
    "DewPoint": 0,
    "pH": 0,
    "Cdct": 0,
    "Tbd": 0,
    "Power": 0,
    "AC": 0,
    "Inv1_Freq": 0,
    "Inv2_Freq": 0,
    "Inv3_Freq": 0,
    "Heat_Capacity": 0,
    "fan_freq1": 0,
    "fan_freq2": 0,
    "fan_freq3": 0,
    "fan_freq4": 0,
    "fan_freq5": 0,
    "fan_freq6": 0,
    "fan_freq7": 0,
    "fan_freq8": 0,
}

mapping = {
    "AmbientTemp":"AmbientTemp",
    "RelativeHumid":"RelativeHumid",
    "DewPoint":"DewPoint",
    "pH":"pH",
    "conductivity": "Cdct",
    "turbidity": "Tbd",
    "inst_power": "Power",
    "Inv1_Freq":"Inv1_Freq",
    "Inv2_Freq":"Inv2_Freq",
    "Inv3_Freq":"Inv3_Freq",
    "average_current": "AC",
    "Fan1Com": "fan_freq1",
    "Fan2Com": "fan_freq2",
    "Fan3Com": "fan_freq3",
    "Fan4Com": "fan_freq4",
    "Fan5Com": "fan_freq5",
    "Fan6Com": "fan_freq6",
    "Fan7Com": "fan_freq7",
    "Fan8Com": "fan_freq8",
}


oc_detection = {
    "p1": False,
    "p2": False,
    "p3": False,
    "f1": False,
    "f2": False,
}

inspection_data = {
    "prev": {
        "inv1": False,
        "inv2": False,
        "inv3": False,
    },
    "result": {
        "p1_speed": False,
        "p2_speed": False,
        "p3_speed": False,
        "f1": [],
        "Temp_ClntSply_broken": False,
        "Temp_ClntSplySpare_broken": False,
        "Temp_ClntRtn_broken": False,
        "Temp_ClntRtnSpare_broken": False,
        "Prsr_ClntSply_broken": False,
        "Prsr_ClntSplySpare_broken": False,
        "Prsr_ClntRtn_broken": False,
        "Prsr_ClntRtnSpare_broken": False,
        "Prsr_FltIn_broken": False,
        "Prsr_FltOut_broken": False,
        "Clnt_Flow_broken": False,
        "Inv1_Freq_com": [],
        "Inv2_Freq_com": [],
        "Inv3_Freq_com": [],
        "coolant_flow_rate_com": [],
        "AmbientTemp_com": [],
        "RelativeHumid_com": [],
        "DewPoint_com": [],
        "pH_com": [],
        "conductivity_com": [],
        "turbidity_com": [],
        "ATS1_com": [],
        "ATS2_com": [],
        "inst_power_com": [],
        "average_current_com": [],
        "Fan1Com_com": [],
        "Fan2Com_com": [],
        "Fan3Com_com": [],
        "Fan4Com_com": [],
        "Fan5Com_com": [],
        "Fan6Com_com": [],
        "Fan7Com_com": [],
        "Fan8Com_com": [],
        "level1": False,
        "level2": False,
        "level3": False,
        "power24v1": False,
        "power24v2": False,
        "power12v1": False,
        "power12v2": False,
    },
    "prog": {
        "p1_speed": 1,
        "p2_speed": 1,
        "p3_speed": 1,
        "f1": 1,
        "Temp_ClntSply_broken": 1,
        "Temp_ClntSplySpare_broken": 1,
        "Temp_ClntRtn_broken": 1,
        "Temp_ClntRtnSpare_broken": 1,
        "Prsr_ClntSply_broken": 1,
        "Prsr_ClntSplySpare_broken": 1,
        "Prsr_ClntRtn_broken": 1,
        "Prsr_ClntRtnSpare_broken": 1,
        "Prsr_FltIn_broken": 1,
        "Prsr_FltOut_broken": 1,
        "Clnt_Flow_broken": 1,
        "Inv1_Freq_com": 1,
        "Inv2_Freq_com": 1,
        "Inv3_Freq_com": 1,
        "coolant_flow_rate_com": 1,
        "AmbientTemp_com": 1,
        "RelativeHumid_com": 1,
        "DewPoint_com": 1,
        "pH_com": 1,
        "conductivity_com": 1,
        "turbidity_com": 1,
        "ATS1_com": 1,
        "ATS2_com": 1,
        "inst_power_com": 1,
        "average_current_com": 1,
        "Fan1Com_com": 1,
        "Fan2Com_com": 1,
        "Fan3Com_com": 1,
        "Fan4Com_com": 1,
        "Fan5Com_com": 1,
        "Fan6Com_com": 1,
        "Fan7Com_com": 1,
        "Fan8_com": 1,
        "level1": 1,
        "level2": 1,
        "level3": 1,
        "power24v1": 1,
        "power24v2": 1,
        "power12v1": 1,
        "power12v2": 1,
    },
    "set": {"total_inspect_time": 95},
    "step": 1,
    "start_time": 0,
    "mid_time": 0,
    "end_time": 0,
    "final_end_time": 0,
    "force_change_mode": 0,
    "start_btn": False,
    "cancel_btn": False,
    "skip": False,
}

ver_switch = {
    "flow_switch": False,
    "median_switch": False,
}

measured_data_mapping = {
    9: "TempClntSply",
    11: "TempClntSplySpare",
    13: "TempClntRtn",
    15: "TempClntRtnSpare",
    17: "PrsrClntSply",
    19: "PrsrClntSplySpare",
    21: "PrsrClntRtn",
    23: "PrsrClntRtnSpare",
    25: "PrsrFltIn",
    27: "PrsrFltOut",
    29: "ClntFlow",
}

counter = {
    "start": 0,
    "end": 0,
    "pass": 0,
}


dword_regs = {
    "p_swap": 0,
    "swap_hr": 0,
    "swap_min": 0,
    "p1_run_min": 0,
    "p1_run_hr": 0,
    "p2_run_min": 0,
    "p2_run_hr": 0,
    "p3_run_min": 0,
    "p3_run_hr": 0,
}

reset_current_btn = {"status": False, "press_reset": False}


sensor_factor = {
    "Temp_ClntSply": 0,
    "Temp_ClntSplySpare": 0,
    "Temp_ClntRtn": 0,
    "Temp_ClntRtnSpare": 0,
    "Prsr_ClntSply": 0,
    "Prsr_ClntSplySpare": 0,
    "Prsr_ClntRtn": 0,
    "Prsr_ClntRtnSpare": 0,
    "Prsr_FltIn": 0,
    "Prsr_FltOut": 0,
    "Clnt_Flow": 0,
    "AmbientTemp": 0,
    "RelativeHumid": 0,
    "DewPoint": 0,
    "pH": 0,
    "Cdct": 0,
    "Tbd": 0,
    "Power": 0,
    "AC": 0,
    "Heat_Capacity": 0,
}

sensor_offset = {
    "Temp_ClntSply": 0,
    "Temp_ClntSplySpare": 0,
    "Temp_ClntRtn": 0,
    "Temp_ClntRtnSpare": 0,
    "Prsr_ClntSply": 0,
    "Prsr_ClntSplySpare": 0,
    "Prsr_ClntRtn": 0,
    "Prsr_ClntRtnSpare": 0,
    "Prsr_FltIn": 0,
    "Prsr_FltOut": 0,
    "Clnt_Flow": 0,
    "AmbientTemp": 0,
    "RelativeHumid": 0,
    "DewPoint": 0,
    "pH": 0,
    "Cdct": 0,
    "Tbd": 0,
    "Power": 0,
    "AC": 0,
    "Heat_Capacity": 0,
}

all_sensors_dict = {
    "Temp_ClntSply": 0,
    "Temp_ClntSplySpare": 0,
    "Temp_ClntRtn": 0,
    "Temp_ClntRtnSpare": 0,
    "space": 0,
    "Prsr_ClntSply": 0,
    "Prsr_ClntSplySpare": 0,
    "Prsr_ClntRtn": 0,
    "Prsr_ClntRtnSpare": 0,
    "Prsr_FltIn": 0,
    "Prsr_FltOut": 0,
    "Clnt_Flow": 0,
    "AmbientTemp": 0,
    "RelativeHumid": 0,
    "DewPoint": 0,
    "pH": 0,
    "Cdct": 0,
    "Tbd": 0,
    "Power": 0,
    "AC": 0,
    "Inv1_Freq": 0,
    "Inv2_Freq": 0,
    "Inv3_Freq": 0,
    "Heat_Capacity": 0,
}


thrshd_data = {
    "Thr_W_TempClntSply": 0,
    "Thr_W_Rst_TempClntSply": 0,
    "Thr_A_TempClntSply": 0,
    "Thr_A_Rst_TempClntSply": 0,
    "Thr_W_TempClntSplySpare": 0,
    "Thr_W_Rst_TempClntSplySpare": 0,
    "Thr_A_TempClntSplySpare": 0,
    "Thr_A_Rst_TempClntSplySpare": 0,
    "Thr_W_TempClntRtn": 0,
    "Thr_W_Rst_TempClntRtn": 0,
    "Thr_A_TempClntRtn": 0,
    "Thr_A_Rst_TempClntRtn": 0,
    "Thr_W_TempClntRtnSpare": 0,
    "Thr_W_Rst_TempClntRtnSpare": 0,
    "Thr_A_TempClntRtnSpare": 0,
    "Thr_A_Rst_TempClntRtnSpare": 0,
    "Thr_W_PrsrClntSply": 0,
    "Thr_W_Rst_PrsrClntSply": 0,
    "Thr_A_PrsrClntSply": 0,
    "Thr_A_Rst_PrsrClntSply": 0,
    "Thr_W_PrsrClntSplySpare": 0,
    "Thr_W_Rst_PrsrClntSplySpare": 0,
    "Thr_A_PrsrClntSplySpare": 0,
    "Thr_A_Rst_PrsrClntSplySpare": 0,
    "Thr_W_PrsrClntRtn": 0,
    "Thr_W_Rst_PrsrClntRtn": 0,
    "Thr_A_PrsrClntRtn": 0,
    "Thr_A_Rst_PrsrClntRtn": 0,
    "Thr_W_PrsrClntRtnSpare": 0,
    "Thr_W_Rst_PrsrClntRtnSpare": 0,
    "Thr_A_PrsrClntRtnSpare": 0,
    "Thr_A_Rst_PrsrClntRtnSpare": 0,
    "Thr_W_PrsrFltIn_L": 0,
    "Thr_W_Rst_PrsrFltIn_L": 0,
    "Thr_A_PrsrFltIn_L": 0,
    "Thr_A_Rst_PrsrFltIn_L": 0,
    "Thr_W_PrsrFltIn_H": 0,
    "Thr_W_Rst_PrsrFltIn_H": 0,
    "Thr_A_PrsrFltIn_H": 0,
    "Thr_A_Rst_PrsrFltIn_H": 0,
    "Thr_W_PrsrFltOut_H": 0,
    "Thr_W_Rst_PrsrFltOut_H": 0,
    "Thr_A_PrsrFltOut_H": 0,
    "Thr_A_Rst_PrsrFltOut_H": 0,
    "Thr_W_ClntFlow": 0,
    "Thr_W_Rst_ClntFlow": 0,
    "Thr_A_ClntFlow": 0,
    "Thr_A_Rst_ClntFlow": 0,
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
    "Thr_W_DewPoint": 0,
    "Thr_W_Rst_DewPoint": 0,
    "Thr_A_DewPoint": 0,
    "Thr_A_Rst_DewPoint": 0,
    "Thr_W_pH_L": 0,
    "Thr_W_Rst_pH_L": 0,
    "Thr_A_pH_L": 0,
    "Thr_A_Rst_pH_L": 0,
    "Thr_W_pH_H": 0,
    "Thr_W_Rst_pH_H": 0,
    "Thr_A_pH_H": 0,
    "Thr_A_Rst_pH_H": 0,
    "Thr_W_Cdct_L": 0,
    "Thr_W_Rst_Cdct_L": 0,
    "Thr_A_Cdct_L": 0,
    "Thr_A_Rst_Cdct_L": 0,
    "Thr_W_Cdct_H": 0,
    "Thr_W_Rst_Cdct_H": 0,
    "Thr_A_Cdct_H": 0,
    "Thr_A_Rst_Cdct_H": 0,
    "Thr_W_Tbt_L": 0,
    "Thr_W_Rst_Tbt_L": 0,
    "Thr_A_Tbt_L": 0,
    "Thr_A_Rst_Tbt_L": 0,
    "Thr_W_Tbt_H": 0,
    "Thr_W_Rst_Tbt_H": 0,
    "Thr_A_Tbt_H": 0,
    "Thr_A_Rst_Tbt_H": 0,
    "Thr_W_AC_H": 0,
    "Thr_W_Rst_AC_H": 0,
    "Thr_A_AC_H": 0,
    "Thr_A_Rst_AC_H": 0,
    "Delay_TempClntSply": 0,
    "Delay_TempClntSplySpare": 0,
    "Delay_TempClntRtn": 0,
    "Delay_TempClntRtnSpare": 0,
    "Delay_PrsrClntSply": 0,
    "Delay_PrsrClntSplySpare": 0,
    "Delay_PrsrClntRtn": 0,
    "Delay_PrsrClntRtnSpare": 0,
    "Delay_PrsrFltIn": 0,
    "Delay_PrsrFltOut": 0,
    "Delay_ClntFlow": 0,
    "Delay_AmbientTemp": 0,
    "Delay_RelativeHumid": 0,
    "Delay_DewPoint": 0,
    "Delay_pH": 0,
    "Delay_Cdct": 0,
    "Delay_Tbt": 0,
    "Delay_AC": 0,
    "Delay_Inv1_OverLoad": 0,
    "Delay_Inv2_OverLoad": 0,
    "Delay_Inv3_OverLoad": 0,
    "Delay_Fan_OverLoad1": 0,
    "Delay_Fan_OverLoad2": 0,
    "Delay_Inv1_Error": 0,
    "Delay_Inv2_Error": 0,
    "Delay_Inv3_Error": 0,
    "Delay_ATS": 0,
    "Delay_Inverter1_Communication": 0,
    "Delay_Inverter2_Communication": 0,
    "Delay_Inverter3_Communication": 0,
    "Delay_Coolant_Flow_Meter_Communication": 0,
    "Delay_AmbientTemp_Communication": 0,
    "Delay_RelativeHumid_Communication": 0,
    "Delay_DewPoint_Communication": 0,
    "Delay_pH_Sensor_Communication": 0,
    "Delay_Conductivity_Sensor_Communication": 0,
    "Delay_Turbidity_Sensor_Communication": 0,
    "Delay_ATS1_Communication": 0,
    "Delay_ATS2_Communication": 0,
    "Delay_Power_Meter_Communication": 0,
    "Delay_average_current_Communication": 0,
    "Delay_Fan1Com_Communication": 0,
    "Delay_Fan2Com_Communication": 0,
    "Delay_Fan3Com_Communication": 0,
    "Delay_Fan4Com_Communication": 0,
    "Delay_Fan5Com_Communication": 0,
    "Delay_Fan6Com_Communication": 0,
    "Delay_Fan7Com_Communication": 0,
    "Delay_Fan8Com_Communication": 0,
    "Delay_TempClntSply_broken": 0,
    "Delay_TempClntSplySpare_broken": 0,
    "Delay_TempClntRtn_broken": 0,
    "Delay_TempClntRtnSpare_broken": 0,
    "Delay_PrsrClntSply_broken": 0,
    "Delay_PrsrClntSplySpare_broken": 0,
    "Delay_PrsrClntRtn_broken": 0,
    "Delay_PrsrClntRtnSpare_broken": 0,
    "Delay_PrsrFltIn_broken": 0,
    "Delay_PrsrFltOut_broken": 0,
    "Delay_Clnt_Flow_broken": 0,
    "Delay_leakage1_leak": 0,
    "Delay_leakage1_broken": 0,
    "Delay_level1": 0,
    "Delay_level2": 0,
    "Delay_level3": 0,
    "Delay_power24v1": 0,
    "Delay_power24v2": 0,
    "Delay_power12v1": 0,
    "Delay_power12v2": 0,
    "Delay_main_mc_error": 0,
    "Delay_fan1_error": 0,
    "Delay_fan2_error": 0,
    "Delay_fan3_error": 0,
    "Delay_fan4_error": 0,
    "Delay_fan5_error": 0,
    "Delay_fan6_error": 0,
    "Delay_fan7_error": 0,
    "Delay_fan8_error": 0,
    "Delay_rack_error": 0,
}

rack_data = {
    "rack_control": {
        "Rack_1_Enable": False,
        "Rack_2_Enable": False,
        "Rack_3_Enable": False,
        "Rack_4_Enable": False,
        "Rack_5_Enable": False,
        "Rack_6_Enable": False,
        "Rack_7_Enable": False,
        "Rack_8_Enable": False,
        "Rack_9_Enable": False,
        "Rack_10_Enable": False,
        "Rack_1_Control": False,
        "Rack_2_Control": False,
        "Rack_3_Control": False,
        "Rack_4_Control": False,
        "Rack_5_Control": False,
        "Rack_6_Control": False,
        "Rack_7_Control": False,
        "Rack_8_Control": False,
        "Rack_9_Control": False,
        "Rack_10_Control": False,
    },
    "rack_pass": {
        "Rack_1_Pass": False,
        "Rack_2_Pass": False,
        "Rack_3_Pass": False,
        "Rack_4_Pass": False,
        "Rack_5_Pass": False,
        "Rack_6_Pass": False,
        "Rack_7_Pass": False,
        "Rack_8_Pass": False,
        "Rack_9_Pass": False,
        "Rack_10_Pass": False,
    },
}


status_data = {
    "TempClntSply": 0,
    "TempClntSplySpare": 0,
    "TempClntRtn": 0,
    "TempClntRtnSpare": 0,
    "PrsrClntSply": 0,
    "PrsrClntSplySpare": 0,
    "PrsrClntRtn": 0,
    "PrsrClntRtnSpare": 0,
    "PrsrFltIn": 0,
    "PrsrFltOut": 0,
    "ClntFlow": 0,
    "AmbientTemp": 0,
    "RelativeHumid": 0,
    "DewPoint": 0,
    "pH": 0,
    "Cdct": 0,
    "Tbt": 0,
    "Power": 0,
    "AC": 0,
    "Inv1_Freq": 0,
    "Inv2_Freq": 0,
    "Inv3_Freq": 0,
    "fan_Freq": 0,
    "HeatCapacity": 0,
}


time_data = {
    "start": {
        "W_TempClntSply": 0,
        "W_TempClntSplySpare": 0,
        "W_TempClntRtn": 0,
        "W_TempClntRtnSpare": 0,
        "W_PrsrClntSply": 0,
        "W_PrsrClntSplySpare": 0,
        "W_PrsrClntRtn": 0,
        "W_PrsrClntRtnSpare": 0,
        "W_PrsrFltIn": 0,
        "W_PrsrFltOut": 0,
        "W_ClntFlow": 0,
        "W_AmbientTemp": 0,
        "W_RelativeHumid": 0,
        "W_DewPoint": 0,
        "W_pH": 0,
        "W_Cdct": 0,
        "W_Tbt": 0,
        "W_AC": 0,
        "W_Power": 0,
        "W_HeatCapacity": 0,
        "A_TempClntSply": 0,
        "A_TempClntSplySpare": 0,
        "A_TempClntRtn": 0,
        "A_TempClntRtnSpare": 0,
        "A_PrsrClntSply": 0,
        "A_PrsrClntSplySpare": 0,
        "A_PrsrClntRtn": 0,
        "A_PrsrClntRtnSpare": 0,
        "A_PrsrFltIn": 0,
        "A_PrsrFltOut": 0,
        "A_ClntFlow": 0,
        "A_AmbientTemp": 0,
        "A_RelativeHumid": 0,
        "A_DewPoint": 0,
        "A_pH": 0,
        "A_Cdct": 0,
        "A_Tbt": 0,
        "A_AC": 0,
        "A_Power": 0,
        "A_HeatCapacity": 0,
        "Delay_TempClntSply": 0,
        "Delay_TempClntSplySpare": 0,
        "Delay_TempClntRtn": 0,
        "Delay_TempClntRtnSpare": 0,
        "Delay_PrsrClntSply": 0,
        "Delay_PrsrClntSplySpare": 0,
        "Delay_PrsrClntRtn": 0,
        "Delay_PrsrClntRtnSpare": 0,
        "Delay_PrsrFltIn": 0,
        "Delay_PrsrFltOut": 0,
        "Delay_ClntFlow": 0,
        "Delay_AmbientTemp": 0,
        "Delay_RelativeHumid": 0,
        "Delay_DewPoint": 0,
        "Delay_pH": 0,
        "Delay_Cdct": 0,
        "Delay_Tbt": 0,
        "Delay_AC": 0,
        "Delay_Inv1_OverLoad": 0,
        "Delay_Inv2_OverLoad": 0,
        "Delay_Inv3_OverLoad": 0,
        "Delay_Fan_OverLoad1": 0,
        "Delay_Fan_OverLoad2": 0,
        "Delay_Inv1_Error": 0,
        "Delay_Inv2_Error": 0,
        "Delay_Inv3_Error": 0,
        "Delay_ATS": 0,
        "Delay_Inverter1_Communication": 0,
        "Delay_Inverter2_Communication": 0,
        "Delay_Inverter3_Communication": 0,
        "Delay_Coolant_Flow_Meter_Communication": 0,
        "Delay_AmbientTemp_Communication": 0,
        "Delay_RelativeHumid_Communication": 0,
        "Delay_DewPoint_Communication": 0,
        "Delay_Conductivity_Sensor_Communication": 0,
        "Delay_pH_Sensor_Communication": 0,
        "Delay_Turbidity_Sensor_Communication": 0,
        "Delay_ATS1_Communication": 0,
        "Delay_ATS2_Communication": 0,
        "Delay_Power_Meter_Communication": 0,
        "Delay_average_current_Communication": 0,
        "Delay_Fan1Com_Communication": 0,
        "Delay_Fan2Com_Communication": 0,
        "Delay_Fan3Com_Communication": 0,
        "Delay_Fan4Com_Communication": 0,
        "Delay_Fan5Com_Communication": 0,
        "Delay_Fan6Com_Communication": 0,
        "Delay_Fan7Com_Communication": 0,
        "Delay_Fan8Com_Communication": 0,
        "Delay_TempClntSply_broken": 0,
        "Delay_TempClntSplySpare_broken": 0,
        "Delay_TempClntRtn_broken": 0,
        "Delay_TempClntRtnSpare_broken": 0,
        "Delay_PrsrClntSply_broken": 0,
        "Delay_PrsrClntSplySpare_broken": 0,
        "Delay_PrsrClntRtn_broken": 0,
        "Delay_PrsrClntRtnSpare_broken": 0,
        "Delay_PrsrFltIn_broken": 0,
        "Delay_PrsrFltOut_broken": 0,
        "Delay_Clnt_Flow_broken": 0,
        "Delay_leakage1_leak": 0,
        "Delay_leakage1_broken": 0,
        "Delay_level1": 0,
        "Delay_level2": 0,
        "Delay_level3": 0,
        "Delay_power24v1": 0,
        "Delay_power24v2": 0,
        "Delay_power12v1": 0,
        "Delay_power12v2": 0,
        "Delay_main_mc_error": 0,
        "Delay_fan1_error": 0,
        "Delay_fan2_error": 0,
        "Delay_fan3_error": 0,
        "Delay_fan4_error": 0,
        "Delay_fan5_error": 0,
        "Delay_fan6_error": 0,
        "Delay_fan7_error": 0,
        "Delay_fan8_error": 0,
        "Delay_rack_error": 0,
    },
    "end": {
        "W_TempClntSply": 0,
        "W_TempClntSplySpare": 0,
        "W_TempClntRtn": 0,
        "W_TempClntRtnSpare": 0,
        "W_PrsrClntSply": 0,
        "W_PrsrClntSplySpare": 0,
        "W_PrsrClntRtn": 0,
        "W_PrsrClntRtnSpare": 0,
        "W_PrsrFltIn": 0,
        "W_PrsrFltOut": 0,
        "W_ClntFlow": 0,
        "W_AmbientTemp": 0,
        "W_RelativeHumid": 0,
        "W_DewPoint": 0,
        "W_pH": 0,
        "W_Cdct": 0,
        "W_Tbt": 0,
        "W_AC": 0,
        "W_Power": 0,
        "W_HeatCapacity": 0,
        "A_TempClntSply": 0,
        "A_TempClntSplySpare": 0,
        "A_TempClntRtn": 0,
        "A_TempClntRtnSpare": 0,
        "A_PrsrClntSply": 0,
        "A_PrsrClntSplySpare": 0,
        "A_PrsrClntRtn": 0,
        "A_PrsrClntRtnSpare": 0,
        "A_PrsrFltIn": 0,
        "A_PrsrFltOut": 0,
        "A_ClntFlow": 0,
        "A_AmbientTemp": 0,
        "A_RelativeHumid": 0,
        "A_DewPoint": 0,
        "A_pH": 0,
        "A_Cdct": 0,
        "A_Tbt": 0,
        "A_AC": 0,
        "A_Power": 0,
        "A_HeatCapacity": 0,
        "Delay_TempClntSply": 0,
        "Delay_TempClntSplySpare": 0,
        "Delay_TempClntRtn": 0,
        "Delay_TempClntRtnSpare": 0,
        "Delay_PrsrClntSply": 0,
        "Delay_PrsrClntSplySpare": 0,
        "Delay_PrsrClntRtn": 0,
        "Delay_PrsrClntRtnSpare": 0,
        "Delay_PrsrFltIn": 0,
        "Delay_PrsrFltOut": 0,
        "Delay_ClntFlow": 0,
        "Delay_AmbientTemp": 0,
        "Delay_RelativeHumid": 0,
        "Delay_DewPoint": 0,
        "Delay_pH": 0,
        "Delay_Cdct": 0,
        "Delay_Tbt": 0,
        "Delay_AC": 0,
        "Delay_Inv1_OverLoad": 0,
        "Delay_Inv2_OverLoad": 0,
        "Delay_Inv3_OverLoad": 0,
        "Delay_Fan_OverLoad1": 0,
        "Delay_Fan_OverLoad2": 0,
        "Delay_Inv1_Error": 0,
        "Delay_Inv2_Error": 0,
        "Delay_Inv3_Error": 0,
        "Delay_ATS": 0,
        "Delay_Inverter1_Communication": 0,
        "Delay_Inverter2_Communication": 0,
        "Delay_Inverter3_Communication": 0,
        "Delay_Coolant_Flow_Meter_Communication": 0,
        "Delay_AmbientTemp_Communication": 0,
        "Delay_RelativeHumid_Communication": 0,
        "Delay_DewPoint_Communication": 0,
        "Delay_pH_Sensor_Communication": 0,
        "Delay_Conductivity_Sensor_Communication": 0,
        "Delay_Turbidity_Sensor_Communication": 0,
        "Delay_ATS1_Communication": 0,
        "Delay_ATS2_Communication": 0,
        "Delay_Power_Meter_Communication": 0,
        "Delay_average_current_Communication": 0,
        "Delay_Fan1Com_Communication": 0,
        "Delay_Fan2Com_Communication": 0,
        "Delay_Fan3Com_Communication": 0,
        "Delay_Fan4Com_Communication": 0,
        "Delay_Fan5Com_Communication": 0,
        "Delay_Fan6Com_Communication": 0,
        "Delay_Fan7Com_Communication": 0,
        "Delay_Fan8Com_Communication": 0,
        "Delay_TempClntSply_broken": 0,
        "Delay_TempClntSplySpare_broken": 0,
        "Delay_TempClntRtn_broken": 0,
        "Delay_TempClntRtnSpare_broken": 0,
        "Delay_PrsrClntSply_broken": 0,
        "Delay_PrsrClntSplySpare_broken": 0,
        "Delay_PrsrClntRtn_broken": 0,
        "Delay_PrsrClntRtnSpare_broken": 0,
        "Delay_PrsrFltIn_broken": 0,
        "Delay_PrsrFltOut_broken": 0,
        "Delay_Clnt_Flow_broken": 0,
        "Delay_leakage1_leak": 0,
        "Delay_leakage1_broken": 0,
        "Delay_level1": 0,
        "Delay_level2": 0,
        "Delay_level3": 0,
        "Delay_power24v1": 0,
        "Delay_power24v2": 0,
        "Delay_power12v1": 0,
        "Delay_power12v2": 0,
        "Delay_main_mc_error": 0,
        "Delay_fan1_error": 0,
        "Delay_fan2_error": 0,
        "Delay_fan3_error": 0,
        "Delay_fan4_error": 0,
        "Delay_fan5_error": 0,
        "Delay_fan6_error": 0,
        "Delay_fan7_error": 0,
        "Delay_fan8_error": 0,
        "Delay_rack_error": 0,
    },
    "check": {
        "W_TempClntSply": 0,
        "W_TempClntSplySpare": 0,
        "W_TempClntRtn": 0,
        "W_TempClntRtnSpare": 0,
        "W_PrsrClntSply": 0,
        "W_PrsrClntSplySpare": 0,
        "W_PrsrClntRtn": 0,
        "W_PrsrClntRtnSpare": 0,
        "W_PrsrFltIn": 0,
        "W_PrsrFltOut": 0,
        "W_ClntFlow": 0,
        "W_AmbientTemp": 0,
        "W_RelativeHumid": 0,
        "W_DewPoint": 0,
        "W_pH": 0,
        "W_Cdct": 0,
        "W_Tbt": 0,
        "W_AC": 0,
        "W_Power": 0,
        "W_HeatCapacity": 0,
        "A_TempClntSply": 0,
        "A_TempClntSplySpare": 0,
        "A_TempClntRtn": 0,
        "A_TempClntRtnSpare": 0,
        "A_PrsrClntSply": 0,
        "A_PrsrClntSplySpare": 0,
        "A_PrsrClntRtn": 0,
        "A_PrsrClntRtnSpare": 0,
        "A_PrsrFltIn": 0,
        "A_PrsrFltOut": 0,
        "A_ClntFlow": 0,
        "A_AmbientTemp": 0,
        "A_RelativeHumid": 0,
        "A_DewPoint": 0,
        "A_pH": 0,
        "A_Cdct": 0,
        "A_Tbt": 0,
        "A_AC": 0,
        "A_Power": 0,
        "A_HeatCapacity": 0,
        "Delay_TempClntSply": 0,
        "Delay_TempClntSplySpare": 0,
        "Delay_TempClntRtn": 0,
        "Delay_TempClntRtnSpare": 0,
        "Delay_PrsrClntSply": 0,
        "Delay_PrsrClntSplySpare": 0,
        "Delay_PrsrClntRtn": 0,
        "Delay_PrsrClntRtnSpare": 0,
        "Delay_PrsrFltIn": 0,
        "Delay_PrsrFltOut": 0,
        "Delay_ClntFlow": 0,
        "Delay_AmbientTemp": 0,
        "Delay_RelativeHumid": 0,
        "Delay_DewPoint": 0,
        "Delay_pH": 0,
        "Delay_Cdct": 0,
        "Delay_Tbt": 0,
        "Delay_AC": 0,
        "Delay_Inv1_OverLoad": 0,
        "Delay_Inv2_OverLoad": 0,
        "Delay_Inv3_OverLoad": 0,
        "Delay_Fan_OverLoad1": 0,
        "Delay_Fan_OverLoad2": 0,
        "Delay_Inv1_Error": 0,
        "Delay_Inv2_Error": 0,
        "Delay_Inv3_Error": 0,
        "Delay_ATS": 0,
        "Delay_Inverter1_Communication": 0,
        "Delay_Inverter2_Communication": 0,
        "Delay_Inverter3_Communication": 0,
        "Delay_Coolant_Flow_Meter_Communication": 0,
        "Delay_AmbientTemp_Communication": 0,
        "Delay_RelativeHumid_Communication": 0,
        "Delay_DewPoint_Communication": 0,
        "Delay_pH_Sensor_Communication": 0,
        "Delay_Conductivity_Sensor_Communication": 0,
        "Delay_Turbidity_Sensor_Communication": 0,
        "Delay_ATS1_Communication": 0,
        "Delay_ATS2_Communication": 0,
        "Delay_Power_Meter_Communication": 0,
        "Delay_average_current_Communication": 0,
        "Delay_Fan1Com_Communication": 0,
        "Delay_Fan2Com_Communication": 0,
        "Delay_Fan3Com_Communication": 0,
        "Delay_Fan4Com_Communication": 0,
        "Delay_Fan5Com_Communication": 0,
        "Delay_Fan6Com_Communication": 0,
        "Delay_Fan7Com_Communication": 0,
        "Delay_Fan8Com_Communication": 0,
        "Delay_TempClntSply_broken": 0,
        "Delay_TempClntSplySpare_broken": 0,
        "Delay_TempClntRtn_broken": 0,
        "Delay_TempClntRtnSpare_broken": 0,
        "Delay_PrsrClntSply_broken": 0,
        "Delay_PrsrClntSplySpare_broken": 0,
        "Delay_PrsrClntRtn_broken": 0,
        "Delay_PrsrClntRtnSpare_broken": 0,
        "Delay_PrsrFltIn_broken": 0,
        "Delay_PrsrFltOut_broken": 0,
        "Delay_Clnt_Flow_broken": 0,
        "Delay_leakage1_leak": 0,
        "Delay_leakage1_broken": 0,
        "Delay_level1": 0,
        "Delay_level2": 0,
        "Delay_level3": 0,
        "Delay_power24v1": 0,
        "Delay_power24v2": 0,
        "Delay_power12v1": 0,
        "Delay_power12v2": 0,
        "Delay_main_mc_error": 0,
        "Delay_fan1_error": 0,
        "Delay_fan2_error": 0,
        "Delay_fan3_error": 0,
        "Delay_fan4_error": 0,
        "Delay_fan5_error": 0,
        "Delay_fan6_error": 0,
        "Delay_fan7_error": 0,
        "Delay_fan8_error": 0,
        "Delay_rack_error": 0,
    },
    "condition": {
        "low": {
            "W_pH": False,
            "W_AmbientTemp": False,
            "W_RelativeHumid": False,
            "W_DewPoint": False,
            "W_PrsrFltIn": False,
            "W_Cdct": False,
            "W_Tbt": False,
            "A_pH": False,
            "A_Cdct": False,
            "A_Tbt": False,
            "A_AmbientTemp": False,
            "A_RelativeHumid": False,
            "A_PrsrFltIn": False,
        },
        "high": {
            "W_pH": False,
            "W_AmbientTemp": False,
            "W_RelativeHumid": False,
            "W_DewPoint": False,
            "W_PrsrFltIn": False,
            "W_Cdct": False,
            "W_Tbt": False,
            "A_pH": False,
            "A_Cdct": False,
            "A_Tbt": False,
            "A_AmbientTemp": False,
            "A_RelativeHumid": False,
            "A_PrsrFltIn": False,
        },
    },
}


overload_error = {
    "Inv1_OverLoad": False,
    "Inv2_OverLoad": False,
    "Inv3_OverLoad": False,
    "Fan_OverLoad1": False,
    "Fan_OverLoad2": False,
}


restart_server = {"stage": 0, "start": 0, "diff": 0}

server_error = {"start": 0, "diff": 0}


warning_data = {
    "warning": {
        "TempClntSply_High": False,
        "TempClntSplySpare_High": False,
        "TempClntRtn_High": False,
        "TempClntRtnSpare_High": False,
        "PrsrClntSply_High": False,
        "PrsrClntSplySpare_High": False,
        "PrsrClntRtn_High": False,
        "PrsrClntRtnSpare_High": False,
        "Prsr_FltIn_Low": False,
        "Prsr_FltIn_High": False,
        "Prsr_FltOut_High": False,
        "ClntFlow_Low": False,
        "AmbientTemp_Low": False,
        "AmbientTemp_High": False,
        "RelativeHumid_Low": False,
        "RelativeHumid_High": False,
        "DewPoint_Low": False,
        "pH_Low": False,
        "pH_High": False,
        "Cdct_Low": False,
        "Cdct_High": False,
        "Tbt_Low": False,
        "Tbt_High": False,
        "AC_High": False,
    },
    "alert": {
        "TempClntSply_High": False,
        "TempClntSplySpare_High": False,
        "TempClntRtn_High": False,
        "TempClntRtnSpare_High": False,
        "PrsrClntSply_High": False,
        "PrsrClntSplySpare_High": False,
        "PrsrClntRtn_High": False,
        "PrsrClntRtnSpare_High": False,
        "Prsr_FltIn_Low": False,
        "Prsr_FltIn_High": False,
        "Prsr_FltOut_High": False,
        "ClntFlow_Low": False,
        "AmbientTemp_Low": False,
        "AmbientTemp_High": False,
        "RelativeHumid_Low": False,
        "RelativeHumid_High": False,
        "DewPoint_Low": False,
        "pH_Low": False,
        "pH_High": False,
        "Cdct_Low": False,
        "Cdct_High": False,
        "Tbt_Low": False,
        "Tbt_High": False,
        "AC_High": False,
    },
    "error": {
        "Inv1_OverLoad": False,
        "Inv2_OverLoad": False,
        "Inv3_OverLoad": False,
        "Fan_OverLoad1": False,
        "Fan_OverLoad2": False,
        "Inv1_Error": False,
        "Inv2_Error": False,
        "Inv3_Error": False,
        "ATS1_Error": False,
        "Inv1_Freq_communication": 0,
        "Inv2_Freq_communication": 0,
        "Inv3_Freq_communication": 0,
        "coolant_flow_rate_communication": False,
        "AmbientTemp_communication": False,
        "RelativeHumid_communication": False,
        "DewPoint_communication": False,
        "pH_communication": False,
        "conductivity_communication": False,
        "turbidity_communication": False,
        "ATS1_communication": False,
        "ATS2_communication": False,
        "inst_power_communication": False,
        "average_current_communication": False,
        "Fan1Com_communication": False,
        "Fan2Com_communication": False,
        "Fan3Com_communication": False,
        "Fan4Com_communication": False,
        "Fan5Com_communication": False,
        "Fan6Com_communication": False,
        "Fan7Com_communication": False,
        "Fan8Com_communication": False,
        "Temp_ClntSply_broken": False,
        "Temp_ClntSplySpare_broken": False,
        "Temp_ClntRtn_broken": False,
        "Temp_ClntRtnSpare_broken": False,
        "Prsr_ClntSply_broken": False,
        "Prsr_ClntSplySpare_broken": False,
        "Prsr_ClntRtn_broken": False,
        "Prsr_ClntRtnSpare_broken": False,
        "Prsr_FltIn_broken": False,
        "Prsr_FltOut_broken": False,
        "Clnt_Flow_broken": False,
        "pc1_error": False,
        "pc2_error": False,
        "leakage1_leak": False,
        "leakage1_broken": False,
        "level1": False,
        "level2": False,
        "level3": False,
        "power24v1": False,
        "power24v2": False,
        "power12v1": False,
        "power12v2": False,
        "main_mc_error": False,
        "fan1_error": False,
        "fan2_error": False,
        "fan3_error": False,
        "fan4_error": False,
        "fan5_error": False,
        "fan6_error": False,
        "fan7_error": False,
        "fan8_error": False,
        "Low_Coolant_Level_Warning": False,
    },
}

ats_status = {
    "ATS1": False,
    "ATS2": False,
}

level_sw = {
    "level1": None,
    "level2": None,
    "level3": None,
    "power24v1": None,
    "power24v2": None,
    "power12v1": None,
    "power12v2": None,
}


def check_inverter(inv):
    return (
        warning_data["error"][f"{inv}_Error"]
        or warning_data["error"][f"{inv}_OverLoad"]
        or warning_data["error"][f"{inv}_Freq_communication"]
    )


def combine_bits(lower, upper):
    value = (upper << 16) | lower
    return value


def read_split_register(r, i):
    lower_16 = r[i]
    upper_16 = r[i + 1]
    value = combine_bits(lower_16, upper_16)
    return value


def split_double(Dword_list):
    registers = []

    for d in Dword_list:
        lower_16 = d & 0xFFFF
        upper_16 = (d >> 16) & 0xFFFF

        registers.append(lower_16)
        registers.append(upper_16)
    return registers


def cvt_registers_to_float(reg1, reg2):
    temp1 = [reg1, reg2]
    decoder_big_endian = BinaryPayloadDecoder.fromRegisters(
        temp1, byteorder=Endian.Big, wordorder=Endian.Little
    )
    decoded_value_big_endian = decoder_big_endian.decode_32bit_float()
    return decoded_value_big_endian


def cvt_float_byte(value):
    float_as_bytes = struct.pack(">f", float(value))
    word1, word2 = struct.unpack(">HH", float_as_bytes)
    return word1, word2


def change_progress(key, status):
    if status == "standby":
        inspection_data["prog"][key] = 4

    elif status == "finish":
        inspection_data["prog"][key] = 2

    elif status == "skip":
        inspection_data["prog"][key] = 5

    elif status == "cancel":
        inspection_data["prog"][key] = 1


def send_all(number, key):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_registers((800 + number), inspection_data["prog"][key])

            result = [1 if inspection_data["result"][key] else 0]
            client.write_registers((750 + number), result)
    except Exception as e:
        print(f"result write-in:{e}")


def send_progress(number, key):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_registers((800 + number), inspection_data["prog"][key])
    except Exception as e:
        print(f"result write-in:{e}")


def thr_check():
    global thrshd_data
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            thr_reg = (sum(1 for key in thrshd_data if "Thr_" in key)) * 2
            delay_reg = sum(1 for key in thrshd_data if "Delay_" in key)
            start_address = 1000
            total_registers = thr_reg
            read_num = 120

            for counted_num in range(0, total_registers, read_num):
                count = min(read_num, total_registers - counted_num)
                result = client.read_holding_registers(
                    start_address + counted_num, count, unit=modbus_slave_id
                )

                if result.isError():
                    print(f"Modbus Errorxxx: {result}")
                    continue
                else:
                    keys_list = list(thrshd_data.keys())
                    j = counted_num // 2
                    for i in range(0, count, 2):
                        if i + 1 < len(result.registers) and j < len(keys_list):
                            temp1 = [
                                result.registers[i],
                                result.registers[i + 1],
                            ]
                            decoder_big_endian = BinaryPayloadDecoder.fromRegisters(
                                temp1,
                                byteorder=Endian.Big,
                                wordorder=Endian.Little,
                            )
                            decoded_value_big_endian = (
                                decoder_big_endian.decode_32bit_float()
                            )
                            thrshd_data[keys_list[j]] = decoded_value_big_endian
                            j += 1

            result = client.read_holding_registers(
                1000 + thr_reg, delay_reg, unit=modbus_slave_id
            )

            if result.isError():
                print(f"Modbus Error: {result}")
            else:
                keys_list = list(thrshd_data.keys())
                j = int(thr_reg / 2)
                for i in range(0, delay_reg):
                    thrshd_data[keys_list[j]] = result.registers[i]
                    j += 1
    except Exception as e:
        print(f"thrshd check error：{e}")


def status_check():
    global status_data
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            ad_count = len(ad_sensor_value.keys())
            serial_count = len(serial_sensor_value.keys())
            all_count = ad_count+(serial_count*2)

            r = client.read_holding_registers(5000, all_count, unit=modbus_slave_id)

            if r.isError():
                print(f"modbus error:{r}")
            else:
                key_list = list(status_data.keys())
                j = 0

                for i in range(0, all_count, 2):
                    temp1 = [r.registers[i], r.registers[i + 1]]
                    decoder_big_endian = BinaryPayloadDecoder.fromRegisters(
                        temp1, byteorder=Endian.Big, wordorder=Endian.Little
                    )
                    decoded_value_big_endian = decoder_big_endian.decode_32bit_float()
                    status_data[key_list[j]] = decoded_value_big_endian
                    j += 1
    except Exception as e:
        print(f"read status data error：{e}")


def check_input(delay, value_key, criteria):
    if criteria:
        try:
            if time_data["check"][delay]:
                if not bit_input_regs[value_key]:
                    time_data["check"][delay] = False
                    warning_data["error"][value_key] = False
                else:
                    time_data["end"][delay] = time.perf_counter()

                    passed_time = time_data["end"][delay] - time_data["start"][delay]

                    if passed_time > thrshd_data[delay]:
                        warning_data["error"][value_key] = True
            else:
                if bit_input_regs[value_key]:
                    time_data["start"][delay] = time.perf_counter()
                    time_data["check"][delay] = True
                else:
                    warning_data["error"][value_key] = False
        except Exception as e:
            print(f"check error：{e}")
    else:
        try:
            if time_data["check"][delay]:
                if bit_input_regs[value_key]:
                    time_data["check"][delay] = False
                    warning_data["error"][value_key] = False
                else:
                    time_data["end"][delay] = time.perf_counter()

                    passed_time = time_data["end"][delay] - time_data["start"][delay]

                    if passed_time > thrshd_data[delay]:
                        warning_data["error"][value_key] = True
            else:
                if not bit_input_regs[value_key]:
                    time_data["start"][delay] = time.perf_counter()
                    time_data["check"][delay] = True
                else:
                    warning_data["error"][value_key] = False
        except Exception as e:
            print(f"check error：{e}")


def check_high_warning(thr_key, rst_key, delay_key, type):
    short_key = thr_key.split("_")[2]

    prefix = "W_" if type == "W" else "A_"

    try:
        if time_data["check"][prefix + short_key]:
            if status_data[short_key] < thrshd_data[rst_key]:
                time_data["check"][prefix + short_key] = False
                if prefix.startswith("W_"):
                    warning_data["warning"][short_key + "_High"] = False
                else:
                    warning_data["alert"][short_key + "_High"] = False
                return False
            else:
                time_data["end"][prefix + short_key] = time.perf_counter()

                passed_time = (
                    time_data["end"][prefix + short_key]
                    - time_data["start"][prefix + short_key]
                )

                if passed_time > thrshd_data[delay_key]:
                    if prefix.startswith("W_"):
                        warning_data["warning"][short_key + "_High"] = True
                    else:
                        warning_data["alert"][short_key + "_High"] = True

                    return True
        else:
            if status_data[short_key] > thrshd_data[thr_key]:
                time_data["start"][prefix + short_key] = time.perf_counter()
                time_data["check"][prefix + short_key] = True
            else:
                time_data["check"][prefix + short_key] = False
                if prefix.startswith("W_"):
                    warning_data["warning"][short_key + "_High"] = False
                else:
                    warning_data["alert"][short_key + "_High"] = False
                return False
    except Exception as e:
        print(f"high warning check error：{e}")


def check_low_warning(thr_key, rst_key, delay_key, type):
    short_key = thr_key.split("_")[2]

    prefix = "W_" if type == "W" else "A_"

    try:
        if time_data["check"][prefix + short_key]:
            if status_data[short_key] > thrshd_data[rst_key]:
                time_data["check"][prefix + short_key] = False
                if prefix.startswith("W_"):
                    warning_data["warning"][short_key + "_Low"] = False
                else:
                    warning_data["alert"][short_key + "_Low"] = False
                return False
            else:
                time_data["end"][prefix + short_key] = time.perf_counter()

                passed_time = (
                    time_data["end"][prefix + short_key]
                    - time_data["start"][prefix + short_key]
                )

                if passed_time > thrshd_data[delay_key]:
                    if prefix.startswith("W_"):
                        warning_data["warning"][short_key + "_Low"] = True
                    else:
                        warning_data["alert"][short_key + "_Low"] = True
                    return True
        else:
            if status_data[short_key] < thrshd_data[thr_key]:
                time_data["start"][prefix + short_key] = time.perf_counter()
                time_data["check"][prefix + short_key] = True
            else:
                if prefix.startswith("W_"):
                    warning_data["warning"][short_key + "_Low"] = False
                else:
                    warning_data["alert"][short_key + "_Low"] = False
                return False
    except Exception as e:
        print(f"low warning check error：{e}")


def check_both_warning_p3(
    thr_key_low, thr_key_high, rst_key_low, rst_key_high, delay_key, type
):
    short_key = thr_key_low.split("_")[2]
    status = status_data[short_key]

    prefix = "W_" if type == "W" else "A_"

    try:
        if time_data["check"][prefix + short_key]:
            if (
                thrshd_data[rst_key_low] < status and status < thrshd_data[rst_key_high]
            ) or (not inv["inv1"] and not inv["inv2"] and not inv["inv3"]):
                time_data["check"][prefix + short_key] = False
                time_data["condition"]["high"][prefix + short_key] = False
                time_data["condition"]["low"][prefix + short_key] = False

            else:
                if status > thrshd_data[thr_key_high]:
                    time_data["end"][prefix + short_key] = time.perf_counter()

                    passed_time = (
                        time_data["end"][prefix + short_key]
                        - time_data["start"][prefix + short_key]
                    )

                    if passed_time > thrshd_data[delay_key]:
                        time_data["condition"]["high"][prefix + short_key] = True

                if status < thrshd_data[thr_key_low]:
                    time_data["end"][prefix + short_key] = time.perf_counter()
                    passed_time = (
                        time_data["end"][prefix + short_key]
                        - time_data["start"][prefix + short_key]
                    )
                    if passed_time > thrshd_data[delay_key]:
                        time_data["condition"]["low"][prefix + short_key] = True
        else:
            if (
                status > thrshd_data[thr_key_high] or status < thrshd_data[thr_key_low]
            ) and (inv["inv1"] or inv["inv2"] or inv["inv3"]):
                time_data["start"][prefix + short_key] = time.perf_counter()
                time_data["check"][prefix + short_key] = True
            else:
                time_data["condition"]["high"][prefix + short_key] = False
                time_data["condition"]["low"][prefix + short_key] = False

        if time_data["condition"]["high"][prefix + short_key]:
            if prefix.startswith("W_"):
                warning_data["warning"][short_key + "_High"] = True
            else:
                warning_data["alert"][short_key + "_High"] = True

        if time_data["condition"]["low"][prefix + short_key]:
            if prefix.startswith("W_"):
                warning_data["warning"][short_key + "_Low"] = True
            else:
                warning_data["alert"][short_key + "_Low"] = True

        if (
            not time_data["condition"]["high"][prefix + short_key]
            and not time_data["condition"]["low"][prefix + short_key]
        ):
            if prefix.startswith("W_"):
                warning_data["warning"][short_key + "_High"] = False
                warning_data["warning"][short_key + "_Low"] = False
            else:
                warning_data["alert"][short_key + "_High"] = False
                warning_data["alert"][short_key + "_Low"] = False

    except Exception as e:
        print(f"check both warning error：{e}")


def check_low_warning_f1(thr_key, rst_key, delay_key, type):
    short_key = "ClntFlow"

    prefix = "W_" if type == "W" else "A_"

    try:
        if time_data["check"][prefix + short_key]:
            if (status_data[short_key] > thrshd_data[rst_key]) or (
                not inv["inv1"] and not inv["inv2"] and not inv["inv3"]
            ):
                time_data["check"][prefix + short_key] = False
                if prefix.startswith("W_"):
                    warning_data["warning"][short_key + "_Low"] = False
                else:
                    warning_data["alert"][short_key + "_Low"] = False
                return False
            else:
                time_data["end"][prefix + short_key] = time.perf_counter()

                passed_time = (
                    time_data["end"][prefix + short_key]
                    - time_data["start"][prefix + short_key]
                )

                if passed_time > thrshd_data[delay_key]:
                    if prefix.startswith("W_"):
                        warning_data["warning"][short_key + "_Low"] = True
                    else:
                        warning_data["alert"][short_key + "_Low"] = True

                    return True
        else:
            if (status_data[short_key] < thrshd_data[thr_key]) and (
                inv["inv1"] or inv["inv2"] or inv["inv3"]
            ):
                time_data["start"][prefix + short_key] = time.perf_counter()
                time_data["check"][prefix + short_key] = True
            else:
                if prefix.startswith("W_"):
                    warning_data["warning"][short_key + "_Low"] = False
                else:
                    warning_data["alert"][short_key + "_Low"] = False
                return False
    except Exception as e:
        print(f"low warning check error：{e}")


def check_both_warning(
    thr_key_low, thr_key_high, rst_key_low, rst_key_high, delay_key, type
):
    short_key = thr_key_low.split("_")[2]
    status = status_data[short_key]

    prefix = "W_" if type == "W" else "A_"

    try:
        if time_data["check"][prefix + short_key]:
            if thrshd_data[rst_key_low] < status and status < thrshd_data[rst_key_high]:
                time_data["check"][prefix + short_key] = False
                time_data["condition"]["high"][prefix + short_key] = False
                time_data["condition"]["low"][prefix + short_key] = False

            else:
                if status > thrshd_data[thr_key_high]:
                    time_data["end"][prefix + short_key] = time.perf_counter()

                    passed_time = (
                        time_data["end"][prefix + short_key]
                        - time_data["start"][prefix + short_key]
                    )

                    if passed_time > thrshd_data[delay_key]:
                        time_data["condition"]["high"][prefix + short_key] = True

                if status < thrshd_data[thr_key_low]:
                    time_data["end"][prefix + short_key] = time.perf_counter()
                    passed_time = (
                        time_data["end"][prefix + short_key]
                        - time_data["start"][prefix + short_key]
                    )
                    if passed_time > thrshd_data[delay_key]:
                        time_data["condition"]["low"][prefix + short_key] = True

        else:
            if status > thrshd_data[thr_key_high] or status < thrshd_data[thr_key_low]:
                time_data["start"][prefix + short_key] = time.perf_counter()
                time_data["check"][prefix + short_key] = True

        if time_data["condition"]["high"][prefix + short_key]:
            if prefix.startswith("W_"):
                warning_data["warning"][short_key + "_High"] = True
            else:
                warning_data["alert"][short_key + "_High"] = True

        if time_data["condition"]["low"][prefix + short_key]:
            if prefix.startswith("W_"):
                warning_data["warning"][short_key + "_Low"] = True
            else:
                warning_data["alert"][short_key + "_Low"] = True

        if (
            not time_data["condition"]["high"][prefix + short_key]
            and not time_data["condition"]["low"][prefix + short_key]
        ):
            if prefix.startswith("W_"):
                warning_data["warning"][short_key + "_High"] = False
                warning_data["warning"][short_key + "_Low"] = False
            else:
                warning_data["alert"][short_key + "_High"] = False
                warning_data["alert"][short_key + "_Low"] = False

    except Exception as e:
        print(f"check both warning error：{e}")


def check_overload_error(delay):
    short_key = delay.replace("Delay_", "")

    try:
        if time_data["check"][delay]:
            if not overload_error[short_key]:
                time_data["check"][delay] = False
                warning_data["error"][short_key] = False
            else:
                time_data["end"][delay] = time.perf_counter()

                passed_time = time_data["end"][delay] - time_data["start"][delay]

                if passed_time > thrshd_data[delay]:
                    warning_data["error"][delay] = True
        else:
            if overload_error[short_key]:
                time_data["start"][delay] = time.perf_counter()
                time_data["check"][delay] = True
            else:
                warning_data["error"][delay] = False
    except Exception as e:
        print(f"inverter overload error：{e}")


def check_ATS(delay):
    try:
        if time_data["check"][delay]:
            if ats_status["ATS1"]:
                warning_data["error"]["ATS1_Error"] = False
                time_data["check"][delay] = False
                return False
            else:
                time_data["end"][delay] = time.perf_counter()

                passed_time = time_data["end"][delay] - time_data["start"][delay]

                if passed_time > thrshd_data[delay]:
                    warning_data["error"]["ATS1_Error"] = True
                    return True
        else:
            if not ats_status["ATS1"]:
                time_data["start"][delay] = time.perf_counter()
                time_data["check"][delay] = True
            else:
                warning_data["error"]["ATS1_Error"] = False
                return False
    except Exception as e:
        print(f"ats check error：{e}")


def check_level(delay, value_key):
    try:
        if time_data["check"][delay]:
            if level_sw[value_key]:
                time_data["check"][delay] = False
                warning_data["error"][delay] = False
            else:
                time_data["end"][delay] = time.perf_counter()

                passed_time = time_data["end"][delay] - time_data["start"][delay]

                if passed_time > thrshd_data[delay]:
                    warning_data["error"][delay] = True
        else:
            if not level_sw[value_key] and level_sw[value_key] is not None:
                time_data["start"][delay] = time.perf_counter()
                time_data["check"][delay] = True
            else:
                warning_data["error"][delay] = False
    except Exception as e:
        print(f"check level error：{e}")


def check_pressure_diff_error(thr_key, rst_key, delay_key, type):
    short_key = thr_key.split("_")[2]

    if type == "W":
        prefix = "W_"
    elif type == "A":
        prefix = "A_"

    try:
        if time_data["check"][prefix + short_key]:
            if (status_data["PrsrFltIn"] - status_data[short_key]) < thrshd_data[
                rst_key
            ]:
                time_data["check"][prefix + short_key] = False
                if prefix.startswith("W_"):
                    warning_data["warning"][short_key + "_High"] = False
                else:
                    warning_data["alert"][short_key + "_High"] = False
                return False
            else:
                time_data["end"][prefix + short_key] = time.perf_counter()

                passed_time = (
                    time_data["end"][prefix + short_key]
                    - time_data["start"][prefix + short_key]
                )

                if passed_time > thrshd_data[delay_key]:
                    if prefix.startswith("W_"):
                        warning_data["warning"][short_key + "_High"] = True
                    else:
                        warning_data["alert"][short_key + "_High"] = True
                    return True
        else:
            if (status_data["PrsrFltIn"] - status_data[short_key]) > thrshd_data[
                thr_key
            ]:
                time_data["start"][prefix + short_key] = time.perf_counter()
                time_data["check"][prefix + short_key] = True
            else:
                warning_data[short_key + "_High"] = False
                return False
    except Exception as e:
        print(f"inlet outlet warning error：{e}")


def check_communication(short_key, delay):
    try:
        if time_data["check"][delay]:
            if not raw_485_comm[short_key]:
                time_data["check"][delay] = False
                warning_data["error"][short_key + "_communication"] = False
            else:
                time_data["end"][delay] = time.perf_counter()

                passed_time = time_data["end"][delay] - time_data["start"][delay]

                if passed_time > thrshd_data[delay]:
                    warning_data["error"][short_key + "_communication"] = True
        else:
            if raw_485_comm[short_key]:
                time_data["start"][delay] = time.perf_counter()
                time_data["check"][delay] = True
            else:
                warning_data["error"][short_key + "_communication"] = False
    except Exception as e:
        print(f"communication error：{e}")


def check_broken(key):
    broken_mapping = {
        "Temp_ClntSply": "Delay_TempClntSply_broken",
        "Temp_ClntSplySpare": "Delay_TempClntSplySpare_broken",
        "Temp_ClntRtn": "Delay_TempClntRtn_broken",
        "Temp_ClntRtnSpare": "Delay_TempClntRtnSpare_broken",
        "Prsr_ClntSply": "Delay_PrsrClntSply_broken",
        "Prsr_ClntSplySpare": "Delay_PrsrClntSplySpare_broken",
        "Prsr_ClntRtn": "Delay_PrsrClntRtn_broken",
        "Prsr_ClntRtnSpare": "Delay_PrsrClntRtnSpare_broken",
        "Prsr_FltIn": "Delay_PrsrFltIn_broken",
        "Prsr_FltOut": "Delay_PrsrFltOut_broken",
        "Clnt_Flow": "Delay_Clnt_Flow_broken",
    }

    delay_key = broken_mapping[key]
    error_key = f"{key}_broken"

    if "Temp" in key:
        try:
            if time_data["check"][delay_key]:
                if sensor_raw[key] < 1000 and sensor_raw[key] > -100:
                    time_data["check"][delay_key] = False
                    warning_data["error"][error_key] = False
                else:
                    time_data["end"][delay_key] = time.perf_counter()

                    passed_time = (
                        time_data["end"][delay_key] - time_data["start"][delay_key]
                    )

                    if passed_time > thrshd_data[delay_key]:
                        warning_data["error"][error_key] = True
            else:
                if sensor_raw[key] > 1000 or sensor_raw[key] < -100:
                    time_data["start"][delay_key] = time.perf_counter()
                    time_data["check"][delay_key] = True
                else:
                    warning_data["error"][error_key] = False
        except Exception as e:
            print(f"broken temp error：{e}")

    elif "Prsr" in key:
        try:
            if time_data["check"][delay_key]:
                if sensor_raw[key] > 1200:
                    time_data["check"][delay_key] = False
                    warning_data["error"][error_key] = False
                else:
                    time_data["end"][delay_key] = time.perf_counter()

                    passed_time = (
                        time_data["end"][delay_key] - time_data["start"][delay_key]
                    )

                    if passed_time > thrshd_data[delay_key]:
                        warning_data["error"][error_key] = True
            else:
                if sensor_raw[key] < 1200:
                    time_data["start"][delay_key] = time.perf_counter()
                    time_data["check"][delay_key] = True
                else:
                    warning_data["error"][error_key] = False
        except Exception as e:
            print(f"broken prsr error：{e}")

    if not ver_switch["flow_switch"]:
        if key == "Clnt_Flow":
            try:
                if time_data["check"][delay_key]:
                    if (
                        serial_sensor_value[key] > 1000
                        and serial_sensor_value[key] < 20000
                    ):
                        time_data["check"][delay_key] = False
                        warning_data["error"][error_key] = False
                    else:
                        time_data["end"][delay_key] = time.perf_counter()

                        passed_time = (
                            time_data["end"][delay_key] - time_data["start"][delay_key]
                        )

                        if passed_time > thrshd_data[delay_key]:
                            warning_data["error"][error_key] = True
                else:
                    if (
                        serial_sensor_value[key] < 1000
                        or serial_sensor_value[key] > 20000
                    ):
                        time_data["start"][delay_key] = time.perf_counter()
                        time_data["check"][delay_key] = True
                    else:
                        warning_data["error"][error_key] = False
            except Exception as e:
                print(f"broken flow error：{e}")


def check_dewPt_warning(thr_key, rst_key, delay_key, type):
    short_key = thr_key.split("_")[2]

    prefix = "W_" if type == "W" else "A_"

    t1 = warning_data["error"]["Temp_ClntSply_broken"]

    if t1:
        set_data = status_data["TempClntSplySpare"]
    else:
        set_data = status_data["TempClntSply"]

    try:
        if time_data["check"][prefix + short_key]:
            if set_data > status_data[short_key] + thrshd_data[rst_key]:
                time_data["check"][prefix + short_key] = False
                if prefix.startswith("W_"):
                    warning_data["warning"][short_key + "_Low"] = False
                else:
                    warning_data["alert"][short_key + "_Low"] = False
                return False
            else:
                time_data["end"][prefix + short_key] = time.perf_counter()

                passed_time = (
                    time_data["end"][prefix + short_key]
                    - time_data["start"][prefix + short_key]
                )

                if passed_time > thrshd_data[delay_key]:
                    # time_data["check"][prefix + short_key] = False
                    if prefix.startswith("W_"):
                        warning_data["warning"][short_key + "_Low"] = True
                    else:
                        warning_data["alert"][short_key + "_Low"] = True
                    return True
        else:
            if set_data < status_data[short_key] + thrshd_data[thr_key]:
                time_data["start"][prefix + short_key] = time.perf_counter()
                time_data["check"][prefix + short_key] = True
            else:
                if prefix.startswith("W_"):
                    warning_data["warning"][short_key + "_Low"] = False
                else:
                    warning_data["alert"][short_key + "_Low"] = False
                return False
    except Exception as e:
        print(f"check dewPt warning error：{e}")


def set_warning_registers(mode):
    global thrshd_data, status_data, x, warning_light

    thr_check()
    status_check()

    check_communication("Inv1_Freq", "Delay_Inverter1_Communication")
    check_communication("Inv2_Freq", "Delay_Inverter2_Communication")
    check_communication("Inv3_Freq", "Delay_Inverter3_Communication")
    check_communication("AmbientTemp", "Delay_AmbientTemp_Communication")
    check_communication("RelativeHumid", "Delay_RelativeHumid_Communication")
    check_communication("DewPoint", "Delay_DewPoint_Communication")
    check_communication("coolant_flow_rate", "Delay_Coolant_Flow_Meter_Communication")
    check_communication("conductivity", "Delay_Conductivity_Sensor_Communication")
    check_communication("pH", "Delay_pH_Sensor_Communication")
    check_communication("turbidity", "Delay_Turbidity_Sensor_Communication")
    check_communication("ATS1", "Delay_ATS1_Communication")
    check_communication("ATS2", "Delay_ATS2_Communication")
    check_communication("inst_power", "Delay_Power_Meter_Communication")
    check_communication("average_current", "Delay_average_current_Communication")
    check_communication("Fan1Com", "Delay_Fan1Com_Communication")
    check_communication("Fan2Com", "Delay_Fan2Com_Communication")
    check_communication("Fan3Com", "Delay_Fan3Com_Communication")
    check_communication("Fan4Com", "Delay_Fan4Com_Communication")
    check_communication("Fan5Com", "Delay_Fan5Com_Communication")
    check_communication("Fan6Com", "Delay_Fan6Com_Communication")
    check_communication("Fan7Com", "Delay_Fan7Com_Communication")
    check_communication("Fan8Com", "Delay_Fan8Com_Communication")

    check_level("Delay_level1", "level1")
    check_level("Delay_level2", "level2")
    check_level("Delay_level3", "level3")
    check_level("Delay_power24v1", "power24v1")
    check_level("Delay_power24v2", "power24v2")
    check_level("Delay_power12v1", "power12v1")
    check_level("Delay_power12v2", "power12v2")

    check_input("Delay_leakage1_leak", "leakage1_leak", True)
    check_input("Delay_leakage1_broken", "leakage1_broken", True)
    check_input("Delay_fan1_error", "fan1_error", True)
    check_input("Delay_fan2_error", "fan2_error", True)
    check_input("Delay_fan3_error", "fan3_error", True)
    check_input("Delay_fan4_error", "fan4_error", True)
    check_input("Delay_fan5_error", "fan5_error", True)
    check_input("Delay_fan6_error", "fan6_error", True)
    check_input("Delay_fan7_error", "fan7_error", True)
    check_input("Delay_fan8_error", "fan8_error", True)
    check_input("Delay_main_mc_error", "main_mc_error", False)
    check_input("Delay_Inv1_Error", "Inv1_Error", False)
    check_input("Delay_Inv2_Error", "Inv2_Error", False)
    check_input("Delay_Inv3_Error", "Inv3_Error", False)

    check_overload_error("Delay_Inv1_OverLoad")
    check_overload_error("Delay_Inv2_OverLoad")
    check_overload_error("Delay_Inv3_OverLoad")
    check_overload_error("Delay_Fan_OverLoad1")
    check_overload_error("Delay_Fan_OverLoad2")

    check_ATS("Delay_ATS")

    check_high_warning(
        "Thr_W_TempClntSply",
        "Thr_W_Rst_TempClntSply",
        "Delay_TempClntSply",
        "W",
    )

    check_high_warning(
        "Thr_A_TempClntSply",
        "Thr_A_Rst_TempClntSply",
        "Delay_TempClntSply",
        "A",
    )

    check_high_warning(
        "Thr_W_TempClntSplySpare",
        "Thr_W_Rst_TempClntSplySpare",
        "Delay_TempClntSplySpare",
        "W",
    )

    check_high_warning(
        "Thr_A_TempClntSplySpare",
        "Thr_A_Rst_TempClntSplySpare",
        "Delay_TempClntSplySpare",
        "A",
    )

    check_high_warning(
        "Thr_W_TempClntRtn",
        "Thr_W_Rst_TempClntRtn",
        "Delay_TempClntRtn",
        "W",
    )
    check_high_warning(
        "Thr_A_TempClntRtn",
        "Thr_A_Rst_TempClntRtn",
        "Delay_TempClntRtn",
        "A",
    )

    check_high_warning(
        "Thr_W_TempClntRtnSpare",
        "Thr_W_Rst_TempClntRtnSpare",
        "Delay_TempClntRtnSpare",
        "W",
    )
    check_high_warning(
        "Thr_A_TempClntRtnSpare",
        "Thr_A_Rst_TempClntRtnSpare",
        "Delay_TempClntRtnSpare",
        "A",
    )

    check_high_warning(
        "Thr_W_PrsrClntSply",
        "Thr_W_Rst_PrsrClntSply",
        "Delay_PrsrClntSply",
        "W",
    )

    check_high_warning(
        "Thr_A_PrsrClntSply",
        "Thr_A_Rst_PrsrClntSply",
        "Delay_PrsrClntSply",
        "A",
    )

    check_high_warning(
        "Thr_W_PrsrClntSplySpare",
        "Thr_W_Rst_PrsrClntSplySpare",
        "Delay_PrsrClntSplySpare",
        "W",
    )

    check_high_warning(
        "Thr_A_PrsrClntSplySpare",
        "Thr_A_Rst_PrsrClntSplySpare",
        "Delay_PrsrClntSplySpare",
        "A",
    )

    check_high_warning(
        "Thr_W_PrsrClntRtn",
        "Thr_W_Rst_PrsrClntRtn",
        "Delay_PrsrClntRtn",
        "W",
    )

    check_high_warning(
        "Thr_A_PrsrClntRtn",
        "Thr_A_Rst_PrsrClntRtn",
        "Delay_PrsrClntRtn",
        "A",
    )

    check_high_warning(
        "Thr_W_PrsrClntRtnSpare",
        "Thr_W_Rst_PrsrClntRtnSpare",
        "Delay_PrsrClntRtnSpare",
        "W",
    )

    check_high_warning(
        "Thr_A_PrsrClntRtnSpare",
        "Thr_A_Rst_PrsrClntRtnSpare",
        "Delay_PrsrClntRtnSpare",
        "A",
    )

    check_both_warning_p3(
        "Thr_W_PrsrFltIn_L",
        "Thr_W_PrsrFltIn_H",
        "Thr_W_Rst_PrsrFltIn_L",
        "Thr_W_Rst_PrsrFltIn_H",
        "Delay_PrsrFltIn",
        "W",
    )

    check_both_warning_p3(
        "Thr_A_PrsrFltIn_L",
        "Thr_A_PrsrFltIn_H",
        "Thr_A_Rst_PrsrFltIn_L",
        "Thr_A_Rst_PrsrFltIn_H",
        "Delay_PrsrFltIn",
        "A",
    )

    check_pressure_diff_error(
        "Thr_W_PrsrFltOut_H",
        "Thr_W_Rst_PrsrFltOut_H",
        "Delay_PrsrFltOut",
        "W",
    )

    check_pressure_diff_error(
        "Thr_A_PrsrFltOut_H",
        "Thr_A_Rst_PrsrFltOut_H",
        "Delay_PrsrFltOut",
        "A",
    )

    check_both_warning(
        "Thr_W_RelativeHumid_L",
        "Thr_W_RelativeHumid_H",
        "Thr_W_Rst_RelativeHumid_L",
        "Thr_W_Rst_RelativeHumid_H",
        "Delay_RelativeHumid",
        "W",
    )

    check_both_warning(
        "Thr_A_RelativeHumid_L",
        "Thr_A_RelativeHumid_H",
        "Thr_A_Rst_RelativeHumid_L",
        "Thr_A_Rst_RelativeHumid_H",
        "Delay_RelativeHumid",
        "A",
    )

    check_both_warning(
        "Thr_W_AmbientTemp_L",
        "Thr_W_AmbientTemp_H",
        "Thr_W_Rst_AmbientTemp_L",
        "Thr_W_Rst_AmbientTemp_H",
        "Delay_AmbientTemp",
        "W",
    )

    check_both_warning(
        "Thr_A_AmbientTemp_L",
        "Thr_A_AmbientTemp_H",
        "Thr_A_Rst_AmbientTemp_L",
        "Thr_A_Rst_AmbientTemp_H",
        "Delay_AmbientTemp",
        "A",
    )

    check_both_warning(
        "Thr_W_pH_L",
        "Thr_W_pH_H",
        "Thr_W_Rst_pH_L",
        "Thr_W_Rst_pH_H",
        "Delay_pH",
        "W",
    )

    check_both_warning(
        "Thr_A_pH_L",
        "Thr_A_pH_H",
        "Thr_A_Rst_pH_L",
        "Thr_A_Rst_pH_H",
        "Delay_pH",
        "A",
    )

    check_both_warning(
        "Thr_W_Cdct_L",
        "Thr_W_Cdct_H",
        "Thr_W_Rst_Cdct_L",
        "Thr_W_Rst_Cdct_H",
        "Delay_Cdct",
        "W",
    )

    check_both_warning(
        "Thr_A_Cdct_L",
        "Thr_A_Cdct_H",
        "Thr_A_Rst_Cdct_L",
        "Thr_A_Rst_Cdct_H",
        "Delay_Cdct",
        "A",
    )

    check_both_warning(
        "Thr_W_Tbt_L",
        "Thr_W_Tbt_H",
        "Thr_W_Rst_Tbt_L",
        "Thr_W_Rst_Tbt_H",
        "Delay_Tbt",
        "W",
    )

    check_both_warning(
        "Thr_A_Tbt_L",
        "Thr_A_Tbt_H",
        "Thr_A_Rst_Tbt_L",
        "Thr_A_Rst_Tbt_H",
        "Delay_Tbt",
        "A",
    )

    check_high_warning(
        "Thr_W_AC_H",
        "Thr_W_Rst_AC_H",
        "Delay_AC",
        "W",
    )

    check_high_warning(
        "Thr_A_AC_H",
        "Thr_A_Rst_AC_H",
        "Delay_AC",
        "A",
    )

    check_low_warning_f1(
        "Thr_W_ClntFlow",
        "Thr_W_Rst_ClntFlow",
        "Delay_ClntFlow",
        "W",
    )

    check_low_warning_f1(
        "Thr_A_ClntFlow",
        "Thr_A_Rst_ClntFlow",
        "Delay_ClntFlow",
        "A",
    )

    check_dewPt_warning(
        "Thr_W_DewPoint",
        "Thr_W_Rst_DewPoint",
        "Delay_DewPoint",
        "W",
    )

    check_dewPt_warning(
        "Thr_A_DewPoint",
        "Thr_A_Rst_DewPoint",
        "Delay_DewPoint",
        "A",
    )

    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            r = client.read_coils((8192 + 10), 2, unit=modbus_slave_id)
            ats_status["ATS1"] = r.bits[0]
            ats_status["ATS2"] = r.bits[1]
    except Exception as e:
        print(f"ATS issue:{e}")

    for i in range(1, 4):
        if not bit_output_regs[f"mc{i}"]:
            warning_data["error"][f"Inv{i}_Freq_communication"] = True

    warning_key = list(warning_data["warning"].keys())
    warning_key_len = len(warning_data["warning"].keys())
    warning_reg = (warning_key_len // 16) + (1 if warning_key_len % 16 != 0 else 0)
    value_w = [0] * warning_reg
    for i in range(0, warning_key_len):
        key = warning_key[i]
        # warning_data["warning"][key] = False
        # warning_data["warning"][key] = True
        # warning_data["warning"]["RelativeHumid_Low"] = False
        # journal_logger.info(f"[key]:{[key]}")
        # journal_logger.info(f"warning_data['warning'][key]:{warning_data['warning'][key]}")
        if warning_data["warning"][key]:
            value_w[i // 16] |= 1 << (i % 16)

    alert_key = list(warning_data["alert"].keys())
    alert_key_len = len(warning_data["alert"].keys())
    alert_reg = (alert_key_len // 16) + (1 if alert_key_len % 16 != 0 else 0)
    value_a = [0] * alert_reg
    for i in range(0, alert_key_len):
        key = alert_key[i]
        # warning_data["alert"][key] = False
        # warning_data["alert"][key] = True
        # warning_data["alert"]["pH_Low"] = False
        if warning_data["alert"][key]:
            value_a[i // 16] |= 1 << (i % 16)

    error_key = list(warning_data["error"].keys())
    err_key_len = len(warning_data["error"].keys())
    err_reg = (err_key_len // 16) + (1 if err_key_len % 16 != 0 else 0)
    value_e = [0] * err_reg
    for i in range(0, err_key_len):
        key = error_key[i]
        # warning_data["error"][key] = False
        # warning_data["error"][key] = True
        # warning_data["error"]["Temp_ClntSply_broken"] = False
        if warning_data["error"][key]:
            value_e[i // 16] |= 1 << (i % 16)

    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_registers(1700, value_w)
            client.write_registers(1705, value_a)
            client.write_registers(1708, value_e)
    except Exception as e:
        print(f"store in 16 bits error{e}")

    ignore_key = ["ATS1_Error"]

    sensor_key_map = {
        "Temp_ClntSplySpare": ["Temp_ClntSplySpare_broken", "TempClntSplySpare_High"],
        "Temp_ClntRtnSpare": ["Temp_ClntRtnSpare_broken", "TempClntRtnSpare_High"],
        "Prsr_ClntSplySpare": ["PrsrClntSplySpare_High", "PrsrClntSplySpare_High"],
        "Prsr_ClntRtnSpare": ["PrsrClntRtnSpare_High", "PrsrClntRtnSpare_High"],
    }

    for sensor, keys in sensor_key_map.items():
        if sensor_factor.get(sensor) == 0:
            ignore_key.extend(keys)

    if ver_switch["flow_switch"]:
        ignore_key.append("Clnt_Flow_broken")
    else:
        ignore_key.append("coolant_flow_rate_communication")

    if (
        not any(
            value
            for key, value in warning_data["alert"].items()
            if key not in ignore_key
        )
        and not any(
            value
            for key, value in warning_data["error"].items()
            if key not in ignore_key
        )
        and not any(
            value
            for key, value in warning_data["warning"].items()
            if key not in ignore_key
        )
    ):
        color_light["green"] = True
        color_light["red"] = False
    elif any(
        value for key, value in warning_data["alert"].items() if key not in ignore_key
    ) or any(
        value for key, value in warning_data["error"].items() if key not in ignore_key
    ):
        color_light["green"] = False
        color_light["red"] = True
    elif (
        any(
            value
            for key, value in warning_data["warning"].items()
            if key not in ignore_key
        )
        and not any(
            value
            for key, value in warning_data["alert"].items()
            if key not in ignore_key
        )
        and not any(
            value
            for key, value in warning_data["error"].items()
            if key not in ignore_key
        )
    ):
        color_light["green"] = True
        color_light["red"] = True

    if onLinux:
        try:
            if mode == "inspection":
                bit_output_regs["led_err"] = False
            elif (
                any(
                    value
                    for key, value in warning_data["warning"].items()
                    if key not in ignore_key
                )
                or any(
                    value
                    for key, value in warning_data["alert"].items()
                    if key not in ignore_key
                )
                or any(
                    value
                    for key, value in warning_data["error"].items()
                    if key not in ignore_key
                )
            ):
                bit_output_regs["led_err"] = warning_light
                warning_light = not warning_light
            else:
                bit_output_regs["led_err"] = False
        except Exception as e:
            print(f"warning light error:{e}")


def translate_pump_speed(speed):
    if speed == 0:
        return 0

    ps = (float(speed) - 25) / 75.0 * 16000.0
    ps = int(ps)
    return ps


def translate_fan_speed(speed):
    fan = (float(speed)) / 100.0 * 16000.0
    fan = int(fan)
    return fan


def set_pump1_speed(speed):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 6660), speed)

    except Exception as e:
        print(f"set pump1 speed error: {e}")


def set_pump2_speed(speed):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 6700), speed)

    except Exception as e:
        print(f"set pump2 speed error: {e}")


def set_pump3_speed(speed):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 6740), speed)

    except Exception as e:
        print(f"set pump3 speed error: {e}")


def set_f1(speed):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 7020), speed)
    except Exception as e:
        print(f"set f1 speed error: {e}")


def set_f2(speed):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 7060), speed)
    except Exception as e:
        print(f"set f2 speed error: {e}")


def set_f3(speed):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 7100), speed)
    except Exception as e:
        print(f"set f3 speed error: {e}")


def set_f4(speed):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 7140), speed)
    except Exception as e:
        print(f"set f4 speed error: {e}")


def set_f5(speed):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 7380), speed)
    except Exception as e:
        print(f"set fan set1 speed error: {e}")


def set_f6(speed):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 7420), speed)
    except Exception as e:
        print(f"set fan set2 speed error: {e}")


def set_f7(speed):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 7460), speed)
    except Exception as e:
        print(f"set fan set3 speed error: {e}")


def set_f8(speed):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 7500), speed)
    except Exception as e:
        print(f"set fan set4 speed error: {e}")


def trigger_overload_from_oc_detection():
    if oc_detection["p1"]:
        overload_error["Inv1_OverLoad"] = True

    if oc_detection["p2"]:
        overload_error["Inv2_OverLoad"] = True

    if oc_detection["p3"]:
        overload_error["Inv3_OverLoad"] = True

    if oc_detection["f1"]:
        overload_error["Fan_OverLoad1"] = True

    if oc_detection["f2"]:
        overload_error["Fan_OverLoad2"] = True


def check_mc():
    if not overload_error["Inv1_OverLoad"] or not bit_input_regs["Inv1_Error"]:
        bit_output_regs["mc1"] = True
    else:
        bit_output_regs["mc1"] = False

    if not overload_error["Inv2_OverLoad"] or not bit_input_regs["Inv2_Error"]:
        bit_output_regs["mc2"] = True
    else:
        bit_output_regs["mc2"] = False

    if not overload_error["Inv3_OverLoad"] or not bit_input_regs["Inv3_Error"]:
        bit_output_regs["mc3"] = True
    else:
        bit_output_regs["mc3"] = False

    if not overload_error["Fan_OverLoad1"]:
        bit_output_regs["mc_fan1"] = True
    else:
        bit_output_regs["mc_fan1"] = False

    if not overload_error["Fan_OverLoad2"]:
        bit_output_regs["mc_fan2"] = True
    else:
        bit_output_regs["mc_fan2"] = False


def uint16_to_int16(value):
    if value >= 32768:
        return value - 65536
    return value


def reset_mc():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_coils(800, [False])
    except Exception as e:
        print(f"reset mc error:{e}")
    overload_error["Inv1_OverLoad"] = False
    overload_error["Inv2_OverLoad"] = False


def open_inv1_auto():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_coils((8192 + 870), [True])
    
    except Exception as e:
        print(f"open inv1: {e}")
    set_pump1_speed(word_regs["pid_pump_out"])



def open_inv2_auto():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_coils((8192 + 871), [True])
    
    except Exception as e:
        print(f"open inv1: {e}")
    set_pump2_speed(word_regs["pid_pump_out"])


def open_inv3_auto():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_coils((8192 + 872), [True])
    
    except Exception as e:
        print(f"open inv1: {e}")
    set_pump3_speed(word_regs["pid_pump_out"])


def close_inv1_auto():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_coils((8192 + 870), [False])
    
    except Exception as e:
        print(f"close inv1: {e}")
    set_pump1_speed(word_regs["pid_pump_out"])



def close_inv2_auto():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_coils((8192 + 871), [False])
    
    except Exception as e:
        print(f"close inv1: {e}")
    set_pump2_speed(word_regs["pid_pump_out"])


def close_inv3_auto():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_coils((8192 + 872), [False])
    
    except Exception as e:
        print(f"close inv1: {e}")
    set_pump3_speed(word_regs["pid_pump_out"])


def reset_btn_false():
    reset_current_btn["status"] = False
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_coils((8192 + 800), [False])
    except Exception as e:
        print(f"reset btn error:{e}")


def clear_p1_speed():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_coils((8192 + 820), [False])
            client.write_register((20480 + 6660), 0)
    except Exception as e:
        print(f"clear p1 speed error:{e}")


def clear_p2_speed():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_coils((8192 + 821), [False])
            client.write_register((20480 + 6700), 0)

    except Exception as e:
        print(f"clear p2 speed error:{e}")


def clear_p3_speed():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_coils((8192 + 822), [False])
            client.write_register((20480 + 6740), 0)

    except Exception as e:
        print(f"clear p3 speed error:{e}")


def clear_f1_speed():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 7020), 0)
            client.write_register((20480 + 7060), 0)
            client.write_register((20480 + 7100), 0)
            client.write_register((20480 + 7140), 0)
    except Exception as e:
        print(f"clear f1 speed error:{e}")


def clear_f2_speed():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 7380), 0)
            client.write_register((20480 + 7420), 0)
            client.write_register((20480 + 7460), 0)
            client.write_register((20480 + 7500), 0)
    except Exception as e:
        print(f"clear f1 speed error:{e}")


def stop_fan():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 7020), 0)
            client.write_register((20480 + 7060), 0)
            client.write_register((20480 + 7100), 0)
            client.write_register((20480 + 7140), 0)
            client.write_register((20480 + 7380), 0)
            client.write_register((20480 + 7420), 0)
            client.write_register((20480 + 7460), 0)
            client.write_register((20480 + 7500), 0)
    except Exception as e:
        print(f"clear fan error:{e}")


def stop_p1():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 6660), 0)
    except Exception as e:
        print(f"clear all speed error:{e}")


def stop_p2():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 6700), 0)
    except Exception as e:
        print(f"clear all speed error:{e}")


def stop_p3():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register((20480 + 6740), 0)
    except Exception as e:
        print(f"clear all speed error:{e}")


def get_key(item):
    return item[1]


def write_measured_data(number, data):
    registers = []

    word1, word2 = cvt_float_byte(data)
    registers.append(word2)
    registers.append(word1)

    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_registers((900 + number), registers)
    except Exception as e:
        print(f"send messure p1:{e}")


def cancel_inspection():
    try:
        value_list_status = list(inspection_data["prog"].values())
        value_list_status = [1 if value == 4 else value for value in value_list_status]
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_registers(800, value_list_status)
    except Exception as e:
        print(f"result write-in:{e}")

    for key, status in inspection_data["prog"].items():
        if status == 1:
            inspection_data["result"][key] = False

    try:
        value_list_result = [
            1 if value else 0 for value in inspection_data["result"].values()
        ]
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_registers(750, value_list_result)
            client.write_register(973, 2)
    except Exception as e:
        print(f"result write-in:{e}")

    inspection_data["step"] = 1
    inspection_data["start_time"] = 0
    inspection_data["mid_time"] = 0
    inspection_data["end_time"] = 0

    print("被切掉模式")


def check_last_mode_from_inspection(mode_last):
    one_time = True
    if mode_last == "inspection":
        if one_time:
            try:
                with ModbusTcpClient(
                    host=modbus_host, port=modbus_port, unit=modbus_slave_id
                ) as client:
                    r = client.read_coils((8192 + 600), 1, unit=modbus_slave_id)
                    inspection_data["force_change_mode"] = r.bits[0]
            except Exception as e:
                print(f"read force change mode error:{e}")
            one_time = False
    else:
        inspection_data["force_change_mode"] = False


def check_inv_speed():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            inv1 = client.read_holding_registers(address=(20480 + 6660), count=1)
            inv2 = client.read_holding_registers(address=(20480 + 6700), count=1)
            inv3 = client.read_holding_registers(address=(20480 + 6740), count=1)

            inv1_v = inv1.registers[0] / 16000 * 75 + 25
            inv2_v = inv2.registers[0] / 16000 * 75 + 25
            inv3_v = inv3.registers[0] / 16000 * 75 + 25

            return inv1_v, inv2_v, inv3_v
    except Exception as e:
        print(f"read inv_en error:{e}")


def go_back_to_last_mode(mode):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register(950, 1)

            p1 = translate_pump_speed(inspection_data["prev"]["inv1"])
            p2 = translate_pump_speed(inspection_data["prev"]["inv2"])
            p3 = translate_pump_speed(inspection_data["prev"]["inv3"])

            p1 = p1 if inspection_data["prev"]["inv1"] != 0 else 0
            p2 = p2 if inspection_data["prev"]["inv2"] != 0 else 0
            p3 = p3 if inspection_data["prev"]["inv3"] != 0 else 0

            set_pump1_speed(p1)
            set_pump2_speed(p2)
            set_pump3_speed(p3)

            if mode == "manual":
                client.write_coils((8192 + 517), [False])
                client.write_coils((8192 + 505), [True])
            elif mode == "engineer":
                client.write_coils((8192 + 517), [False])
                client.write_coils((8192 + 516), [True])
            elif mode == "auto":
                client.write_coils((8192 + 517), [False])
                client.write_coils((8192 + 505), [False])
            elif mode == "stop":
                client.write_coils((8192 + 517), [False])
                client.write_coils((8192 + 514), [False])
            else:
                client.write_coils((8192 + 517), [False])
                client.write_coils((8192 + 505), [True])
    except Exception as e:
        print(f"respec error:{e}")


def reset_inspect_btn():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register(900, 3)
            inspection_data["start_btn"] = 3
    except Exception as e:
        print(f"close inspection:{e}")


def only_send_inspection_data(number, progress_value):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_registers((800 + number), progress_value)
    except Exception as e:
        print(f"result write-in:{e}")


def send_inspection_data(number, progress_value, result_value):
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_registers((800 + number), progress_value)
    except Exception as e:
        print(f"result write-in:{e}")

    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            change_result_value = [1 if result_value else 0]
            client.write_registers((750 + number), change_result_value)
    except Exception as e:
        print(f"result write-in:{e}")


def change_inspect_time():
    try:
        with ModbusTcpClient(
            host=modbus_host, port=modbus_port, unit=modbus_slave_id
        ) as client:
            client.write_register(950, 2)

    except Exception as e:
        print(f"change_inspect_time:{e}")

def call(message):
    journal_logger.info(f"測試：{message}")

def control():
    global check_server2, server2_occur_stop, pre_check_server2

    mode_last = ""
    pump1_run_last_min = time.time()
    pump2_run_last_min = time.time()
    pump3_run_last_min = time.time()
    swap_last = time.time()
    first_p = False
    mode = ""
    global \
        previous_inv, \
        previous_inv1, \
        previous_inv2, \
        change_back_mode, \
        oc_issue, \
        diff, \
        f1_data, \
        pump_signial, \
        water_pv_set
    global auto_flag, port
    global \
        count_f1, \
        p1_data, \
        p2_data, \
        p3_data, \
        zero_flag, \
        rtu_flag, \
        previous_ver, \
        oc_trigger, \
        p1_error_box, \
        p2_error_box, \
        p3_error_box
    clnt_flow_data = deque(maxlen=20)

    while True:
        try:
            restart_server["start"] = time.time()
            server_error["start"] = time.time()
            try:
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    value_list = [v for key, v in raw_485_data.items() if key != "ATS1" and key != "ATS2"]
                    new_list = []

                    for value in value_list:
                        r1, r2 = cvt_float_byte(value)
                        new_list.append(r2)
                        new_list.append(r1)
                    client.write_registers(11, new_list)
            except Exception as e:
                print(f"485 data error:{e}")

            try:
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    client.write_coil((8192 + 10), raw_485_data["ATS1"])
                    client.write_coil((8192 + 11), raw_485_data["ATS2"])
            except Exception as e:
                print(f"485 ATS 1&2 error:{e}")

            try:
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    r = client.read_coils((8192 + 800), 4)
                    reset_current_btn["status"] = r.bits[0]
                    ver_switch["flow_switch"] = r.bits[2]
                    ver_switch["median_switch"] = r.bits[3]

                    r2 = client.read_holding_registers(900, 1)
                    inspection_data["start_btn"] = r2.registers[0]
            except Exception as e:
                print(f"check version: {e}")

            try:
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    leak = client.read_discrete_inputs(2, 2, unit=modbus_slave_id)
                    bit_input_regs["leakage1_leak"] = leak.bits[0]
                    bit_input_regs["leakage1_broken"] = leak.bits[1]

                    mainMC = client.read_discrete_inputs(35, 1, unit=modbus_slave_id)
                    bit_input_regs["main_mc_error"] = mainMC.bits[0]

                    full_input = client.read_discrete_inputs(
                        40, 8, unit=modbus_slave_id
                    )
                    for i in range(8):
                        key_list = list(bit_input_regs.keys())
                        bit_input_regs[key_list[i + 6]] = full_input.bits[i]

                    inv_error = client.read_discrete_inputs(0, 2, unit=modbus_slave_id)
                    bit_input_regs["Inv1_Error"] = inv_error.bits[0]
                    bit_input_regs["Inv2_Error"] = inv_error.bits[1]

                    inv_error_3 = client.read_discrete_inputs(
                        26, 1, unit=modbus_slave_id
                    )
                    bit_input_regs["Inv3_Error"] = inv_error_3.bits[0]

                    level = client.read_discrete_inputs(12, 4)
                    level_sw["level1"] = level.bits[0]
                    level_sw["level2"] = level.bits[1]
                    level_sw["power24v1"] = level.bits[2]
                    level_sw["power24v2"] = level.bits[3]

                    level2 = client.read_discrete_inputs(18, 3)
                    level_sw["level3"] = level2.bits[0]
                    level_sw["power12v1"] = level2.bits[1]
                    level_sw["power12v2"] = level2.bits[2]

                    oc = client.read_discrete_inputs(16, 2)
                    oc_detection["p1"] = oc.bits[0]
                    oc_detection["p2"] = oc.bits[1]

                    oc2 = client.read_discrete_inputs(32, 3)
                    oc_detection["p3"] = oc2.bits[0]
                    oc_detection["f1"] = oc2.bits[1]
                    oc_detection["f2"] = oc2.bits[2]

            except Exception as e:
                print(f"read leak error {e}")

            check_mc()

            try:
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    mc = client.read_coils((8192 + 840), 5, unit=modbus_slave_id)
                    bit_output_regs["mc1"] = mc.bits[0]
                    bit_output_regs["mc2"] = mc.bits[1]
                    bit_output_regs["mc3"] = mc.bits[2]
                    bit_output_regs["mc_fan1"] = mc.bits[3]
                    bit_output_regs["mc_fan2"] = mc.bits[4]
            except Exception as e:
                print(f"output read: {e}")

            try:
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    word = client.read_holding_registers(246, 2, unit=modbus_slave_id)
                    word_regs["pump_speed"] = cvt_registers_to_float(
                        word.registers[0], word.registers[1]
                    )

                    word2 = client.read_holding_registers(470, 2, unit=modbus_slave_id)
                    word_regs['fan_speed'] = cvt_registers_to_float(
                        word2.registers[0], word2.registers[1]
                    )
                    # journal_logger.info(f"word_regs['fan_speed']:{word_regs['fan_speed']}")

                    word1 = client.read_coils((8192 + 820), 3, unit=modbus_slave_id)
                    word_regs["p1_check"] = word1.bits[0]
                    word_regs["p2_check"] = word1.bits[1]
                    word_regs["p3_check"] = word1.bits[2]

                    word2 = client.read_coils((8192 + 850), 8, unit=modbus_slave_id)
                    word_regs["f1_check"] = word2.bits[0]
                    word_regs["f2_check"] = word2.bits[1]
                    word_regs["f3_check"] = word2.bits[2]
                    word_regs["f4_check"] = word2.bits[3]
                    word_regs["f5_check"] = word2.bits[4]
                    word_regs["f6_check"] = word2.bits[5]
                    word_regs["f7_check"] = word2.bits[6]
                    word_regs["f8_check"] = word2.bits[7]

                    word3 = client.read_holding_registers(50, 1, unit=modbus_slave_id)
                    word_regs["pid_pump_out"] = word3.registers[0]
            except Exception as e:
                print(f"read mc error: {e}")

            try:
                with ModbusTcpClient(
                    host=modbus_host, port=modbus_port, unit=modbus_slave_id
                ) as client:
                    inv1 = client.read_holding_registers(
                        address=(20480 + 6660), count=1
                    )
                    inv2 = client.read_holding_registers(
                        address=(20480 + 6700), count=1
                    )
                    inv3 = client.read_holding_registers(
                        address=(20480 + 6740), count=1
                    )

                    inv1_v = inv1.registers[0] / 16000 * 75 + 25
                    inv2_v = inv2.registers[0] / 16000 * 75 + 25
                    inv3_v = inv3.registers[0] / 16000 * 75 + 25

                    if not bit_output_regs["mc1"] or not word_regs["p1_check"]:
                        inv1_v = 0

                    if not bit_output_regs["mc2"] or not word_regs["p2_check"]:
                        inv2_v = 0

                    if not bit_output_regs["mc3"] or not word_regs["p3_check"]:
                        inv3_v = 0

                    inv["inv1"] = inv1_v >= 25
                    inv["inv2"] = inv2_v >= 25
                    inv["inv3"] = inv3_v >= 25
            except Exception as e:
                print(f"read inv_en 2 error:{e}")

            try:
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    time1 = client.read_holding_registers(270, 4, unit=modbus_slave_id)
                    dword_regs["p1_run_min"] = read_split_register(time1.registers, 0)
                    dword_regs["p1_run_hr"] = read_split_register(time1.registers, 2)

                    time2 = client.read_holding_registers(274, 4, unit=modbus_slave_id)
                    dword_regs["p2_run_min"] = read_split_register(time2.registers, 0)
                    dword_regs["p2_run_hr"] = read_split_register(time2.registers, 2)

                    time3 = client.read_holding_registers(278, 4, unit=modbus_slave_id)
                    dword_regs["p3_run_min"] = read_split_register(time3.registers, 0)
                    dword_regs["p3_run_hr"] = read_split_register(time3.registers, 2)

                    p_swap = client.read_holding_registers(303, 2, unit=modbus_slave_id)
                    swap = cvt_registers_to_float(
                        p_swap.registers[0], p_swap.registers[1]
                    )
                    dword_regs["p_swap"] = swap
            except Exception as e:
                print(f"read pump1 runtime error: {e}")

            try:
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    result = client.read_coils((8192 + 514), 1)

                    if not result.bits[0]:
                        mode = "stop"
                    else:
                        result = client.read_coils((8192 + 516), 1)

                        if result.bits[0]:
                            mode = "engineer"
                        else:
                            r = client.read_coils((8192 + 517), 1)

                            if r.bits[0]:
                                mode = "inspection"
                            else:
                                result = client.read_coils((8192 + 505), 1)

                                if result.isError():
                                    print(f"Modbus Error: {result}")
                                else:
                                    if not result.bits[0]:
                                        mode = "auto"
                                    else:
                                        mode = "manual"
            except Exception as e:
                print(f"read mode & control data: {e}")

            try:
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    ad_count = len(ad_sensor_value.keys())
                    serial_count = len(serial_sensor_value.keys()) - 1
                    all_count = ad_count + (serial_count * 2)

                    all_sensors = client.read_holding_registers(
                        0, all_count, unit=modbus_slave_id
                    )

                    keys_list = list(ad_sensor_value.keys())
                    for i in range(ad_count):
                        value = all_sensors.registers[i]
                        value_translate = uint16_to_int16(value)
                        sensor_raw[keys_list[i]] = value_translate

                    key_list = list(sensor_raw.keys())

                    for key in key_list:
                        if ("Temp" in key or "Prsr" in key) and key != "AmbientTemp":
                            check_broken(key)

                    for key in key_list:
                        if "Prsr" in key:
                            if 6400 > sensor_raw[key] > 6080:
                                sensor_raw[key] = 6400

                    ad_sensor_value["Temp_ClntSply"] = (
                        float(sensor_raw["Temp_ClntSply"]) / 10.0
                    )
                    ad_sensor_value["Temp_ClntSplySpare"] = (
                        float(sensor_raw["Temp_ClntSplySpare"]) / 10.0
                    )
                    ad_sensor_value["Temp_ClntRtn"] = (
                        float(sensor_raw["Temp_ClntRtn"]) / 10.0
                    )
                    ad_sensor_value["Temp_ClntRtnSpare"] = (
                        float(sensor_raw["Temp_ClntRtnSpare"]) / 10.0
                    )
                    ad_sensor_value["Prsr_ClntSply"] = (
                        float(sensor_raw["Prsr_ClntSply"]) - 6400
                    ) / 25600
                    ad_sensor_value["Prsr_ClntSplySpare"] = (
                        float(sensor_raw["Prsr_ClntSplySpare"]) - 6400
                    ) / 25600
                    ad_sensor_value["Prsr_ClntRtn"] = (
                        float(sensor_raw["Prsr_ClntRtn"] - 6400)
                    ) / 25600.0
                    ad_sensor_value["Prsr_ClntRtnSpare"] = (
                        float(sensor_raw["Prsr_ClntRtnSpare"] - 6400)
                    ) / 25600.0

                    ad_sensor_value["Prsr_FltIn"] = (
                        float(sensor_raw["Prsr_FltIn"]) - 6400
                    ) / 25600.0
                    ad_sensor_value["Prsr_FltOut"] = (
                        float(sensor_raw["Prsr_FltOut"]) - 6400
                    ) / 25600.0

                    keys_list = list(serial_sensor_value.keys())

                    for k, v in mapping.items():
                        if k in raw_485_data:
                            serial_sensor_value[v] = raw_485_data[k]

                    # j = 0
                    # for i in range(ad_count, all_count, 2):
                    #     temp1 = [all_sensors.registers[i], all_sensors.registers[i + 1]]
                    #     decoder_big_endian = BinaryPayloadDecoder.fromRegisters(
                    #         temp1, byteorder=Endian.Big, wordorder=Endian.Little
                    #     )
                    #     try:
                    #         decoded_value = decoder_big_endian.decode_32bit_float()
                    #         if decoded_value != decoded_value:
                    #             print(f"key {keys_list[j]} results NaN")
                    #         else:
                    #             serial_sensor_value[keys_list[j]] = decoded_value
                    #     except Exception as e:
                    #         print(f"{keys_list[j]} value error：{e}")
                    #     j += 1

                    if not ver_switch["flow_switch"]:
                        try:
                            f1 = client.read_holding_registers((20480 + 6380), 1)

                            if not f1.isError():
                                serial_sensor_value["Clnt_Flow"] = f1.registers[0]
                                if serial_sensor_value["Clnt_Flow"] > 32767:
                                    serial_sensor_value["Clnt_Flow"] = (
                                        65535 - serial_sensor_value["Clnt_Flow"]
                                    )
                                if 3200 > serial_sensor_value["Clnt_Flow"] > 3040:
                                    serial_sensor_value["Clnt_Flow"] = 3200
                                sensor_raw["Clnt_Flow"] = serial_sensor_value[
                                    "Clnt_Flow"
                                ]
                                check_broken("Clnt_Flow")
                                serial_sensor_value["Clnt_Flow"] = (
                                    (serial_sensor_value["Clnt_Flow"] - 3200)
                                    / 12800
                                    * 1650
                                )
                            else:
                                print("f1 error")

                        except Exception as e:
                            print(f"check version f1: {e}")
            except Exception as e:
                journal_logger.info(f"ad and serial value error: {e}")

            try:
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    adjust_len = (
                        len(sensor_factor.keys()) + len(sensor_offset.keys())
                    ) * 2
                    sensor_adjs = client.read_holding_registers(
                        1400, adjust_len, unit=modbus_slave_id
                    )

                    if sensor_adjs.isError():
                        print(f"Modbus Error: {sensor_adjs}")
                    else:
                        keys_list = list(sensor_factor.keys())

                        for i in range(0, adjust_len, 4):
                            temp1 = [
                                sensor_adjs.registers[i],
                                sensor_adjs.registers[i + 1],
                            ]
                            decoder_big_endian = BinaryPayloadDecoder.fromRegisters(
                                temp1, byteorder=Endian.Big, wordorder=Endian.Little
                            )
                            decoded_value_big_endian = (
                                decoder_big_endian.decode_32bit_float()
                            )
                            sensor_factor[keys_list[i // 4]] = decoded_value_big_endian

                        for i in range(2, adjust_len, 4):
                            temp1 = [
                                sensor_adjs.registers[i],
                                sensor_adjs.registers[i + 1],
                            ]
                            decoder_big_endian = BinaryPayloadDecoder.fromRegisters(
                                temp1, byteorder=Endian.Big, wordorder=Endian.Little
                            )
                            decoded_value_big_endian = (
                                decoder_big_endian.decode_32bit_float()
                            )
                            sensor_offset[keys_list[i // 4]] = decoded_value_big_endian
                


                    for key in ad_sensor_value.keys():
                        if key != "space":
                            all_sensors_dict[key] = (
                                ad_sensor_value[key] * sensor_factor[key]
                                + sensor_offset[key]
                            )
                    if not ver_switch["median_switch"]:
                        clnt_flow_data.append(serial_sensor_value["Clnt_Flow"])
                        if len(clnt_flow_data) > 20:
                            clnt_flow_data.popleft()
                        clnt_median = statistics.median(clnt_flow_data)
                        serial_sensor_value["Clnt_Flow"] = clnt_median

                    exclude_this_key = [
                        "Inv1_Freq",
                        "Inv2_Freq",
                        "Inv3_Freq",
                        "fan_freq1",
                        "fan_freq2",
                        "fan_freq3",
                        "fan_freq4",
                        "fan_freq5",
                        "fan_freq6",
                        "fan_freq7",
                        "fan_freq8",
                    ]
                    for key in serial_sensor_value.keys():
                        if key not in exclude_this_key:
                            all_sensors_dict[key] = (
                                serial_sensor_value[key] * sensor_factor[key]
                                + sensor_offset[key]
                            )
                            # journal_logger.info(f"[key]{[key]} ")
                            
                            # journal_logger.info(f"all_sensors_dict[key]{all_sensors_dict[key]} ")
                    
                    for i in range(1, 4):
                        key = f"Inv{i}_Freq"
                        all_sensors_dict[key] = (
                            0.1664 * serial_sensor_value[key] + 0.0818
                        )
                        # journal_logger.info(f"all_sensors_dict[key]{all_sensors_dict[key]}")

                        if not bit_output_regs[f"mc{i}"]:
                            all_sensors_dict[key] = 0

                    r = (
                        all_sensors_dict["Clnt_Flow"]
                        * 1.667
                        / 100
                        * 4.18
                        * (
                            all_sensors_dict["Temp_ClntSply"]
                            - all_sensors_dict["Temp_ClntRtn"]
                        )
                    )

                    all_sensors_dict["Heat_Capacity"] = (
                        r * sensor_factor["Heat_Capacity"]
                        + sensor_offset["Heat_Capacity"]
                    )

            except Exception as e:
                print(f"translate adjust raw data error: {e}")

            try:
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    r = client.read_coils((8192 + 500), 1)

                    if r.bits[0]:
                        key_list = list(all_sensors_dict.keys())
                        for key in key_list:
                            if "Temp" in key or "DewPoint" in key:
                                all_sensors_dict[key] = (
                                    all_sensors_dict[key] * 9.0 / 5.0 + 32.0
                                )

                            if "Prsr" in key:
                                all_sensors_dict[key] = all_sensors_dict[key] * 0.145038

                            if "Flow" in key:
                                all_sensors_dict[key] = all_sensors_dict[key] * 0.2642
            except Exception as e:
                print(f"change to imperial error: {e}")
            registers = []
            for key in all_sensors_dict.keys():
                value = all_sensors_dict[key]

                word1, word2 = cvt_float_byte(value)
                registers.append(word2)
                registers.append(word1)

            try:
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    client.write_registers(5000, registers)
            except Exception as e:
                print(f"write into thrshd error: {e}")

            trigger_overload_from_oc_detection()

            if mode in ["auto", "stop"]:
                if (
                    warning_data["alert"]["ClntFlow_Low"]
                    and warning_data["error"]["level1"]
                    and warning_data["error"]["level2"]
                    and warning_data["error"]["level3"]
                ):
                    try:
                        with ModbusTcpClient(
                            host=modbus_host, port=modbus_port
                        ) as client:
                            warning_data["error"]["Low_Coolant_Level_Warning"] = True
                            client.write_coils((8192 + 514), [False])
                    except Exception as e:
                        print(f"change to stop error:{e}")
                elif warning_data["error"]["Low_Coolant_Level_Warning"]:
                    if count_f1 > 5:
                        warning_data["error"]["Low_Coolant_Level_Warning"] = False
                        count_f1 = 0
                    else:
                        count_f1 += 1

            if reset_current_btn["status"]:
                overload_error["Inv1_OverLoad"] = False
                overload_error["Inv2_OverLoad"] = False
                overload_error["Inv3_OverLoad"] = False
                overload_error["Fan_OverLoad1"] = False
                overload_error["Fan_OverLoad2"] = False
                reset_btn_false()

            oc_list = list(oc_detection.values())

            # if any(oc_list):
            #     oc_issue = True
            #     if oc_detection["p1"]:
            #         bit_output_regs["mc1"] = False
            #         clear_p1_speed()

            #     if oc_detection["p2"]:
            #         bit_output_regs["mc2"] = False
            #         clear_p2_speed()

            #     if oc_detection["p3"]:
            #         bit_output_regs["mc3"] = False
            #         clear_p3_speed()

            #     if oc_detection["f1"]:
            #         bit_output_regs["mc_fan1"] = False
            #         clear_f1_speed()

            #     if oc_detection["f2"]:
            #         bit_output_regs["mc_fan2"] = False
            #         clear_f2_speed()

            # elif not any(oc_list) and oc_issue:
            #     ol_list = list(overload_error.values())
            #     if not any(ol_list):
            #         reset_mc()
            #         oc_issue = False
            #     else:
            #         if oc_detection["p1"]:
            #             bit_output_regs["mc1"] = False
            #             clear_p1_speed()

            #         if oc_detection["p2"]:
            #             bit_output_regs["mc2"] = False
            #             clear_p2_speed()

            #         if oc_detection["p3"]:
            #             bit_output_regs["mc3"] = False
            #             clear_p3_speed()

            #         if oc_detection["f1"]:
            #             bit_output_regs["mc_fan1"] = False
            #             clear_f1_speed()

            #         if oc_detection["f2"]:
            #             bit_output_regs["mc_fan2"] = False
            #             clear_f2_speed()
            # else:
            #     oc_issue = False

            if mode == "manual":
                check_last_mode_from_inspection(mode_last)
                if inspection_data["force_change_mode"]:
                    cancel_inspection()
                reset_inspect_btn()
                change_inspect_time()
                diff = 0
                inspection_data["step"] = 1
                flag1 = False
                flag2 = False
                flag3 = False
                flag4 = False
                flag5 = False
                # journal_logger.info(f'overload_error["Inv1_OverLoad"]:{overload_error["Inv1_OverLoad"]}')
                # journal_logger.info(f'flag1:{flag1}')
                
                # if overload_error["Inv1_OverLoad"]:
                #     clear_p1_speed()
                #     flag1 = True

                # if overload_error["Inv2_OverLoad"]:
                #     clear_p2_speed()
                #     flag2 = True

                # if overload_error["Inv3_OverLoad"]:
                #     clear_p3_speed()
                #     flag3 = True

                # if overload_error["Fan_OverLoad1"]:
                #     clear_f1_speed()
                #     flag4 = True

                # if overload_error["Fan_OverLoad2"]:
                #     clear_f2_speed()
                #     flag5 = True

                if not flag1:
                    journal_logger.info(f'word_regs["p1_check"]{word_regs["p1_check"]}')
                    if word_regs["p1_check"]:
                        ps = translate_pump_speed(word_regs["pump_speed"])
                        set_pump1_speed(ps)
                        journal_logger.info(f"ps1{ps}")
                        
                    else:
                        set_pump1_speed(0)
                        journal_logger.info(f"set_pump1_speed:0")
                        
                        

                if not flag2:
                    if word_regs["p2_check"]:
                        ps = translate_pump_speed(word_regs["pump_speed"])
                        journal_logger.info(f"ps2{ps}")
                        
                        set_pump2_speed(ps)
                    else:
                        set_pump2_speed(0)

                if not flag3:
                    if word_regs["p3_check"]:
                        ps = translate_pump_speed(word_regs["pump_speed"])
                        journal_logger.info(f"ps3{ps}")
                        set_pump3_speed(ps)
                    else:
                        set_pump3_speed(0)

                if not flag4:
                    if word_regs["fan_speed"] > 0:
                        fs = translate_fan_speed(word_regs["fan_speed"])
                        set_f1(fs if word_regs["f1_check"] else 0)
                        set_f2(fs if word_regs["f2_check"] else 0)
                        set_f3(fs if word_regs["f3_check"] else 0)
                        set_f4(fs if word_regs["f4_check"] else 0)
                        
                    else:
                        set_f1(0)
                        set_f2(0)
                        set_f3(0)
                        set_f4(0)

                if not flag5:
                    if word_regs["fan_speed"] > 0:
                        fs = translate_fan_speed(word_regs["fan_speed"])
                        set_f5(fs if word_regs["f5_check"] else 0)
                        set_f6(fs if word_regs["f6_check"] else 0)
                        set_f7(fs if word_regs["f7_check"] else 0)
                        set_f8(fs if word_regs["f8_check"] else 0)
                    else:
                        set_f5(0)
                        set_f6(0)
                        set_f7(0)
                        set_f8(0)

                mode_last = mode
                change_back_mode = mode
            elif mode == "auto":
                check_last_mode_from_inspection(mode_last)
                if inspection_data["force_change_mode"]:
                    cancel_inspection()
                diff = 0
                change_inspect_time()
                reset_inspect_btn()
                inspection_data["step"] = 1
                swap_current = time.time()
                time_rank = []
                inv_to_run = []

                if not first_p:
                    for i in range(1, 4):
                        p_run_min = dword_regs[f"p{i}_run_min"]
                        p_run_hr = dword_regs[f"p{i}_run_hr"]

                        total_time = p_run_hr * 60 + p_run_min

                        time_rank.append((f"p{i}", total_time))

                    time_rank.sort(key=get_key)
                    lowest1 = time_rank[0][0]
                    lowest2 = time_rank[1][0]
                    top = time_rank[2][0]

                    first_p = True

                try:
                    if swap_current - swap_last >= 60:
                        dword_regs["swap_min"] += 1
                        dword_regs["swap_hr"] = int(dword_regs["swap_min"] / 60)
                        swap_last = swap_current

                    if dword_regs["swap_hr"] >= dword_regs["p_swap"]:
                        for i in range(1, 4):
                            p_run_min = dword_regs[f"p{i}_run_min"]
                            p_run_hr = dword_regs[f"p{i}_run_hr"]

                            total_time = p_run_hr * 60 + p_run_min

                            time_rank.append((f"p{i}", total_time))

                        time_rank.sort(key=get_key)
                        lowest1 = time_rank[0][0]
                        lowest2 = time_rank[1][0]
                        top = time_rank[2][0]

                        # print(f"最小的是：{lowest1} 和 {lowest2}")

                        dword_regs["swap_hr"] = 0
                        dword_regs["swap_min"] = 0
                except Exception as e:
                    print(f"auto error: {e}")

                try:
                    l1_key = f"Inv{lowest1[-1]}"
                    l2_key = f"Inv{lowest2[-1]}"
                    t_key = f"Inv{top[-1]}"

                    if check_inverter(l1_key) and check_inverter(l2_key):
                        inv_to_run.append(top)
                    elif not check_inverter(l1_key) and check_inverter(l2_key):
                        inv_to_run.append(lowest1)
                    elif check_inverter(l1_key) and not check_inverter(l2_key):
                        inv_to_run.append(lowest2)
                    else:
                        inv_to_run.append(lowest1)
                        inv_to_run.append(lowest2)

                    if top in inv_to_run:
                        if check_inverter(t_key):
                            inv_to_run = []
                    
                    if "p1" in inv_to_run:
                        open_inv1_auto()
                    else:
                        close_inv1_auto()

                    if "p2" in inv_to_run:
                        open_inv2_auto()
                    else:
                        close_inv2_auto()

                    if "p3" in inv_to_run:
                        open_inv3_auto()
                    else:
                        close_inv3_auto()
                except Exception as e:
                    print(f"run inverter error: {e}")

                change_back_mode = mode
                mode_last = "auto"
            elif mode == "stop":
                check_last_mode_from_inspection(mode_last)
                if inspection_data["force_change_mode"]:
                    cancel_inspection()
                diff = 0
                change_inspect_time()
                reset_inspect_btn()
                inspection_data["step"] = 1
                stop_p1()
                stop_p2()
                stop_p3()
                stop_fan()

                mode_last = mode
                change_back_mode = mode
            elif mode == "inspection":
                read_flow_time = 15
                pump_open_time = 10
                communication_check_time = 18
                mode_last = mode
                change_inspect_time()
                global count

                try:
                    with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                        r = client.read_holding_registers(740, 1)
                        pump_open_time = r.registers[0]
                except Exception as e:
                    print(f"read inspection time error:{e}")

                if inspection_data["start_btn"] == 1:
                    try:
                        if inspection_data["step"] == 1:
                            print("1. 全部重置")

                            inspection_data["start_time"] = time.time()

                            inv1_v, inv2_v, inv3_v = check_inv_speed()

                            inspection_data["prev"]["inv1"] = inv1_v
                            inspection_data["prev"]["inv2"] = inv2_v
                            inspection_data["prev"]["inv3"] = inv3_v

                            for key in inspection_data["result"]:
                                if key == "f1" or "_com" in key:
                                    inspection_data["result"][key] = []
                                else:
                                    inspection_data["result"][key] = False

                            for key in inspection_data["prog"]:
                                change_progress(key, "cancel")

                            try:
                                with ModbusTcpClient(
                                    host=modbus_host, port=modbus_port
                                ) as client:
                                    client.write_registers(
                                        800, [3] * len(inspection_data["prog"])
                                    )
                            except Exception as e:
                                print(f"reset inspection error:{e}")

                            stop_p1()
                            stop_p2()
                            stop_p3()

                            count += 1

                            if count > 3:
                                inspection_data["step"] += 1

                        if inspection_data["step"] == 2:
                            print(f"2. 開啟 inv/mc: {pump_open_time} 秒")

                            change_progress("p1_speed", "standby")
                            change_progress("p2_speed", "standby")
                            change_progress("p3_speed", "standby")

                            speed = translate_pump_speed(50)

                            set_pump1_speed(speed)
                            set_pump2_speed(speed)
                            set_pump3_speed(speed)

                            p1_error_box.append(warning_data["error"]["Inv1_Error"])
                            p1_error_box.append(warning_data["error"]["Inv1_OverLoad"])
                            p1_error_box.append(oc_detection["p1"])

                            p2_error_box.append(warning_data["error"]["Inv2_Error"])
                            p2_error_box.append(warning_data["error"]["Inv2_OverLoad"])
                            p2_error_box.append(oc_detection["p2"])

                            p3_error_box.append(warning_data["error"]["Inv3_Error"])
                            p3_error_box.append(warning_data["error"]["Inv3_OverLoad"])
                            p3_error_box.append(oc_detection["p3"])

                            try:
                                with ModbusTcpClient(
                                    host=modbus_host, port=modbus_port
                                ) as client:
                                    r = client.read_holding_registers(5038, 6)

                                    p1 = cvt_registers_to_float(
                                        r.registers[0], r.registers[1]
                                    )
                                    p2 = cvt_registers_to_float(
                                        r.registers[2], r.registers[3]
                                    )
                                    p3 = cvt_registers_to_float(
                                        r.registers[4], r.registers[5]
                                    )
                                    p1_data.append(p1)
                                    p2_data.append(p2)
                                    p3_data.append(p3)

                            except Exception as e:
                                print(f"pump speed check: {e}")

                            inspection_data["end_time"] = time.time()
                            diff = (
                                inspection_data["end_time"]
                                - inspection_data["start_time"]
                            )
                            if diff >= pump_open_time:
                                inspection_data["step"] += 1
                                inspection_data["mid_time"] = inspection_data[
                                    "end_time"
                                ]

                            send_progress(0, "p1_speed")
                            send_progress(1, "p2_speed")
                            send_progress(2, "p3_speed")

                        if inspection_data["step"] == 3:
                            print(f"3. 測所有 inv/mc：{pump_open_time} 秒")

                            if any(p1_error_box):
                                print("跳過 p1")
                                change_progress("p1_speed", "skip")
                                inspection_data["result"]["p1_speed"] = True
                                stop_p1()
                                send_all(0, "p1_speed")
                                inspection_data["mid_time"] = inspection_data[
                                    "end_time"
                                ]
                            else:
                                max_p1 = max(p1_data)
                                inspection_data["result"]["p1_speed"] = not (
                                    55 > max_p1 > 45
                                )
                                write_measured_data(1, max_p1)
                                change_progress("p1_speed", "finish")

                            if any(p2_error_box):
                                print("跳過 p2")
                                change_progress("p2_speed", "skip")
                                inspection_data["result"]["p2_speed"] = True
                                stop_p2()
                                send_all(1, "p2_speed")
                                inspection_data["mid_time"] = inspection_data[
                                    "end_time"
                                ]
                            else:
                                max_p2 = max(p2_data)
                                inspection_data["result"]["p2_speed"] = not (
                                    55 > max_p2 > 45
                                )
                                write_measured_data(3, max_p2)
                                change_progress("p2_speed", "finish")

                            if any(p3_error_box):
                                print("跳過 p3")
                                change_progress("p3_speed", "skip")
                                inspection_data["result"]["p3_speed"] = True
                                stop_p3()
                                send_all(2, "p3_speed")
                                inspection_data["mid_time"] = inspection_data[
                                    "end_time"
                                ]
                            else:
                                max_p3 = max(p3_data)
                                inspection_data["result"]["p3_speed"] = not (
                                    55 > max_p3 > 45
                                )
                                write_measured_data(5, max_p3)
                                change_progress("p3_speed", "finish")

                            inspection_data["step"] += 1
                            inspection_data["end_time"] = time.time()
                            inspection_data["mid_time"] = inspection_data["end_time"]
                            send_all(0, "p1_speed")
                            send_all(1, "p2_speed")
                            send_all(2, "p3_speed")

                        if inspection_data["step"] == 4:
                            print(f"4. 開 f1：{read_flow_time} 秒")

                            speed = translate_pump_speed(50)
                            set_pump1_speed(speed)
                            set_pump2_speed(speed)
                            set_pump3_speed(speed)

                            if (
                                warning_data["alert"]["ClntFlow_Low"]
                                or warning_data["error"][
                                    "coolant_flow_rate_communication"
                                ]
                            ):
                                inspection_data["result"]["f1"].append(True)
                            else:
                                inspection_data["result"]["f1"].append(False)

                            f1_data.append(status_data["ClntFlow"])

                            change_progress("f1", "standby")
                            send_progress(3, "f1")

                            inspection_data["end_time"] = time.time()
                            diff = (
                                inspection_data["end_time"]
                                - inspection_data["mid_time"]
                            )
                            if diff > read_flow_time:
                                inspection_data["step"] += 1
                                inspection_data["mid_time"] = inspection_data[
                                    "end_time"
                                ]

                        if inspection_data["step"] == 5:
                            print("5. 測 f1")
                            max_f1 = max(f1_data)

                            if warning_data["error"]["coolant_flow_rate_communication"]:
                                max_f1 = 0

                            write_measured_data(7, max_f1)
                            print(f"F1 結果：{max_f1}")

                            inspection_data["result"]["f1"] = all(
                                inspection_data["result"]["f1"]
                            )

                            change_progress("f1", "finish")
                            send_all(3, "f1")

                            inspection_data["step"] += 0.5
                            inspection_data["end_time"] = time.time()
                            inspection_data["mid_time"] = inspection_data["end_time"]

                            for x, level in enumerate(level_sw):
                                change_progress(level, "standby")
                                send_progress(37 + x, level)

                        if inspection_data["step"] == 5.5:
                            print("5.5 測 liquid & power")
                            journal_logger.info("5.5 測 liquid & power")

                            stop_p1()
                            stop_p2()
                            stop_p3()

                            for k, level in enumerate(level_sw):
                                inspection_data["result"][level] = not level_sw[level]
                                change_progress(level, "finish")
                                send_all(37 + k, level)

                            for x, key in enumerate(inspection_data["result"], start=0):
                                if "_broken" in key:
                                    change_progress(key, "standby")
                                    send_progress(4 + x, key)

                            inspection_data["step"] += 0.5

                        if inspection_data["step"] == 6:
                            print("6. 測 broken")

                            i = j = z = 0

                            for key in inspection_data["result"]:
                                if "_broken" in key:
                                    delete_part = "_broken"
                                    raw_key = key.replace(delete_part, "")

                                    if "Temp_" in key:
                                        temp_check = (
                                            sensor_raw[raw_key] > 1000
                                            or sensor_raw[raw_key] < -100
                                        )
                                        inspection_data["result"][key] = temp_check
                                        change_progress(key, "finish")
                                        send_all(4 + i, key)
                                        i += 1

                                    if "Prsr_" in key:
                                        prsr_check = sensor_raw[raw_key] < 1200
                                        inspection_data["result"][key] = prsr_check
                                        change_progress(key, "finish")
                                        send_all(8 + j, key)
                                        j += 1

                                    if "Flow_" in key:
                                        flow_check = (
                                            serial_sensor_value[raw_key] < 1000
                                            or serial_sensor_value[key] > 20000
                                        )
                                        inspection_data["result"][key] = flow_check
                                        change_progress(key, "finish")
                                        send_all(14 + z, key)
                                        z += 1

                            for (
                                register,
                                status_key,
                            ) in measured_data_mapping.items():
                                write_measured_data(register, status_data[status_key])

                            for n, key in enumerate(raw_485_comm):
                                key_name = f"{key}_com"
                                change_progress(key_name, "standby")
                                send_progress(15 + n, key_name)

                            inspection_data["step"] += 1
                            inspection_data["end_time"] = time.time()
                            inspection_data["mid_time"] = inspection_data["end_time"]

                        if inspection_data["step"] == 7:
                            print(f"7. 測 communication：{communication_check_time} 秒")

                            inspection_data["end_time"] = time.time()
                            diff = (
                                inspection_data["end_time"]
                                - inspection_data["mid_time"]
                            )

                            if int(diff) % 4 == 0 and diff <= communication_check_time:
                                for key, value in raw_485_comm.items():
                                    key_name = f"{key}_com"
                                    inspection_data["result"][key_name].append(
                                        not value
                                    )

                            if int(diff) > communication_check_time:
                                inspection_data["step"] = 12

                                for k, key in enumerate(raw_485_comm):
                                    key_name = f"{key}_com"
                                    inspection_data["result"][key_name] = not any(
                                        inspection_data["result"][key_name]
                                    )
                                    change_progress(key_name, "finish")
                                    send_all(15 + k, key_name)

                        if inspection_data["step"] == 12:
                            print("12. 最後收尾")

                            f1_data = []
                            p1_data = []
                            p2_data = []
                            p3_data = []
                            p1_error_box = []
                            p2_error_box = []
                            p3_error_box = []

                            try:
                                with ModbusTcpClient(
                                    host=modbus_host, port=modbus_port
                                ) as client:
                                    value_list_status = list(
                                        inspection_data["prog"].values()
                                    )
                                    client.write_registers(800, value_list_status)
                            except Exception as e:
                                print(f"result write-in:{e}")

                            for key, status in inspection_data["prog"].items():
                                if status == 1:
                                    inspection_data["result"][key] = False

                            try:
                                with ModbusTcpClient(
                                    host=modbus_host, port=modbus_port
                                ) as client:
                                    value_list_result = [
                                        1 if value else 0
                                        for value in inspection_data["result"].values()
                                    ]
                                    client.write_registers(750, value_list_result)

                            except Exception as e:
                                print(f"result write-in:{e}")

                            reset_inspect_btn()

                            go_back_to_last_mode(change_back_mode)
                            mode_last = mode

                            inspection_data["step"] = 1
                            inspection_data["start_time"] = 0
                            inspection_data["mid_time"] = 0
                            inspection_data["end_time"] = 0
                            diff = 0

                            try:
                                with ModbusTcpClient(
                                    host=modbus_host, port=modbus_port
                                ) as client:
                                    client.write_register(973, 2)
                            except Exception as e:
                                print(f"reset error: {e}")
                    except Exception as e:
                        print(f"inspect error:{e}")

                elif inspection_data["start_btn"] == 2:
                    print("被 cancel")

                    try:
                        with ModbusTcpClient(
                            host=modbus_host, port=modbus_port
                        ) as client:
                            value_list_status = list(inspection_data["prog"].values())
                            value_list_status = [
                                1 if value == 4 else value
                                for value in value_list_status
                            ]

                            client.write_registers(800, value_list_status)

                    except Exception as e:
                        print(f"result write-in:{e}")

                    for key, status in inspection_data["prog"].items():
                        if status == 1:
                            inspection_data["result"][key] = False

                    try:
                        with ModbusTcpClient(
                            host=modbus_host, port=modbus_port
                        ) as client:
                            value_list_result = [
                                1 if value else 0
                                for value in inspection_data["result"].values()
                            ]
                            client.write_registers(750, value_list_result)

                    except Exception as e:
                        print(f"result write-in:{e}")

                    reset_inspect_btn()

                    go_back_to_last_mode(change_back_mode)

                    mode_last = mode

                    inspection_data["step"] = 1
                    inspection_data["start_time"] = 0
                    inspection_data["mid_time"] = 0
                    inspection_data["end_time"] = 0
                    diff = 0
                    print("結束囉")

            # for i in range(1, 4):
            #     if (
            #         not bit_output_regs[f"mc{i}"]
            #         or warning_data["error"][f"Inv{i}_Error"]
            #     ):
            #         if i == 1:
            #             clear_p1_speed()
            #         elif i == 2:
            #             clear_p2_speed()
            #         elif i == 3:
            #             clear_p3_speed()

            try:
                output_value = list(bit_output_regs.values())
                light_value = list(color_light.values())
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    client.write_coils(2, output_value)
                    client.write_coils(14, light_value)
                    client.write_coils((8192 + 700), [oc_issue])
            except Exception as e:
                print(f"set output data error: {e}")

            if inv["inv1"]:
                pump1_run_current_time = time.time()

                if pump1_run_current_time - pump1_run_last_min >= 60:
                    dword_regs["p1_run_min"] += 1
                    dword_regs["p1_run_hr"] = int(dword_regs["p1_run_min"] / 60)
                    pump1_run_last_min = pump1_run_current_time

                    try:
                        with ModbusTcpClient(
                            host=modbus_host, port=modbus_port
                        ) as client:
                            rt1_min = split_double([dword_regs["p1_run_min"]])
                            rt1_hr = split_double([dword_regs["p1_run_hr"]])

                            client.write_registers(270, rt1_min)
                            client.write_registers(272, rt1_hr)

                            client.write_registers(200, rt1_hr)

                    except Exception as e:
                        print(f"read pump1 runtime error: {e}")
            else:
                pump1_run_last_min = time.time()

            if inv["inv2"]:
                pump2_run_current_time = time.time()

                if pump2_run_current_time - pump2_run_last_min >= 60:
                    dword_regs["p2_run_min"] += 1
                    dword_regs["p2_run_hr"] = int(dword_regs["p2_run_min"] / 60)
                    pump2_run_last_min = pump2_run_current_time
                    registers = []
                    try:
                        with ModbusTcpClient(
                            host=modbus_host, port=modbus_port
                        ) as client:
                            rt2_min = split_double([dword_regs["p2_run_min"]])
                            rt2_hr = split_double([dword_regs["p2_run_hr"]])

                            client.write_registers(274, rt2_min)
                            client.write_registers(276, rt2_hr)

                            client.write_registers(202, rt2_hr)

                    except Exception as e:
                        print(f"read pump2 runtime error: {e}")
            else:
                pump2_run_last_min = time.time()

            if inv["inv3"]:
                pump3_run_current_time = time.time()

                if pump3_run_current_time - pump3_run_last_min >= 60:
                    dword_regs["p3_run_min"] += 1
                    dword_regs["p3_run_hr"] = int(dword_regs["p3_run_min"] / 60)
                    pump3_run_last_min = pump3_run_current_time
                    registers = []
                    try:
                        with ModbusTcpClient(
                            host=modbus_host, port=modbus_port
                        ) as client:
                            rt3_min = split_double([dword_regs["p3_run_min"]])
                            rt3_hr = split_double([dword_regs["p3_run_hr"]])

                            client.write_registers(278, rt3_min)
                            client.write_registers(280, rt3_hr)
                            client.write_registers(204, rt3_hr)

                    except Exception as e:
                        print(f"read pump3 runtime error: {e}")
            else:
                pump3_run_last_min = time.time()
            set_warning_registers(mode)

            time.sleep(1)
        except Exception as e:
            print(f"TCP Client Error: {e}")

        try:
            try:
                global server1_count
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    r = client.read_holding_registers(300, 1, unit=modbus_slave_id)

                    server1_count = r.registers[0]
                    if r.registers[0] > 30000:
                        server1_count = 0
                        client.write_register(300, server1_count)

                    else:
                        server1_count += 1
                        client.write_register(300, server1_count)

            except Exception as e:
                print(f"main server count error:{e}")

            try:
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    r = client.read_holding_registers(301, 1, unit=modbus_slave_id)
                    check_server2 = r.registers[0]

                    if zero_flag:
                        server_error["diff"] = 0
                        zero_flag = False

                    if check_server2 == pre_check_server2:
                        server_error["diff"] += time.time() - server_error["start"]
                    else:
                        server_error["diff"] = 0

                    if server_error["diff"] >= 300:
                        if restart_server["stage"] == 0:
                            restart_server["stage"] = 1
                        else:
                            pass
                    else:
                        restart_server["stage"] = 0

                    if server_error["diff"] >= 5:
                        server2_occur_stop = True
                        pre_check_server2 = check_server2
                        warning_data["error"]["pc2_error"] = True
                    else:
                        server2_occur_stop = False
                        pre_check_server2 = check_server2
                        warning_data["error"]["pc2_error"] = False

            except Exception as e:
                print(f"server 1 check error:{e}")

            if server2_occur_stop:
                try:
                    with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                        if restart_server["stage"] == 1:
                            client.write_coils(13, [True])
                            print("按10秒 on")

                            restart_server["diff"] += (
                                time.time() - restart_server["start"]
                            )

                            if restart_server["diff"] > 10:
                                restart_server["stage"] = 2

                        elif restart_server["stage"] == 2:
                            client.write_coils(13, [False])
                            print("按1秒 off")
                            restart_server["diff"] += (
                                time.time() - restart_server["start"]
                            )
                            if restart_server["diff"] > 16:
                                restart_server["stage"] = 3

                        elif restart_server["stage"] == 3:
                            client.write_coils(13, [True])
                            print("按1秒 on")
                            restart_server["diff"] += (
                                time.time() - restart_server["start"]
                            )
                            if restart_server["diff"] > 18:
                                restart_server["stage"] = 4

                        elif restart_server["stage"] == 4:
                            client.write_coils(13, [False])
                            restart_server["diff"] = 0
                            restart_server["start"] = 0
                            zero_flag = True
                            print("回歸 off")
                except Exception as e:
                    print(f"server 2 restart error:{e}")
        except Exception as e:
            print(f"only pc1: {e}")


duration = 1


def rtu_thread():
    client = ModbusSerialClient(
        method="rtu",
        port="/dev/ttyS0",
        baudrate=19200,
        parity="E",
        stopbits=1,
        bytesize=8,
        timeout=0.5,
    )
    try:
        while True:
            global ver_switch

            try:
                if not client.connect():
                    for key in raw_485_data.keys():
                        raw_485_data[key] = 0
                        raw_485_comm[key] = True
                    print("Failed to connect to Modbus server")
                    journal_logger.info("Failed to connect to Modbus server")
                    time.sleep(2)
                    continue

                try:
                    r = client.read_holding_registers(2, 2, unit=4)
                    t3 = cvt_registers_to_float(r.registers[0], r.registers[1])
                    raw_485_data["AmbientTemp"] = t3
                    raw_485_comm["AmbientTemp"] = False
                except Exception as e:
                    raw_485_comm["AmbientTemp"] = True
                    journal_logger.info(f"Ambient Temperature error: {e}")

                time.sleep(duration)

                try:
                    r = client.read_holding_registers(0, 2, unit=4)
                    rh = cvt_registers_to_float(r.registers[0], r.registers[1])
                    raw_485_data["RelativeHumid"] = rh
                    raw_485_comm["RelativeHumid"] = False
                except Exception as e:
                    raw_485_comm["RelativeHumid"] = True
                    print(f"Relative Humidity error: {e}")

                time.sleep(duration)

                try:
                    r = client.read_holding_registers(8, 2, unit=4)
                    dewPt = cvt_registers_to_float(r.registers[0], r.registers[1])
                    raw_485_data["DewPoint"] = dewPt
                    raw_485_comm["DewPoint"] = False
                except Exception as e:
                    raw_485_comm["DewPoint"] = False
                    print(f"Dew Point Temperature error: {e}")

                time.sleep(duration)

                try:
                    r = client.read_holding_registers(0, 2, unit=9)
                    pH = cvt_registers_to_float(r.registers[0], r.registers[1])
                    raw_485_data["pH"] = pH
                    raw_485_comm["pH"] = False
                except Exception as e:
                    raw_485_comm["pH"] = True
                    print(f"pH error: {e}")

                time.sleep(duration)

                try:
                    r = client.read_holding_registers(0, 2, unit=7)
                    CON = cvt_registers_to_float(r.registers[0], r.registers[1])
                    raw_485_data["conductivity"] = CON
                    raw_485_comm["conductivity"] = False
                except Exception as e:
                    raw_485_comm["conductivity"] = True
                    print(f"CON error: {e}")

                time.sleep(duration)

                try:
                    r = client.read_holding_registers(0, 2, unit=8)
                    Tur = cvt_registers_to_float(r.registers[0], r.registers[1])
                    raw_485_data["turbidity"] = Tur
                    raw_485_comm["turbidity"] = False
                except Exception as e:
                    raw_485_comm["turbidity"] = True
                    print(f"Turbidity error: {e}")

                time.sleep(duration)

                try:
                    r = client.read_holding_registers(324, 2, unit=3)
                    instant = cvt_registers_to_float(r.registers[0], r.registers[1])
                    raw_485_data["inst_power"] = instant
                    raw_485_comm["inst_power"] = False
                except Exception as e:
                    raw_485_comm["inst_power"] = True
                    print(f"Instant Power Consumption error: {e}")

                time.sleep(duration)

                try:
                    r = client.read_holding_registers(294, 2, unit=3)
                    ac = cvt_registers_to_float(r.registers[0], r.registers[1])
                    raw_485_data["average_current"] = ac
                    raw_485_comm["average_current"] = False
                except Exception as e:
                    raw_485_comm["average_current"] = True
                    print(f"Average Current error: {e}")

                time.sleep(duration)

                pump_units = [1, 2, 11]

                for i, pump in enumerate(pump_units, start=1):
                    try:
                        r = client.read_input_registers(
                            address=8449, count=1, unit=pump
                        )
                        raw_485_data[f"Inv{i}_Freq"] = r.registers[0]
                        raw_485_comm[f"Inv{i}_Freq"] = False
                    except Exception as e:
                        raw_485_comm[f"Inv{i}_Freq"] = True
                        print(f"Pump{i} error: {e}")

                    time.sleep(duration)

                fan_units = [16, 17, 18, 19, 12, 13, 14, 15]

                for i, unit in enumerate(fan_units, start=1):
                    try:
                        r = client.read_holding_registers(1, 1, unit=unit)
                        raw_485_data[f"Fan{i}Com"] = r.registers[0]
                        raw_485_comm[f"Fan{i}Com"] = False
                    except Exception as e:
                        raw_485_comm[f"Fan{i}Com"] = True
                        print(f"Fan {i} error: {e}")

                    time.sleep(duration)

                try:
                    r = client.read_discrete_inputs(6, 9, unit=10)
                    ats1 = bool(r.bits[0])
                    ats2 = bool(r.bits[8])
                    raw_485_data["ATS1"] = ats1 == 1
                    raw_485_data["ATS2"] = ats2 == 1
                    raw_485_comm["ATS1"] = False
                    raw_485_comm["ATS2"] = False
                except Exception as e:
                    raw_485_comm["ATS1"] = True
                    raw_485_comm["ATS2"] = True
                    print(f"ATS error: {e}")

                time.sleep(duration)

                journal_logger.info(f"485 數據：{raw_485_data}")
                journal_logger.info(f"485 通訊：{raw_485_comm}")
            except Exception as e:
                print(f"enclosed: {e}")
    except Exception as e:
        print(f"485 issue: {e}")
    finally:
        client.close()


def rack_thread():
    host = {
        "rack1": "192.168.3.10",
        "rack2": "192.168.3.11",
        "rack3": "192.168.3.12",
        "rack4": "192.168.3.13",
        "rack5": "192.168.3.14",
        "rack6": "192.168.3.15",
        "rack7": "192.168.3.16",
        "rack8": "192.168.3.17",
        "rack9": "192.168.3.18",
        "rack10": "192.168.3.19",
    }

    while True:
        try:
            try:
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    r = client.read_coils((8192 + 710), 20)
                    for x, key in enumerate(rack_data["rack_control"].keys()):
                        rack_data["rack_control"][key] = r.bits[x]
            except Exception as e:
                print(f"rack control error: {e}")
                continue

            try:
                for i in range(10):
                    enable_key = f"Rack_{i + 1}_Enable"
                    control_key = f"Rack_{i + 1}_Control"
                    ip_key = f"rack{i + 1}"
                    rack_ip = host[ip_key]
                    pass_key = f"Rack_{i + 1}_Pass"

                    if rack_data["rack_control"][enable_key]:
                        try:
                            with ModbusTcpClient(
                                host=rack_ip, port=modbus_port, timeout=0.5
                            ) as client:
                                if rack_data["rack_control"][control_key]:
                                    client.write_register(0, 4095)
                                else:
                                    client.write_register(0, 0)
                                rack_data["rack_pass"][pass_key] = True
                        except Exception as e:
                            rack_data["rack_pass"][pass_key] = False
                            print(f"rack input error: {e}")
                            # journal_logger.info(f"rack input error: {e}")
            except Exception as e:
                print(f"rack key error: {e}")

            try:
                coil_values = list(rack_data["rack_pass"].values())
                with ModbusTcpClient(host=modbus_host, port=modbus_port) as client:
                    client.write_coils((8192 + 730), coil_values)
            except Exception as e:
                print(f"pass error: {e}")
        except Exception as e:
            print(f"enclosed: {e}")

        time.sleep(2)


rack_thread_obj = threading.Thread(target=rack_thread)
rack_thread_obj.daemon = True
rack_thread_obj.start()

thread = threading.Thread(target=control)
thread.daemon = True
thread.start()

if onLinux:
    rtu_thread_obj = threading.Thread(target=rtu_thread)
    rtu_thread_obj.daemon = True
    rtu_thread_obj.start()

try:
    while True:
        time.sleep(30)
except KeyboardInterrupt:
    print("程序已终止")

except Exception as e:
    print(f"異常：{e}")
