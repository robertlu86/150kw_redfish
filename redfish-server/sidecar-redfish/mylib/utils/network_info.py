import psutil

def get_network_protocol_status():
    """
    利用 psutil.net_connections() 檢查本機是否在聽特定埠號，
    除了 HTTP/HTTPS/SSH/SNMP/NTP 外，現在也加上 DHCP (UDP 67/68)。
    回傳格式參考 Redfish ManagerNetworkProtocol schema，示例如下：
    {
      "HTTPEnabled": bool,
      "HTTPPort": 80,
      "HTTPSProtocolEnabled": bool,
      "HTTPSPort": 443,
      "SSHEnabled": bool,
      "SNMPEnabled": bool,
      "NTPEnabled": bool,
      "DHCPEnabled": bool,
      "DHCPPort": int,  # 67 或 68，若都沒監聽就設 0
    }
    """
    # 先收集目前所有 LISTENing 狀態的端口（包含 TCP/UDP）
    listening_ports = set()
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == psutil.CONN_LISTEN:
            # conn.laddr = (ip, port)
            listening_ports.add(conn.laddr.port)

    # 定義我們關心的協議及其預設埠號
    protocol_ports = {
        "HTTP": 80,
        "HTTPS": 443,
        "SSH": 22,
        "SNMP": 161,
        "NTP": 123,
        # DHCP 客戶端會監聽 UDP 68，DHCP 伺服器則監聽 UDP 67
        "DHCP_Server": 67,
        "DHCP_Client": 68
    }

    # 檢查 HTTP、HTTPS、SSH、SNMP、NTP 是否啟用
    http_enabled = protocol_ports["HTTP"] in listening_ports
    https_enabled = protocol_ports["HTTPS"] in listening_ports
    ssh_enabled = protocol_ports["SSH"] in listening_ports
    snmp_enabled = protocol_ports["SNMP"] in listening_ports
    ntp_enabled = protocol_ports["NTP"] in listening_ports

    # 檢查 DHCP 是否啟用：只要 67 (server) 或 68 (client) 有人在監聽，就算啟用
    dhcp_ser_port = protocol_ports["DHCP_Server"]
    dhcp_cli_port = protocol_ports["DHCP_Client"]
    dhcp_enabled = (dhcp_ser_port in listening_ports) or (dhcp_cli_port in listening_ports)

    # 決定回傳的 DHCPPort：如果 67 有人在監聽，就回傳 67；否則若 68 在監聽就回傳 68；都沒有則 0
    if dhcp_ser_port in listening_ports:
        dhcp_port = dhcp_ser_port
    elif dhcp_cli_port in listening_ports:
        dhcp_port = dhcp_cli_port
    else:
        dhcp_port = 0

    result = {
        "HTTPEnabled":        http_enabled,
        "HTTPPort":           protocol_ports["HTTP"],

        "HTTPSProtocolEnabled": https_enabled,
        "HTTPSPort":            protocol_ports["HTTPS"],

        "SSHEnabled":         ssh_enabled,
        "SSHPort":            protocol_ports["SSH"],
        
        "SNMPEnabled":        snmp_enabled,
        "SNMPPort":           protocol_ports["SNMP"],
        
        "NTPEnabled":         ntp_enabled,
        "NTPPort":            protocol_ports["NTP"],
        "NTPServers":         ["time.google.com","pool.ntp.org"],

        "DHCPEnabled":        dhcp_enabled,
        "DHCPPort":           dhcp_port
    }

    return result    