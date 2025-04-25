from pymodbus.client.sync import ModbusTcpClient
import logging
import struct

# 設置日誌輸出（可選）
logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

# Modbus 伺服器的地址與端口
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5020

# 定義讀取 input_registers 的起始地址和數量
START_ADDRESS = 1  # 起始地址
FLOAT_COUNT = 10  # 要讀取的浮點數數量
REGISTERS_PER_FLOAT = 2  # 每個浮點數需要 2 個 16 位寄存器

def read_multiple_floats():
    # 計算需要讀取的總寄存器數量
    total_registers = FLOAT_COUNT * REGISTERS_PER_FLOAT

    # 創建 Modbus 客戶端
    client = ModbusTcpClient(SERVER_HOST, port=SERVER_PORT)
    if not client.connect():
        print("無法連接到 Modbus 伺服器！")
        return

    print(f"成功連接到 {SERVER_HOST}:{SERVER_PORT}")

    try:
        # 讀取指定數量的寄存器
        response = client.read_input_registers(START_ADDRESS, total_registers)
        if response.isError():
            print(f"讀取 input_registers 時發生錯誤: {response}")
        else:
            # 取得寄存器數據
            registers = response.registers
            print(f"讀取到的寄存器數據: {registers}")

            # 迴圈處理每組浮點數
            for i in range(FLOAT_COUNT):
                # 計算每組浮點數的寄存器索引範圍
                start = i * REGISTERS_PER_FLOAT
                end = start + REGISTERS_PER_FLOAT

                # 合併兩個16位元數字成一個浮點數
                raw_bytes = struct.pack('<HH', registers[start], registers[start + 1])
                float_value = struct.unpack('<f', raw_bytes)[0]

                print(f"浮點數 {i + 1}: {float_value}")

    except Exception as e:
        print(f"讀取或處理 input_registers 時發生例外錯誤: {e}")
    finally:
        # 斷開與伺服器的連接
        client.close()

if __name__ == "__main__":
    read_multiple_floats()
