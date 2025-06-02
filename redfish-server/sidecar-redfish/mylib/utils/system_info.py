import uuid

def get_mac_uuid() -> str:
    """
    取得本機的 MAC 位址並轉換為 UUID 格式。
    """
    mac = uuid.getnode()
    mac_uuid = uuid.UUID(int=mac)
    # print(f"MAC Address: {mac}, UUID: {mac_uuid}")
    return str(mac_uuid)

