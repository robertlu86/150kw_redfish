# 標準函式庫
import sys
import time
from threading import Thread

# 第三方套件
import logging
from pymodbus.server.sync import ModbusTcpServer, ModbusBaseRequestHandler
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext, ModbusSequentialDataBlock
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.transaction import ModbusSocketFramer


logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)


input_registers = [0] * 5000
input_coils = [0] * 5000
slave_context = ModbusSlaveContext(
    ir=ModbusSequentialDataBlock(0, input_registers),
    di=ModbusSequentialDataBlock(0, input_coils),
)
context = ModbusServerContext(slaves=slave_context, single=True)


def sync_holding_to_input_with_mapping(
    proxy_client, context, address_mapping, interval=5
):
    while True:
        try:
            for holding_start, holding_length, input_start in address_mapping:
                response = proxy_client.read_holding_registers(
                    holding_start, holding_length, unit=1
                )
                if response.isError():
                    log.error(
                        f"Failed to read holding registers {holding_start}-{holding_start + holding_length - 1}: {response}"
                    )
                else:
                    values = response.registers

                    if holding_start >= 1700:
                        bits = []
                        for reg in values:
                            bits.extend([(reg >> i) & 1 for i in range(16)])

                        required_bits = bits[: holding_length * 16]

                        context[0x00].setValues(2, input_start, required_bits)

                    else:
                        context[0x00].setValues(4, input_start, values)

        except Exception as e:
            log.error(f"Error during sync: {e}")

        time.sleep(interval)


class ModbusProxyRequestHandler(ModbusBaseRequestHandler):
    def __init__(self, request, client_address, server):
        self.proxy_client = server.proxy_client
        super().__init__(request, client_address, server)

    def handle(self):
        try:
            data = self.request.recv(1024)
            if not data:
                return

            try:
                self.proxy_client.socket.sendall(data)

                response = self.proxy_client.socket.recv(1024)

                self.request.sendall(response)

            except Exception as e:
                log.error("Error forwarding request to target server: %s", e)

                self.send_error_response("Failed to communicate with target server")

        except Exception as e:
            log.error("Error handling request: %s", e)

            self.send_error_response("Failed to handle request")

    def send_error_response(self, message):
        error_response = self.create_error_response(message)
        self.request.sendall(error_response)

    def create_error_response(self, message):
        return b"ERROR: " + message.encode()


class ModbusProxyServer:
    def __init__(
        self, server_host, server_port, target_host, target_port, address_mapping
    ):
        self.server_host = server_host
        self.server_port = server_port
        self.target_host = target_host
        self.target_port = target_port
        self.address_mapping = address_mapping

        self.context = context

        self.client = ModbusTcpClient(target_host, target_port)
        try:
            self.client.connect()
        except Exception as e:
            log.error("Failed to connect to target server: %s", e)
            raise

        self.identity = ModbusDeviceIdentification()
        self.identity.VendorName = "pymodbus"
        self.identity.ProductCode = "PM"
        self.identity.VendorUrl = "http://github.com/riptideio/pymodbus/"
        self.identity.ProductName = "pymodbus Server"
        self.identity.ModelName = "pymodbus Server"
        self.identity.MajorMinorRevision = "1.0"

    def start(self):
        self.sync_thread = Thread(
            target=sync_holding_to_input_with_mapping,
            args=(self.client, self.context, self.address_mapping),
            daemon=True,
        )
        self.sync_thread.start()

        self.server = ModbusTcpServer(
            context=self.context,
            identity=self.identity,
            address=(self.server_host, self.server_port),
            framer=ModbusSocketFramer,
        )
        self.server_thread = Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        log.info(
            f"Modbus Proxy Server started on {self.server_host}:{self.server_port}"
        )

    def stop(self):
        try:
            self.server.server_close()
            self.client.close()
            log.info("Modbus Proxy Server stopped")
        except Exception as e:
            log.error("Error stopping the server: %s", e)


if __name__ == "__main__":
    # 定義映射表：每個條目 (holding_start, holding_length, input_start)
    address_mapping = [
        (1700, 2, 1), # Holding 1700~1701 對應到 Input Coils 10001~10024
        (1705, 2, 25), # Holding 1705~1706 對應到 Input Coils 10025~10048
        (1708, 4, 49), # Holding 1708~1711 對應到 Input Coils 10049~10112
        (1715, 2, 113), # Holding 1715~1716 對應到 Input Coils 10113~10150
        (1000, 100, 1), # Holding 1000~1099 對應到 Input Registers 30001~30100
        (1100, 100, 101), # Holding 1100~1199 對應到 Input Registers 30101~30200
        (1200, 71, 201), # Holding 1200~1299 對應到 Input Registers 30201~30300
    ]

    server = ModbusProxyServer(
        server_host="0.0.0.0",
        server_port=5020,
        target_host="192.168.3.250",
        target_port=502,
        address_mapping=address_mapping,
    )
    server.start()
    print("Modbus Proxy Server is running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
        print("Server stopped.")
