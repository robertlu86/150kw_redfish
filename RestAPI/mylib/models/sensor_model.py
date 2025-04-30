
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

from mylib.models.status_model import StatusModel

class SensorCollectionModel(BaseModel):
    odata_type: str   = Field(default="#SensorCollection.SensorCollection", alias="@odata.type")
    Name: str         = Field(default="Sensor Collection")
    Members_odata_count: int      = Field(default=0, alias="Members@odata.count")
    Members: List[Dict[str, Any]] = Field(default=[], description='[{"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryFlowLitersPerMinute"}, ...]')
    Oem: Dict[str, Any]           = Field(default={})
    odata_id: Optional[str]       = Field(default=None, alias="@odata.id", description="/redfish/v1/Chassis/<chassis_id>/Sensors")

    def build_odata_id(self, chassis_id: str):
        return f"/redfish/v1/Chassis/{chassis_id}/Sensors"


class SensorModel(BaseModel):
    odata_type: str   = Field(default="#Sensor.v1_1_0.Sensor", alias="@odata.type")
    Id: str           = Field(default="", description="ex: PrimaryFlowLitersPerMinute|PrimaryHeatRemovedkW|..., 會放到odata_id的最後一層")
    Name: str         = Field(default="")
    Reading: float    = Field(default=0.0, description="ex: 23.5")
    ReadingUnits: str = Field(default="", description="ex: L/min, kW, kPa, ...")
    odata_id: Optional[str]         = Field(default=None, alias="@odata.id", description="")
    Status: Optional[StatusModel]   = None

    model_config = ConfigDict(
        extra='allow',
        exclude_none=True # 排除 None 的值
    )

    def build_odata_id(self, chassis_id: str):
        return f"/redfish/v1/Chassis/{chassis_id}/Sensors/{self.Id}"

    @model_validator(mode='after')
    def _set_odata_id(self, **kwargs):
        """
        @see https://docs.pydantic.dev/latest/concepts/validators/#model-validators
        """
        # chassis_id = values.get('chassis_id')
        # values['@odata.id'] = f"/redfish/v1/Chassis/{chassis_id}/Sensors/{self.Id}"
        chassis_id = self.__pydantic_extra__.get('chassis_id')
        self.odata_id = f"/redfish/v1/Chassis/{chassis_id}/Sensors/{self.Id}"
        return self


    # @computed_field
    # @property
    # def odata_id(self) -> str:
    #     # chassis_id = self.__pydantic_extra__['chassis_id']
    #     chassis_id = self.chassis_id
    #     return f"/redfish/v1/Chassis/{chassis_id}/Sensors/{self.Id}"
    
