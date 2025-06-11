import uuid
import psutil

# def get_mac_uuid() -> str:
#     """
#     取得本機的 MAC 位址並轉換為 UUID 格式。
#     """
#     mac = uuid.getnode()
#     mac_uuid = uuid.UUID(int=mac)
#     mac_to_uuid()
#     return str(mac_uuid)

def get_mac_uuid() -> str:
    '''
    把 MAC Address 轉成 UUID
    '''
    mac_str = get_first_mac_psutil()
    # 字串處理
    mac_int = int(mac_str.replace("-", "").replace(":", ""), 16)
    # 更新成 UUID
    u = uuid.UUID(int=mac_int)
    
    # print(f"MAC Address: {mac_str}, UUID: {u}")
    return str(u)

def get_first_mac_psutil() -> str:
    """
    抓取所有mac並排序，回傳第一張
    """
    macs = []
    for ifname, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                mac = addr.address
                if mac and mac != "00:00:00:00:00:00":
                    macs.append(mac)
    result = sorted(set(macs))         
    # print(f"MACs: {result}")       
    return result[0]



def list_nics_fullinfo():
    """
    同時取得：
      - 介面數量
      - 每張網卡的是否啟用、速度 (Mbps)、MAC Address
    """
    stats = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()  # key: 介面名稱, value: list of snicaddr

    result = {}
    for nic_name, nic_stat in stats.items():
        speed = nic_stat.speed
        is_up = nic_stat.isup

        # psutil.net_if_addrs() 會回傳一個 list，其中可能包含多種位址（IPv4、IPv6、MAC…）。
        # 只取 family == psutil.AF_LINK (MAC)
        mac_addr = ""
        for snic in addrs.get(nic_name, []):
            if snic.family == psutil.AF_LINK:
                mac_addr = snic.address
                break

        result[nic_name] = {
            "is_up": is_up,
            "speed_mbps": speed,
            "mac_address": mac_addr
        }
        print(f"NIC: {nic_name}, Up: {is_up}, Speed: {speed} Mbps, MAC: {mac_addr}")
    return result

import psutil


