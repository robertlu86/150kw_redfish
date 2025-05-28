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

class RfPumpType(str, Enum):
    """
    @see https://redfish.dmtf.org/schemas/v1/Pump.v1_2_0.json#/definitions/PumpType
    """
    Liquid = "Liquid"
    Compressor = "Compressor"

class RfPumpModel(RfResourceBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Pump.v1_2_0.json
    @note properties 30 items
    """
    class Actions(BaseModel):
        PumpSetMode: Optional[Dict[str, str]] = Field(default=None, alias="#Pump.SetMode")
        Oem: Optional[Dict[str, Any]] = Field(default=None)
        
    Odata_context: Optional[str] = Field(default=None, alias="@odata.context")
    Odata_etag: Optional[str] = Field(default=None, alias="@odata.etag")
    # Odata_id: Optional[str] = Field(default=None, alias="@odata.id")
    # Odata_type: Optional[str] = Field(default=None, alias="@odata.type")
    Actions: Optional[Actions] = Field(default=None)
    Assembly: Optional[RfAssemblyModel] = Field(default=None)
    AssetTag: Optional[str] = Field(default=None, description="The user-assigned asset tag for this equipment.")
    Description: Optional[str] = Field(default=None)
    Filters: Optional[RfFilterCollectionModel] = Field(default=None)
    FirmwareVersion: Optional[str] = Field(default=None)
    # Id: Optional[str] = Field(default=None)
    InletPressurekPa: Optional[RfSensorExcerpt] = Field(default=None, description="The inlet pressure (kPa).", extra={"unit": "kPa"})
    Location: Optional[RfLocationModel] = Field(default=None)
    LocationIndicatorActive: Optional[bool] = Field(default=None)
    Manufacturer: Optional[str] = Field(default=None)
    Model: Optional[str] = Field(default=None, description="The model number for this pump.")
    # Name: Optional[str] = Field(default=None)
    Oem: Optional[RfOemModel] = Field(default=None)
    PartNumber: Optional[str] = Field(default=None)
    PhysicalContext: Optional[RfPhysicalContext] = Field(default=None)
    ProductionDate: Optional[str] = Field(default=None)
    PumpSpeedPercent: Optional[RfSensorPumpExcerpt] = Field(default=None, description="The pump speed (%).")
    PumpType: Optional[RfPumpType] = Field(default=None)
    SerialNumber: Optional[str] = Field(default=None)
    ServiceHours: Optional[int] = Field(default=None, description="The hours of service this pump has provided.")
    SparePartNumber: Optional[str] = Field(default=None, description="The spare part number for this pump.")
    SpeedControlPercent: Optional[RfControlSingleLoopExcerptModel] = Field(default=None, description="The speed control percentage.")
    Status: Optional[RfStatusModel] = Field(default=None)
    UserLabel: Optional[str] = Field(default=None, description="A user-assigned label.")
    Version: Optional[str] = Field(default=None, description="The hardware version of this equipment.")


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



    