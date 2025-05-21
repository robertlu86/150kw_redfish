'''
@see https://redfish.dmtf.org/schemas/v1/PowerSupply.v1_6_0.json
'''
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
from enum import Enum
from mylib.models.rf_base_model import RfResourceBaseModel, RfResourceCollectionBaseModel
from mylib.models.rf_status_model import RfStatusModel
from mylib.models.rf_circuit_model import RfNominalVoltageType
from mylib.models.rf_assembly_model import RfAssemblyModel
from mylib.models.rf_redundancy_model import RfRedundantGroup
from mylib.models.rf_coolant_connector_collection_model import RfCoolantConnectorCollectionModel
from mylib.models.rf_fan_collection_model import RfFanCollectionModel
from mylib.models.rf_heater_collection_model import RfHeaterCollectionModel
from mylib.models.rf_leak_detection_model import RfLeakDetectionModel
from mylib.models.rf_pump_collection_model import RfPumpCollectionModel

class RfThermalSubsystemCollectionModel(RfResourceCollectionBaseModel):
    def __init__(self, chassis_id: str, **kwargs):
        # super().__init__(**kwargs)
        # self.odata_type = "#PowerSupplyCollection.PowerSupplyCollection"
        # self.Name = "Power Supply Collection"
        # self.odata_id = f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies"
        
        # power_supply_cnt = int(os.environ.get('REDFISH_POWERSUPPLY_COLLECTION_CNT', 0))
        # for sn in range(1, power_supply_cnt + 1):
        #     self.Members.append({"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{sn}"})
        # self.Members_odata_count = power_supply_cnt
        pass


class RfThermalSubsystemModel(RfResourceBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/ThermalSubsystem.v1_3_3.json
    @note properties 18 items
    """
    Odata_context: Optional[str] = Field(default=None, alias="@odata.context")
    Odata_etag: Optional[str] = Field(default=None, alias="@odata.etag")
    # "@odata.id": {1 item},
    # "@odata.type": {1 item},
    Actions: Optional[Dict[str, Any]] = Field(default=None)
    CoolantConnectorRedundancy: Optional[RfCoolantConnectorCollectionModel] = Field(default=None)
    CoolantConnectors: Optional[RfCoolantConnectorCollectionModel] = Field(default=None)
    Description: Optional[str] = Field(default=None)
    FanRedundancy: Optional[List[RfRedundantGroup]] = Field(default=None)
    Fans: Optional[RfFanCollectionModel] = Field(default=None)
    Heaters: Optional[RfHeaterCollectionModel] = Field(default=None)
    # "Id": {2 items},
    LeakDetection: Optional[RfLeakDetectionModel] = Field(default=None)
    # "Name": {2 items},
    Oem: Optional[Dict[str, Any]] = Field(default=None)
    Pumps: Optional[RfPumpCollectionModel] = Field(default=None)
    Status: Optional[RfStatusModel] = Field(default=None)
    # ThermalMetrics: Optional[List[Dict[str, Any]]] = Field(default=None)


    model_config = ConfigDict(
        extra='allow',
    )

    def __init__(self, chassis_id: str, **kwargs):
        super().__init__(**kwargs)
        self.odata_type = "#PowerSupply.v1_6_0.PowerSupply"
        self.Name = "System Power Control"

        # chassis_id = self.__pydantic_extra__.get('chassis_id')
        self.odata_id = f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{self.Id}"





    