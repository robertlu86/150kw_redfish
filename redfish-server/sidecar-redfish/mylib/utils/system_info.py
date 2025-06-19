import uuid
import psutil
import subprocess
import socket

#====================================================
# get system uuid
#====================================================
def get_system_uuid():
    """
    Get system uuid by command: `sudo dmidecode -s system-uuid`
    @Author: Chatgpt, welson
    @Note: You can impl. this function by `pip install python-dmidecode`, only works on specific Linux. 
    """
    try:
        # FAIL: it will requuest user to type-in password in terminal
        # output = subprocess.check_output(
        #     ["sudo", "dmidecode", "-s", "system-uuid"],
        #     stderr=subprocess.DEVNULL  # 隱藏錯誤訊息
        # ).decode().strip()
        # return output
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, str(get_first_mac_psutil())))
    except Exception as e:
        return str(uuid.uuid3(uuid.NAMESPACE_DNS, str(get_first_mac_psutil())))

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

#====================================================
# get network info 
# ===================================================
def list_nics_fullinfo():
    """
    同時取得：
      - 介面數量
      - 每張網卡的是否啟用、速度 (Mbps)、MAC Address
    """
    stats = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()
    interfaces = []

    for name, stat in stats.items():
        # Filter out down or non-physical (speed == 0) interfaces
        if not stat.isup or getattr(stat, 'speed', 0) <= 0:
            continue

        iface = {
            'Name': name,
            'MAC': None,
            'IPv4': [],
            'IPv6': [],
            'Speed_Mbps': stat.speed,
            'MTU': stat.mtu,
            'FullDuplex': stat.duplex == psutil.NIC_DUPLEX_FULL,
            'isUp': stat.isup
        }

        for addr in addrs.get(name, []):
            if addr.family == socket.AF_INET:
                if not addr.address.startswith('127.'):
                    iface['IPv4'].append(addr.address)
            elif addr.family == socket.AF_INET6:
                iface['IPv6'].append(addr.address.split('%')[0])
            elif addr.family == psutil.AF_LINK or addr.family == socket.AF_PACKET:
                iface['MAC'] = addr.address

        # 如果過濾完 IPv4，發現都沒有有效地址，也可視為非實體
        if not iface['IPv4']:
            continue

        # Convert lists to comma-separated strings
        iface['IPv4'] = ', '.join(iface['IPv4'])
        iface['IPv6'] = ', '.join(iface['IPv6'])
        interfaces.append(iface)
        print(f"共 {len(interfaces)} 張實體網卡：")
        for iface in interfaces:
            print(f"\n名稱: {iface['Name']}")
            print(f"  MAC            : {iface['MAC']}")
            print(f"  IPv4           : {iface['IPv4']}")
            print(f"  IPv6           : {iface['IPv6']}")
            print(f"  Speed (Mbps)   : {iface['Speed_Mbps']}")
            print(f"  MTU            : {iface['MTU']}")
            print(f"  Full Duplex    : {iface['FullDuplex']}")
            print(f"  Is Up          : {iface['isUp']}")

    return interfaces




