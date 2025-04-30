
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
from mylib.models.status_model import StatusModel

class PowerSupplyCollectionModel(RfResourceCollectionBaseModel):
    def __init__(self, chassis_id: str, **kwargs):
        super().__init__(**kwargs)
        self.odata_type = "#PowerSupplyCollection.PowerSupplyCollection"
        self.Name = "Power Supply Collection"
        self.odata_id = f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies"
        
        power_supply_cnt = int(os.environ.get('REDFISH_POWERSUPPLY_COLLECTION_CNT', 0))
        for sn in range(1, power_supply_cnt + 1):
            self.Members.append({"@odata.id": f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{sn}"})
        self.Members_odata_count = power_supply_cnt


class PowerSupplyModel(RfResourceBaseModel):
    Status: Optional[StatusModel]   = None

    model_config = ConfigDict(
        extra='allow',
    )

    def __init__(self, chassis_id: str, **kwargs):
        super().__init__(**kwargs)
        self.odata_type = "#PowerSupply.v1_6_0.PowerSupply"
        self.Name = "System Power Control"

        # chassis_id = self.__pydantic_extra__.get('chassis_id')
        self.odata_id = f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{self.Id}"

    # @model_validator(mode='after')
    # def _set_odata_id(self) -> Self:
    #     chassis_id = self.__pydantic_extra__.get('chassis_id')
    #     self.odata_id = f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{self.Id}"
    #     return self



    