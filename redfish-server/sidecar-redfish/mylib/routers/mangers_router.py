from flask import request
from flask_restx import Namespace, Resource, fields
from mylib.utils.load_api import load_raw_from_api 
from mylib.utils.load_api import CDU_BASE
from mylib.services.rf_managers_service import RfManagersService

managers_ns = Namespace('', description='Chassis Collection')

managers_data = {
    "@odata.id": "/redfish/v1/Managers",
    "@odata.type": "#ManagerCollection.ManagerCollection",
    "@odata.context": "/redfish/v1/$metadata#ManagerCollection.ManagerCollection",
    
    "Name": "Manager Collection",
    "Description":    "The collection of all available Manager resources on the system.",
    
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/Managers/CDU"
        }
    ],
    "Oem": {},
}

managers_cdu_data =    {
    "@odata.id": "/redfish/v1/Managers/CDU",
    "@odata.type": "#Manager.v1_15_0.Manager",
    "@odata.context": "/redfish/v1/$metadata#Manager.v1_15_0.Manager",
    
    "Id": "CDU",
    "Name": "CDU Network Interface Module",
    "Description": "Cooling Distribution Unit Management Module",
    
    "ManagerType": "ManagementController",
    
    # 製造商與韌體資訊
    "Manufacturer": "Supermicro",
    "PartNumber": "LCS-SCDU-200AR001",
    "Model": "200KW-SideCar-L/A-Colling-CDU",
    "FirmwareVersion": "1502",# webUI1版本
    "SerialNumber":"LCS-SCDU-200AR001", # 讀WebUI的FW Status，不是固定值
    "UUID": "00000000-0000-0000-0000-e45f013e98f8",
    "ServiceEntryPointUUID": "92384634-2938-2342-8820-489239905423",
    
    # 時間與時區
    "DateTime": "2025-02-21T06:02:08Z", # 有規範怎麼寫 ok
    "DateTimeLocalOffset": "+00:00", # 有規範怎麼寫 ok
    "LastResetTime": "2025-01-24T07:08:48Z",
    
    # 自動夏令時間（DST）設定
    "AutoDSTEnabled": False,
    "AutoDSTEnabled@Redfish.AllowableValues": [
        "False"
    ],
    # 時區名稱，以及可選列表
    "TimeZoneName": "Taipei Standard Time",
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
    # 服務與連線狀態
    "Status": {
        "State": "Enabled",
        "Health": "Critical"
    },
    "PowerState": "On",
    # 可支援的串流方式
    "SerialConsole": {
        "ServiceEnabled": False
    },
    "ServiceIdentification": "ServiceRoot",
    
    "LogServices": {
        # TBD
        "@odata.id": "/redfish/v1/Managers/CDU/LogServices"
    },
    "HostInterfaces": {
        # TBD
        "@odata.id": "/redfish/v1/Managers/CDU/HostInterfaces"
    },
    "NetworkProtocol": {
        "@odata.id": "/redfish/v1/Managers/CDU/NetworkProtocol"
    },
    "EthernetInterfaces": {
        "@odata.id": "/redfish/v1/Managers/CDU/EthernetInterfaces"
    },

    
    "Links": {
        "Oem": {
            # "Supermicro": {
            #     "Memory": {
            #         "@odata.id": "/redfish/v1/Managers/CDU/Memory"
            #     },
            # }
        }
    },
    
    # 允許 client 用 PATCH 修改的屬性
    "@Redfish.WriteableProperties": [
        "DateTime",
        "DateTimeLocalOffset",
        "AutoDSTEnabled",
        "TimeZoneName"
    ],
    
    "Actions": {
        "#Manager.ResetToDefaults": {
            "target": "/redfish/v1/Managers/CDU/Actions/Manager.ResetToDefaults",
            "ResetType@Redfish.AllowableValues": [
                "PreserveNetwork",
                "ResetAll",
                "PreserveNetworkAndUsers",
            ]
        },
        "#Manager.Reset": {
            "target": "/redfish/v1/Managers/CDU/Actions/Manager.Reset",
            "ResetType@Redfish.AllowableValues": [
                "ForceRestart",
                "GracefulRestart"
            ]
        },
        "#Manager.Shutdown": {
            "target": "/redfish/v1/Managers/CDU/Actions/Manager.Shutdown",
            "ShutdownType@Redfish.AllowableValues": [
                "ForceRestart",
                "GracefulRestart"
            ]
        },
        "Oem": {}
    },
    "Oem": {
        "Supermicro": {
            # 暫時設定
            # "@odata.id": "/redfish/v1/Managers/CDU/Supermicro"
        }
    }
}

ethernet_interfaces_data = {
    "@odata.id": "/redfish/v1/Managers/CDU/EthernetInterfaces",
    "@odata.type": "#EthernetInterfaceCollection.EthernetInterfaceCollection",
    "@odata.context": "/redfish/v1/$metadata#EthernetInterfaceCollection.EthernetInterfaceCollection",
    "Name": "Ethernet Network Interface Collection",
    "Description": "Network Interface Collection for the CDU Management Controller",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/Managers/CDU/EthernetInterfaces/Main"
        }
    ],
    "Oem": {},
}

#====================================================== 
# Managers
#====================================================== 
@managers_ns.route("/Managers")
class Managers(Resource):
    # # @requires_auth
    @managers_ns.doc("managers")
    def get(self):
        
        return managers_data
import datetime       
@managers_ns.route("/Managers/CDU")
class ManagersCDU(Resource):
    # # @requires_auth
    @managers_ns.doc("managers_cdu")
    def get(self):
        local_now = datetime.datetime.now().astimezone().replace(microsecond=0)

        locol_time = local_now.strftime('%Y-%m-%dT%H:%M:%S')

        rep = managers_cdu_data
        rep['DateTime'] = locol_time + "Z"
        rep['DateTimeLocalOffset'] = local_now.strftime('%z')[:3] + ':' + local_now.strftime('%z')[3:]
        rep["FirmwareVersion"] = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/display/version")["version"]["WebUI"]
        return rep, 200

#====================================================== 
# NetworkProtocol
#====================================================== 
Host_name = managers_ns.model('HttpProtocolPatch', {
    'HostName': fields.String(
        required=True,
        description='啟用或停用 HTTP (80/TCP)',
        example="CDU-200KW"
    ),
})
http_patch = managers_ns.model('HttpProtocolPatch', {
    'ProtocolEnabled': fields.Boolean(
        required=True,
        description='啟用或停用 HTTP (80/TCP)',
        example=True
    ),
    'Port': fields.Integer(
        required=False,
        description='HTTP 要監聽的埠號 (1–65535)',
        example=8080
    )
})

# HTTPS 更新時可傳 ProtocolEnabled + Port
https_patch = managers_ns.model('HttpsProtocolPatch', {
    'ProtocolEnabled': fields.Boolean(
        required=True,
        description='啟用或停用 HTTPS (443/TCP)',
        example=False
    ),
    'Port': fields.Integer(
        required=False,
        description='HTTPS 要監聽的埠號 (1–65535)',
        example=8443
    )
})

# SSH 更新時只需 ProtocolEnabled
ssh_patch = managers_ns.model('SshProtocolPatch', {
    'ProtocolEnabled': fields.Boolean(
        required=True,
        description='啟用或停用 SSH (22/TCP)',
        example=True
    )
})

# SNMP 更新時只需 ProtocolEnabled
snmp_patch = managers_ns.model('SnmpProtocolPatch', {
    'ProtocolEnabled': fields.Boolean(
        required=True,
        description='啟用或停用 SNMP (161/UDP)',
        example=False
    )
})

# NTP 更新時可傳 ProtocolEnabled + NTPServers 列表
ntp_patch = managers_ns.model('NtpProtocolPatch', {
    'ProtocolEnabled': fields.Boolean(
        required=True,
        description='啟用或停用 NTP (123/UDP)',
        example=True
    ),
    'NTPServers': fields.List(
        fields.String,
        required=False,
        description='NTP 伺服器清單',
        example=['0.pool.ntp.org', '1.pool.ntp.org']
    )
})

# DHCP 更新時只需 ProtocolEnabled
dhcp_patch = managers_ns.model('DhcpProtocolPatch', {
    'ProtocolEnabled': fields.Boolean(
        required=True,
        description='啟用或停用 DHCP (UDP 67/68)',
        example=False
    )
})

# 2) 定義最上層的 NetworkProtocolPatch model，把上述所有 Nested 放進來
NetworkProtocolPatch = managers_ns.model('NetworkProtocolPatch', {
    'HTTP':  fields.Nested(http_patch,  required=False, description='HTTP 協議設定'),
    'HTTPS': fields.Nested(https_patch, required=False, description='HTTPS 協議設定'),
    'SSH':   fields.Nested(ssh_patch,   required=False, description='SSH 協議設定'),
    'SNMP':  fields.Nested(snmp_patch,  required=False, description='SNMP 協議設定'),
    'NTP':   fields.Nested(ntp_patch,   required=False, description='NTP 協議設定'),
    'DHCP':  fields.Nested(dhcp_patch,  required=False, description='DHCP 協議設定'),
})

SnmpPatch = managers_ns.model('SnmpPatch', {
    'TrapIP': fields.String(
        required=True,
        description='IP address of the SNMP trap receiver',
        example="127.0.0.1"
    ),
    # 'TrapPort': fields.Integer(
    #     required=True,
    #     description='Port of the SNMP trap receiver',
    #     example=162
    # ),
    'Community': fields.String(
        required=True,
        description='SNMP community string',
        example="public",
        enum = ["public", "private"]  # 假設只允許這兩個社群字串
    ),
    # 'TrapFormat': fields.String(
    #     required=True,
    #     description='SNMP trap format',
    #     example="v2c",
    #     enum=["v2c"]
    # ),
    'Enabled': fields.Boolean(
        required=True,
        description='Enable or disable the SNMP trap',
        example=True
    )
})


@managers_ns.route("/Managers/CDU/NetworkProtocol")
class ManagersCDUNetworkProtocol(Resource):

    @managers_ns.doc("managers_cdu_network_protocol_get")
    def get(self):

        return RfManagersService().NetworkProtocol_service(), 200  

    @managers_ns.expect(NetworkProtocolPatch, validate=True)
    @managers_ns.doc("managers_cdu_network_protocol_patch")
    # @requires_auth
    def patch(self):
        body = request.json or {}
        # 只驗其中一個欄位就夠 validator 用
        ntp = body.get("NTP", {})
        RfManagersService().NetworkProtocol_service_patch(ntp)
            
        return "", 200
    
# @managers_ns.route("/Managers/CDU/NetworkProtocol/Oem/Supermicro/SNMPServers")
# class ManagersCDUNetworkProtocolOemSupermicroSNMPServers(Resource):
#     @managers_ns.doc("managers_cdu_network_protocol_oem_supermicro_snmpservers")
#     # @requires_auth
#     def get(self):
#         return RfManagersService().NetworkProtocol_Snmp_get()
    
#     @managers_ns.expect(SnmpPatch)
#     def patch(self):
#         body = request.json or {}
#         return RfManagersService().NetworkProtocol_Snmp_patch(body)
        
@managers_ns.route("/Managers/CDU/NetworkProtocol/HTTPS/Certificates")
class ManagersCDUNetworkProtocolHTTPS(Resource):
    @managers_ns.doc("managers_cdu_network_protocol_https_certificates")
    # @requires_auth
    def get(self):
        network_Certificates_data = {
            "@odata.id": "/redfish/v1/Managers/CDU/NetworkProtocol/HTTPS/Certificates",
            "@odata.type": "#CertificateCollection.CertificateCollection",
            "@odata.context": "/redfish/v1/$metadata#CertificateCollection.CertificateCollection",
            
            "Name": "Certificate Collection",
            "Members@odata.count": 1,
            "Members": [
                {
                    "@odata.id": "/redfish/v1/Managers/CDU/NetworkProtocol/HTTPS/Certificates/1"
                }
            ]
        }
        return network_Certificates_data
    
@managers_ns.route("/Managers/CDU/NetworkProtocol/HTTPS/Certificates/<string:cert_id>")
class ManagersCDUNetworkProtocolHTTPSCertificates(Resource):
    @managers_ns.doc("managers_cdu_network_protocol_https_certificates")
    # @requires_auth
    def get(self, cert_id):
        certificate_1_data = {
            "@odata.id": f"/redfish/v1/Managers/CDU/NetworkProtocol/HTTPS/Certificates/{cert_id}",
            "@odata.type": "#Certificate.v1_9_0.Certificate",
            "@odata.context": "/redfish/v1/$metadata#Certificate.v1_9_0.Certificate",
            
            "Id": cert_id,
            "Name": f"Certificate {cert_id}",
            
            "CertificateString": "TBD",
            "CertificateType": "PEM",
            "Issuer": {
                "DisplayString": "CN=Example CA",
            },
            "KeyUsage": [
                "DigitalSignature",
            ],
            "Subject": {
                "DisplayString": "CN=example.com",
            },
            "ValidNotAfter": "2025-01-01T00:00:00Z",
            "ValidNotBefore": "2024-01-01T00:00:00Z",
            
            "Actions": {
                "#Certificate.Renew": {
                    "@Redfish.ActionInfo": "/redfish/v1/.../Certificates/1/Actions/Certificate.RenewActionInfo",
                    "target":    "/redfish/v1/.../Certificates/1/Actions/Certificate.Renew",
                    "title":     "Renew Certificate",  
                },
                "#Certificate.Rekey": {
                    "@Redfish.ActionInfo": "/redfish/v1/.../Certificates/1/Actions/Certificate.RekeyActionInfo",
                    "target":    "/redfish/v1/.../Certificates/1/Actions/Certificate.Rekey",
                    "title":     "Rekey Certificate",
                }
            }
            
        }
        return certificate_1_data   
#====================================================== 
# EthernetInterfaces
#====================================================== 
@managers_ns.route("/Managers/CDU/EthernetInterfaces", strict_slashes=False)
class ManagersCDUEthernetInterfaces(Resource):
    # # @requires_auth
    @managers_ns.doc("managers_cdu_ethernet_interfaces")
    def get(self):
        
        return ethernet_interfaces_data
    
@managers_ns.route("/Managers/CDU/EthernetInterfaces/<string:ethernet_interfaces_id>")
class ManagersCDUEthernetInterfacesMain(Resource):
    # # @requires_auth
    @managers_ns.doc("managers_cdu_ethernet_interfaces")
    def get(self, ethernet_interfaces_id):
        ethernet_data = load_raw_from_api(f"{CDU_BASE}/api/v1/cdu/components/network")[ethernet_interfaces_id]
        print(ethernet_data)
        ethernet_interfaces_main_data ={
            "@odata.id": f"/redfish/v1/Managers/CDU/EthernetInterfaces/{ethernet_interfaces_id}",
            "@odata.type": "#EthernetInterface.v1_12_4.EthernetInterface",
            "@odata.context": "/redfish/v1/$metadata#EthernetInterface.v1_12_4.EthernetInterface",
            
            "Id": str(ethernet_interfaces_id),
            "Name": f"Manager Ethernet Interface {ethernet_interfaces_id}",
            "Description": "Network Interface of the CDU Management Controller",
            
            # TBD 不知道怎麼判斷
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            },
            
            "LinkStatus": "LinkUp",
            "InterfaceEnabled": True,
            "PermanentMACAddress": "e4-5f-01-3e-98-f8", # profile不用
            "MACAddress": "e4-5f-01-3e-98-f8",
            "SpeedMbps": 1000,
            "AutoNeg": True, # profile不用
            "FullDuplex": True, # profile不用
            "MTUSize": 1500, # profile不用
            
            # 可由 client 修改的欄位
            "@Redfish.WriteableProperties": [
                "InterfaceEnabled",
                "MTUSize",
                "HostName",
                "FQDN",
                "VLAN",
                "IPv4Addresses",
                "IPv6StaticAddresses"
            ],
            
            "HostName": "localhost",
            "FQDN": None,

            # VLAN 設定 profile不用
            "VLAN": {
                "VLANEnable": False,
                "VLANId": None
            },
            # IPv4 位址清單
            "IPv4Addresses": [
                {
                    "Address": ethernet_data["IPv4Address"], 
                    "SubnetMask": ethernet_data["v4Subnet"], 
                    "AddressOrigin": "DHCP", 
                    "Gateway": ethernet_data["v4DefaultGateway"],
                    "Oem": {
                        "Supermicro": {
                            "Ipv4DHCP": {"Enabled": ethernet_data["v4dhcp_en"]},
                            "Ipv4DNS": {"Auto": ethernet_data["v4AutoDNS"]},
                            "Ipv4DNSPrimary": {"Address":ethernet_data["v4DNSPrimary"]},
                            "Ipv4DNSSecondary": {"Address":ethernet_data["v4DNSOther"]}
                        }
                    }
                }
            ],
            # profile不用跑ipv6
            "MaxIPv6StaticAddresses": 1,
            # IPv6 位址清單 
            "IPv6AddressPolicyTable": [
                {
                    "Prefix": "::1/128",
                    "Precedence": 50,
                    "Label": 0
                }
            ],
            # IPv6 靜態位址
            "IPv6StaticAddresses": [],
            # IPv6 預設閘道（若無則為 null）
            "IPv6DefaultGateway": None,
            # IPv6 位址優先權表
            "IPv6Addresses": [
                {
                    "Address": ethernet_data["IPv6Address"],
                    "PrefixLength": ethernet_data["v6Subnet"],
                    "AddressOrigin": "DHCPv6", 
                    "AddressState": "Preferred", 
                    "Oem": {
                        "Ipv6Gateway": ethernet_data["v6DefaultGateway"],
                        "Ipv6DHCP": ethernet_data["v6dhcp_en"],
                        "Ipv6DNS": ethernet_data["v6AutoDNS"],
                        "Ipv6DNSPrimary": ethernet_data["v6DNSPrimary"],
                        "Ipv6DNSSecondary": ethernet_data["v6DNSOther"]
                    }
                }
            ],
            
            # DNS 伺服器
            "NameServers": [
                "localhost"
            ],
            
            "Oem": {},
        }
        return ethernet_interfaces_main_data    
    
#=========================================0514新增==================================================    
LogServices_data = {
        "@odata.id": "/redfish/v1/Managers/CDU/LogServices",
        "@odata.type": "#LogServiceCollection.LogServiceCollection",
        "@odata.context": "/redfish/v1/$metadata#LogServiceCollection.LogServiceCollection",

        "Name": "System Event Log Service",
        "Description": "System Event and Error Log Service",
        
        "Members@odata.count": 1,
        "Members": [
            {"@odata.id": "/redfish/v1/Managers/CDU/LogServices/1"}
        ],
        "Oem": {}
    }
#====================================================== 
# LogServices
#====================================================== 
@managers_ns.route("/Managers/CDU/LogServices")
class LogServices(Resource):
    # # @requires_auth
    @managers_ns.doc("LogServices")
    def get(self):
        
        return LogServices_data   

@managers_ns.route("/Managers/CDU/LogServices/<string:log_id>")
class LogServicesId(Resource):
    # @requires_auth
    @managers_ns.doc("LogServices")
    def get(self, log_id):
        LogServices_id_data = {
            "@odata.id": f"/redfish/v1/Managers/CDU/LogServices/{log_id}",
            "@odata.type": "#LogService.v1_8_0.LogService",
            "@odata.context": "/redfish/v1/$metadata#LogService.v1_8_0.LogService",

            "Id": str(log_id),
            "Name": "System Event Log Service",
            "Description": "System Event and Error Log Service",
            
            "Entries": { "@odata.id": f"/redfish/v1/Managers/CDU/LogServices/{log_id}/Entries" },
            "LogEntryType": "Event",
            "DateTime": "2021-01-01T00:00:00Z",
            "DateTimeLocalOffset": "+08:00",
            "MaxNumberOfRecords": 1000,
            "OverWritePolicy": "WrapsWhenFull",
            "ServiceEnabled": False,
            "Status": { "State": "Enabled", "Health": "OK" },
            
            "Actions": {
                "#LogService.ClearLog": {
                    "target": f"/redfish/v1/Managers/CDU/LogServices/{log_id}/Actions/LogService.ClearLog",
                }
            },
            "Oem": {}
        }
        
        return LogServices_id_data     
    
@managers_ns.route("/Managers/CDU/LogServices/<string:log_id>/Entries")
class LogServicesIdEntries(Resource):
    # @requires_auth
    @managers_ns.doc("LogServicesEntries")
    def get(self, log_id):
        LogServices_Entries__data = {
            "@odata.id": f"/redfish/v1/Managers/CDU/LogServices/{log_id}/Entries",
            "@odata.type": "#LogEntryCollection.LogEntryCollection",
            "@odata.context": "/redfish/v1/$metadata#LogEntryCollection.LogEntryCollection",

            "Name": "System Event Log Service",
            "Description": "System Event and Error Log Service",
            
            "Members@odata.count": 1,
            "Members": [
                { 
                    # service validator 只能讀到這邊 要研究為甚麼
                    "@odata.id": "/redfish/v1/Managers/CDU/LogServices/1/Entries/1",
                    
                    "Id": "1",
                    "Name": "Log Entry 1",
                    "EntryType": "Event",
                }
            ],
            "Oem": {}
        }
        
        return LogServices_Entries__data

@managers_ns.route("/Managers/CDU/LogServices/<string:log_id>/Entries/<string:entry_id>")
class LogServicesIdEntriesId(Resource):
    # @requires_auth
    @managers_ns.doc("LogServicesId")
    def get(self, log_id, entry_id):
        LogServices_Entries_id_data = {
            "@odata.id": f"/redfish/v1/Managers/CDU/LogServices/{log_id}/Entries/{entry_id}",
            "@odata.type": "#LogEntry.v1_18_0.LogEntry",
            "@odata.context": "/redfish/v1/$metadata#LogEntry.LogEntry",

            "Id": str(entry_id),    
            "Name": "System Event Log Service",
            "Description": "System Event and Error Log Service",
            
            "EntryType": "Event",
            "Created": "2021-01-01T00:00:00Z",
            "MessageId": "CDU001",
            "Message": "CDU Network Interface Module started successfully.",
            "Severity": "Critical",
            
            "Oem": {}
        }    
        return LogServices_Entries_id_data


#====================================================== 
# Memory
#======================================================     

# @managers_ns.route("/Managers/CDU/Memory")
# class ManagerMemoryCollection(Resource):
#     def get(self):
#         return {
#             "@odata.context": "/redfish/v1/$metadata#MemoryCollection.MemoryCollection",
#             "@odata.id": f"/redfish/v1/Managers/CDU/Memory",
#             "@odata.type": "#MemoryCollection.MemoryCollection",
#             "Name": "Manager Memory Collection",
#             "Members@odata.count": 1,
#             "Members": [
#                 { "@odata.id": f"/redfish/v1/Managers/CDU/Memory/1" }
#             ]
#         }

# @managers_ns.route("/Managers/CDU/Memory/<string:mem_id>")
# class ManagerMemory(Resource):
#     def get(self, mem_id):
#         return {
#             "@odata.context": "/redfish/v1/$metadata#Memory.Memory",
#             "@odata.id": f"/redfish/v1/Managers/CDU/Memory/{mem_id}",
#             "@odata.type": "#Memory.v1_4_0.Memory",
#             "Id": mem_id,
#             "Name": f"Memory {mem_id}",
#             "Status": { "State": "Enabled", "Health": "OK" },
#             "CapacityMiB": 16384,
#             "MemoryType": "DRAM"
#         }    
#====================================================== 
# HostInterfaces
#====================================================== 
@managers_ns.route("/Managers/CDU/HostInterfaces")        
class ManagerHostInterfaces(Resource):
    def get(self):
        HostInterfaces_data = {
            "@odata.context": "/redfish/v1/$metadata#HostInterfaceCollection.HostInterfaceCollection",
            "@odata.id": f"/redfish/v1/Managers/CDU/HostInterfaces",
            "@odata.type": "#HostInterfaceCollection.HostInterfaceCollection",
            "Name": "Manager Host Interface Collection",
            "Members@odata.count": 1,
            "Members": [
                { "@odata.id": f"/redfish/v1/Managers/CDU/HostInterfaces/Main" }
            ],
            "Oem": {}
        }
        return HostInterfaces_data

@managers_ns.route("/Managers/CDU/HostInterfaces/<string:hi_id>")        
class ManagerHostInterface(Resource):
    def get(self, hi_id):
        HostInterfaces_id_data = {
            "@odata.context": "/redfish/v1/$metadata#HostInterface.HostInterface",
            "@odata.id": f"/redfish/v1/Managers/CDU/HostInterfaces/{hi_id}",
            "@odata.type": "#HostInterface.v1_3_3.HostInterface",

            "Id": hi_id,
            "Name": f"Host Interface {hi_id}",
            
            "HostEthernetInterfaces": {
                "@odata.id": f"/redfish/v1/Managers/CDU/EthernetInterfaces"
            },
            "ManagerEthernetInterface": {
                "@odata.id": f"/redfish/v1/Managers/CDU/EthernetInterfaces/{hi_id}"
            },
            "InterfaceEnabled": True,
            "NetworkProtocol": {            
                "@odata.id": f"/redfish/v1/Managers/CDU/NetworkProtocol"
            },
            "Status": { "State": "Enabled", "Health": "OK" },
            
            

            "Oem": {}
    }     
        return HostInterfaces_id_data

# @managers_ns.route("/Managers/CDU/ActionRequirements")
# class ManagerActionRequirements(Resource):
#     def get(self):
#         ActionRequirements_data = {
#             "@odata.id": "/redfish/v1/Managers/CDU/ActionRequirements",
#             "@odata.type": "#ActionRequirementsCollection.ActionRequirementsCollection",
#             "Name": "Action Requirements",
#             "Members@odata.count": 1,
#             "Members": [
#                 { "@odata.id": "/redfish/v1/Managers/CDU/ActionRequirements/SetMode" }
#             ]
#         }
        
#         return ActionRequirements_data


# @managers_ns.route("/Managers/CDU/ActionRequirements/SetMode")
# class ManagerSetMode(Resource):
#     def get(self):
#         ActionRequirements_SetMode_data = {
#             "@odata.id": "/redfish/v1/Managers/CDU/ActionRequirements/SetMode",
#             "@odata.type": "#ActionRequirements.v1_0_0.ActionRequirements",
#             "Name": "SetMode Action Requirements",
#             "Action": "#Pump.SetMode",
#             "Parameters": [
#                 {
#                 "Name": "Mode",
#                 "Required": True,
#                 "DataType": "String",
#                 "AllowableValues": ["Enabled", "Disabled"]
#                 }
#             ]
#         }
        
#         return ActionRequirements_SetMode_data