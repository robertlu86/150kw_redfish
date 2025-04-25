import struct
from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusSlaveContext,
    ModbusServerContext,
)

raw_data = {
    "temp_clntSply": 34,
    "temp_clntSplySpr": 1020,
    "temp_clntRtn": 41,
    "temp_waterIn": 1020,
    "temp_waterOut": 3,
    "prsr_clntSply": 2,
    "prsr_clntSplySpr": 2200,
    "prsr_clntRtn": 3,
    "prsr_fltIn": 2200,
    "prsr_flt1Out": 4,
    "prsr_flt2Out": 2200,
    "prsr_flt3Out": 5,
    "prsr_flt4Out": 2200,
    "prsr_flt5Out": 6,
    "prsr_qltOut": 2200,
    "prsr_wtrIn": 7,
    "prsr_wtrOut": 2200,
    "pV_wtr": 76,
    "rltHmd": 52.4,
    "temp_ambient": 1200,
    "dewPt": 4,
    "flow_clnt": 45.7,
    "flow_wtr": 38.6,
    "pH": 7.2,
    "cdct": 65.1,
    "tbd": 15.8,
    "power": 84.9,
    "inv1_freq": 50.2,
    "inv2_freq": 60.1,
}

data = {
    "value": {
        "temp_clntSply": 11.1,
        "temp_clntRtn": 22.2,
        "prsr_clntSply": 33.3,
        "prsr_clntRtn": 44.4,
        "flow_clnt": 55.5,
        "pH": 66.66,
        "cdct": 77.77,
        "tbd": 88.88,
        "power": 99.9,
        "average_current": 1.1,
        "inv1_freq": 2.2,
        "inv2_freq": 3.3,
        "inv3_freq": 4.4,
    },
    "valve": {"EV1": False, "EV2": False, "EV3": False, "EV4": False},
}

ctr_data = {
    "value": {
        "opMod": "Auto",
        "oil_temp_set": 0,
        "oil_pressure_set": 0,
        "pump1_speed": 0,
        "pump2_speed": 0,
        "water_PV": 0,
        "filter_interval": 0,
        "filter_time": 0,
        "pump_swap_time": 0,
    },
    "text": {
        "Pump1_run_time": 65535,
        "Pump2_run_time": 30000,
    },
    "checkbox": {"filter_unlock_sw": True, "all_filter_sw": False},
    "unit": {"unit_temp": "", "unit_prsr": ""},
    "valve": {"ev1_sw": False, "ev2_sw": False, "ev3_sw": False, "ev4_sw": False},
}

ini_values = list(data["value"].values())
ini_values2 = list(ctr_data["text"].values())

store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [0] * 50000),
    co=ModbusSequentialDataBlock(0, [0] * 50000),
    ir=ModbusSequentialDataBlock(0, [0] * 50000),
    di=ModbusSequentialDataBlock(0, [0] * 50000),
)

context = ModbusServerContext(slaves=store, single=True)


def change_to_float(value):
    to_binary = struct.pack(">f", float(value))
    r1, r2 = struct.unpack(">HH", to_binary)
    return r1, r2


def split_double(Dword_list):
    registers = []

    for d in Dword_list:
        lower_16 = d & 0xFFFF
        upper_16 = (d >> 16) & 0xFFFF

        registers.append(lower_16)
        registers.append(upper_16)
    return registers


def init_data():
    # hr_values = []
    # raw_values = []
    # index = 0
    # runtime1 = [4500]
    # runtime2 = [5000]

    # filter_time1 = [100]
    # filter_time3 = [100]
    # filter_time5 = [100]
    # filter_time1_min = [6000]

    # com_values = [True]

    # for key, value in data["value"].items():
    #     result1, result2 = change_to_float(value)
    #     hr_values.append(result2)
    #     hr_values.append(result1)

    # for k, v in raw_data.items():
    #     if index < 18:
    #         raw_values.append(v)
    #     else:
    #         r1, r2 = change_to_float(v)
    #         raw_values.append(r2)
    #         raw_values.append(r1)
    #     index += 1

    # rt1 = split_double(runtime1)
    # rt2 = split_double(runtime2)

    # context[0].setValues(16, 200, rt1)
    # context[0].setValues(16, 202, rt2)

    # f1 = split_double(filter_time1)
    # f3 = split_double(filter_time3)
    # f5 = split_double(filter_time5)

    # f1_min = split_double(filter_time1_min)

    # context[0].setValues(16, 562, f1)
    # context[0].setValues(16, 570, f3)
    # context[0].setValues(16, 578, f5)
    # context[0].setValues(16, 560, f1_min)
    # context[0].setValues(4, 15, [15])
    # context[0].setValues(3, 16, [16])

    # context[0].setValues(16, 50, [300])

    # # context[0].setValues(16, 0, hr_values)

    # context[0].setValues(16, 270, [0] * 4)

    # context[0].setValues(16, 3000, [15])

    # context[0].setValues(16, (20480 + 6740), [100])
    # context[0].setValues(16, (20480 + 6780), [200])

    # context[0].setValues(5, (8192 + 20), [True, True])

    # context[0].setValues(5, (8192 + 530), [False])

    # context[0].setValues(1, 11, [1])
    # context[0].setValues(2, 12, [1])
    # context[0].setValues(3, 13, [1])
    # context[0].setValues(4, 14, [1])
    # context[0].setValues(5, 15, [1])
    
    # context[0].setValues(1, 11, [1])    #coil                          讀寫
    # context[0].setValues(2, 12, [1])    #input coil               只讀
    # context[0].setValues(3, 13, [1])    #holding_regiser    讀寫
    # context[0].setValues(4, 14, [1])    #input_register       只讀
    
    context[0].setValues(2, 27, [1])    #input coil 
    context[0].setValues(2, 28, [1])    #input coil 
    context[0].setValues(2, 29, [1])    #input coil 
    context[0].setValues(2, 30, [1])    #input coil 
    context[0].setValues(2, 31, [1])    #input coil 
    
    # context[0].setValues(5, (8192 + 100), com_values)
    # context[0].setValues(5, (8192 + 102), com_values)
    # context[0].setValues(5, (8192 + 104), com_values)
    # context[0].setValues(5, (8192 + 106), com_values)
    # context[0].setValues(5, (8192 + 108), com_values)

    print("開始運行")


init_data()

StartTcpServer(context, address=("0.0.0.0", 502))
