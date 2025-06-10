from typing import Optional
from pydantic import (
    BaseModel,
    Field,
    validator, # deprecated
    field_validator,
)
from enum import Enum
from mylib.models.rf_base_model import RfResourceCollectionBaseModel

        
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

class RfControlCollectionExcerptModel(RfResourceCollectionBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Control.v1_6_0.json#/definitions/ControlSingleLoopExcerpt
    """
    
    
    def __init__(self, chassis_id: str, **kwargs):
        super().__init__(**kwargs)
        self.odata_id = f"/redfish/v1/Chassis/{chassis_id}/Controls"
        self.odata_type = "#ControlCollection.ControlCollection"
        self.odata_context = "/redfish/v1/$metadata#ControlCollection.ControlCollection"
        self.Name = "Control Collection"
        self.Description = "Contains all control interfaces for issuing commands"
        

                
