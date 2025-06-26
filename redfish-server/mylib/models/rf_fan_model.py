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
from mylib.models.rf_assembly_model import RfAssemblyModel
from mylib.models.rf_filter_collection_model import RfFilterCollectionModel
from mylib.models.rf_sensor_model import RfSensorExcerpt
from mylib.models.rf_resource_model import RfLocationModel, RfOemModel
from mylib.models.rf_physical_context_model import RfPhysicalContext
from mylib.models.rf_sensor_model import RfSensorPumpExcerpt
from mylib.models.rf_control_model import RfControlSingleLoopExcerptModel
from mylib.models.rf_sensor_model import RfSensorPowerExcerpt, RfSensorFanExcerpt



class RfFanModel(RfResourceBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Fan.v1_5_2.json
    @note properties 26 items
    """
    class Actions(BaseModel):
        Oem: Optional[Dict[str, Any]] = Field(default=None)

    class Links(BaseModel):
        CoolingChassis: Optional[List[str]] = Field(default=None, description="An array of links to the chassis that are directly cooled by this fan.")
        CoolingChassis_odata_count: Optional[Dict] = Field(default=None, alias="CoolingChassis@odata.count")
        Oem: Optional[Dict[str, Any]] = Field(default=None)
        
    Odata_context: Optional[str] = Field(default=None, alias="@odata.context")
    Odata_etag: Optional[str] = Field(default=None, alias="@odata.etag")
    # Odata_id: Optional[str] = Field(default=None, alias="@odata.id")
    # Odata_type: Optional[str] = Field(default=None, alias="@odata.type")
    Actions: Optional[Actions] = Field(default=None)
    Assembly: Optional[RfAssemblyModel] = Field(default=None)
    Description: Optional[str] = Field(default=None)
    FanDiameterMm: Optional[int] = Field(default=None, description="The diameter of the fan assembly in millimeter units.", extra={"unit": "mm"})
    HotPluggable: Optional[bool] = Field(default=None)
    # Id: Optional[str] = Field(default=None)
    Links: Optional[Dict[str, Any]] = Field(default=None, extra={
        "example": {
            "CoolingChassis": {}, "CoolingChassis@odata.count": 0, "Oem": {}}
        }
    )
    Location: Optional[RfLocationModel] = Field(default=None)
    LocationIndicatorActive: Optional[bool] = Field(default=None)
    Manufacturer: Optional[str] = Field(default=None)
    Model: Optional[str] = Field(default=None, description="The model number for this pump.")
    # Name: Optional[str] = Field(default=None)
    Oem: Optional[RfOemModel] = Field(default=None)
    PartNumber: Optional[str] = Field(default=None)
    PhysicalContext: Optional[RfPhysicalContext] = Field(default=None)
    PowerWatts: Optional[RfSensorPowerExcerpt] = Field(default=None)
    Replaceable: Optional[bool] = Field(default=None)
    SecondarySpeedPercent: Optional[RfSensorFanExcerpt] = Field(default=None)
    SerialNumber: Optional[str] = Field(default=None)
    SparePartNumber: Optional[str] = Field(default=None, description="The spare part number for this pump.")
    SpeedPercent: Optional[RfControlSingleLoopExcerptModel] = Field(default=None, description="The speed control percentage.")
    Status: Optional[RfStatusModel] = Field(default=None)


    model_config = ConfigDict(
        extra='allow',
    )

    def __init__(self, chassis_id: str, **kwargs):
        # super().__init__(**kwargs)
        # self.odata_type = "#PowerSupply.v1_6_0.PowerSupply"
        # self.Name = "System Power Control"

        # # chassis_id = self.__pydantic_extra__.get('chassis_id')
        # self.odata_id = f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{self.Id}"
        pass

    # @model_validator(mode='after')
    # def _set_odata_id(self) -> Self:
    #     chassis_id = self.__pydantic_extra__.get('chassis_id')
    #     self.odata_id = f"/redfish/v1/Chassis/{chassis_id}/PowerSubsystem/PowerSupplies/{self.Id}"
    #     return self



    