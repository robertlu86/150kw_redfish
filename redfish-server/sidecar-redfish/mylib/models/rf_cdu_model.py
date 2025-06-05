
import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pydantic import (
    BaseModel,
    ConfigDict,
    Field, 
    computed_field,
    model_validator,
    #validator, # deprecated
    field_validator,
)
from typing_extensions import Self

from mylib.models.rf_base_model import RfResourceBaseModel, RfResourceCollectionBaseModel
from mylib.models.rf_status_model import RfStatusModel
from mylib.utils.DateTimeUtil import DateTimeUtil

class RfCduCollectionModel(RfResourceCollectionBaseModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.odata_type = "#CoolingUnitCollection.CoolingUnitCollection"
        self.odata_id = f"/redfish/v1/ThermalEquipment/CDUs"
        self.odata_context = "/redfish/v1/$metadata#CoolingUnitCollection.CoolingUnitCollection"
        self.Name = "CDU Collection"
        self.Description = "Collection of Central Distribution Units (CDUs)"
        self.Oem = {}
        
        member_cnt = int(os.environ.get('REDFISH_CDU_COLLECTION_CNT', 1))
        for sn in range(1, member_cnt + 1):
            self.Members.append({"@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{sn}"})
        self.Members_odata_count = member_cnt


"""
@Example:
CDUs_data_1 = {
    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1",
    "@odata.type": "#CoolingUnit.v1_1_0.CoolingUnit",
    "@odata.context": "/redfish/v1/$metadata#CoolingUnit.v1_1_0.CoolingUnit",
    
    "Name": "#1 Cooling Distribution Unit",
    "Id": "1",
    "Description": "第一台冷卻分配單元，用於機箱液冷散熱",
    
    # 資訊
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
    
    # 底下服務
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
    "LeakDetection": {
        "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/LeakDetection"
    },
    # 液冷劑參數    
    "Coolant": {
        "CoolantType": "Water",
        "DensityKgPerCubicMeter": 1000,
        "SpecificHeatkJoulesPerKgK": 4180
    },
    # 泵冗餘示例
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
                },                
                {
                    "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/3"
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
    "Oem": {}
}
"""
class RfCduModel(RfResourceBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/CoolingUnit.v1_1_0.json
    @see https://redfish.dmtf.org/schemas/v1/CoolingUnit.v1_2_0.json
    """
    Status: Optional[RfStatusModel]   = None

    Manufacturer: Optional[str] = Field(default="", description="")
    Model: Optional[str] = Field(default="", description="")
    SerialNumber: Optional[str] = Field(default="", description="")
    PartNumber: Optional[str] = Field(default="", description="")
    FirmwareVersion: Optional[str] = Field(default="", description="")
    Version: Optional[str] = Field(default="", description="")
    ProductionDate: Optional[str] = Field(default="", description="The production or manufacturing date of this equipment.")

    CoolingCapacityWatts: Optional[int] = Field(default=1000, description="")
    EquipmentType: Optional[str] = Field(default="CDU", description="")

    Filters: Optional[Dict[str, Any]] = Field(default={}, description="")
    PrimaryCoolantConnectors: Optional[Dict[str, Any]] = Field(default={}, description="PrimaryCoolantConnectors")
    Pumps: Optional[Dict[str, Any]] = Field(default={}, description="Pumps")
    LeakDetection: Optional[Dict[str, Any]] = Field(default={}, description="LeakDetection")
    Coolant: Optional[Dict[str, Any]] = Field(default=None, description="Coolant")
    PumpRedundancy: Optional[Dict[str, Any]] = Field(default={}, description="PumpRedundancy")
    Reservoirs: Optional[Dict[str, Any]] = Field(default={}, description="Reservoirs")
    EnvironmentMetrics: Optional[Dict[str, Any]] = Field(default={}, description="EnvironmentMetrics")
    SecondaryCoolantConnectors: Optional[Dict[str, Any]] = Field(default={}, description="SecondaryCoolantConnectors")
    Status: Optional[RfStatusModel] = Field(default=None)
    Actions: Optional[Dict[str, Any]] = Field(default={}, description="Actions")
    Links: Optional[Dict[str, Any]] = Field(default={}, description="Links")
    Oem: Optional[Dict[str, Any]] = Field(default={}, description="Oem")

    model_config = ConfigDict(
        extra='allow',
    )

    def __init__(self, cdu_id: str, **kwargs):
        super().__init__(**kwargs)
        self.odata_type = "#CoolingUnit.v1_2_0.CoolingUnit"
        self.Name = f"#{cdu_id} Cooling Distribution Unit"
        self.Id = cdu_id
        self.odata_context = "/redfish/v1/$metadata#CoolingUnit.v1_2_0.CoolingUnit"

        # cdu_id = self.__pydantic_extra__.get('cdu_id')
        self.odata_id = f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}"

        self.Description = f"Cooling Distribution Unit #{cdu_id}, designed for liquid cooling of chassis systems."

        self.Filters = {
            "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Filters"
        }
        self.PrimaryCoolantConnectors = {
            "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/PrimaryCoolantConnectors"
        }
        self.SecondaryCoolantConnectors = {
            "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/SecondaryCoolantConnectors"
        }
        self.Pumps = {
            "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Pumps"
        }
        self.LeakDetection = {
            "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/LeakDetection"
        }
        self.Coolant = {
            "CoolantType": "PropyleneGlycolAq",
            "DensityKgPerCubicMeter": 1030, 
            "SpecificHeatkJoulesPerKgK": 3900,
        }
        # self.PumpRedundancy = [
        #     {
        #         "RedundancyType": "NPlusM",
        #         "MinNeededInGroup": 1,
        #         "RedundancyGroup": [
        #             {
        #                 "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Pumps/{sn}"
        #             }
        #             for sn in range(1, int(os.environ.get('REDFISH_PUMP_COLLECTION_CNT', 1)) + 1)
        #         ],
        #         "Status": {
        #             "Health": "OK",
        #             "State": "Enabled"
        #         }
        #     }
        # ]
        # self.Reservoirs = {
        #     "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Reservoirs"
        # }
        self.EnvironmentMetrics = {
            "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/EnvironmentMetrics"
        }
        self.Actions = {
            "#CoolingUnit.SetMode": {
                "target": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Actions/CoolingUnit.SetMode",
                "CoolingUnitMode@Redfish.AllowableValues": [
                    "Enabled",
                    "Disabled"
                ]
            }
        }
        self.Links = {
            "Chassis": [
                {
                    "@odata.id": f"/redfish/v1/Chassis/{sn}"
                }
                for sn in range(1, int(os.environ.get('REDFISH_CHASSIS_COLLECTION_CNT', 1)) + 1)
            ],
            "ManagedBy": [
                {
                    "@odata.id": "/redfish/v1/Managers/CDU"
                }
            ]
        }
        self.Oem = {}


        # TODO: to be refactored
        # for smc interop validator
        datetime_format = os.getenv("DATETIME_FORMAT", "%Y-%m-%dT%H:%M:%SZ")
        self.ProductionDate = DateTimeUtil.format_string(datetime_format)

    