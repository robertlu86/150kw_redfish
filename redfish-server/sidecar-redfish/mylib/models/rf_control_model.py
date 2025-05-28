from typing import Optional
from pydantic import (
    BaseModel,
    Field,
    validator, # deprecated
    field_validator,
)
from enum import Enum


        
class RfControlLoop(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Control.v1_6_0.json#/definitions/ControlLoop
    """
    CoefficientUpdateTime: Optional[str] = Field(default=None, description="The date and time that the control loop coefficients were changed.")
    Differential: Optional[float] = Field(default=None, description="The differential coefficient.")
    Integral: Optional[float] = Field(default=None, description="The integral coefficient.")
    Proportional: Optional[float] = Field(default=None, description="The proportional coefficient.")

class RfControlMode(str, Enum):
    """
    @see https://redfish.dmtf.org/schemas/v1/Control.v1_6_0.json#/definitions/ControlMode
    """
    Automatic = "Automatic"
    Override = "Override"
    Manual = "Manual"
    Disabled = "Disabled"

class RfControlSingleLoopExcerptModel(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Control.v1_6_0.json#/definitions/ControlSingleLoopExcerpt
    """
    AllowableMax: Optional[float] = Field(default=None)
    AllowableMin: Optional[float] = Field(default=None)
    ControlLoop: Optional[RfControlLoop] = Field(default=None, description="The control loop details.")
    ControlMode: Optional[RfControlMode] = Field(default=None)
    DataSourceUri: Optional[str] = Field(default=None)
    Reading: Optional[float] = Field(default=None)
    ReadingUnits: Optional[str] = Field(default=None)
    SetPoint: Optional[float] = Field(default=None, description="The desired set point of the control.")
                
