
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
# from mylib.models.status_model import StatusModel

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

    # @model_validator(mode="before")
    # @classmethod
    # def validate_odata_id(cls, v, values):
    #     return f"/redfish/v1/Chassis/{values['chassis_id']}/Sensors/{values['Id']}"
    
    # @model_validator(mode='before') # 'after' is not work
    # @classmethod
    # def _set_odata_id(cls, values, **kwargs):
    #     """
    #     @note Note that `@root_validator` is deprecated and should be replaced with `@model_validator`.
    #     @see https://docs.pydantic.dev/latest/concepts/validators/#model-validators
    #     """
    #     chassis_id = values.get('chassis_id')
    #     values['@odata.id'] = f"/redfish/v1/Chassis/{chassis_id}/Sensors/{values['Id']}"
    #     # del redundant fields
    #     del values['chassis_id'] # Not in redfish spec.
    #     return values

    @model_validator(mode='after') # 'after' is not work
    # @classmethod
    def _set_odata_id(cls, self, **kwargs):
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
    
# if __name__ == "__main__":
#     import json

#     Sensors_data = {
#         "PrimaryFlowLitersPerMinute": {
#             "@odata.type": "#Sensor.v1_1_0.Sensor",
#             "Id": "PrimaryFlowLitersPerMinute",
#             "Name": "Primary Flow Liters Per Minute",
#             "Reading": "1",
#             "ReadingUnits": "L/min",
#             "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryFlowLitersPerMinute",
#         },
#         "PrimaryHeatRemovedkW": {
#             "@odata.type": "#Sensor.v1_1_0.Sensor",
#             "Id": "PrimaryHeatRemovedkW",
#             "Name": "Primary Heat Removed kW",
#             "Reading": 0.2,
#             "ReadingUnits": "kW",
#             "@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryHeatRemovedkW",
#         },
#         "HumidityPercent": {
#             "@odata.type": "#Sensor.v1_1_0.Sensor",
#             "Id": "HumidityPercent",
#             "Name": "Humidity Percent",
#             "Reading": 56.73,
#             "ReadingUnits": "Percent",
#             "Status": {
#                 "Health": "OK", 
#                 "State": "Enabled"
#             },
#             "@odata.id": "/redfish/v1/Chassis/1/Sensors/HumidityPercent",
#         },
#     }
#     for key in Sensors_data.keys():
#         sensor = Sensors_data[key]
#         del sensor['@odata.id']
#         # sensor['chassis_id'] = "1"
#         m = SensorModel(**sensor, chassis_id="100000000")
#         # print(f"output => {m.model_dump_json(by_alias=True)}")
#         dump_result = m.model_dump(by_alias=True, exclude_none=True) #exclude_none: 排除值為 None 的欄位
#         print(f"output => {json.dumps(dump_result, indent=4, ensure_ascii=False)}")
