from typing import Optional, Dict, Any, List
from pydantic import (
    BaseModel,
    Field,
    validator, # deprecated
    field_validator,
)
from enum import Enum
from mylib.models.rf_status_model import RfStatusModel
from mylib.models.rf_resource_model import RfResourceModel


class RfRedundancyType(Enum):
    Failover     = "Failover"
    NPlusM       = "NPlusM"
    Sharing      = "Sharing"
    Sparing      = "Sparing"
    NotRedundant = "NotRedundant"

class RfRedundancyMode(Enum):
    """
    @see https://www.dmtf.org/sites/default/files/standards/documents/DSP0268_2024.1.pdf Section 4.12.3.1 
    """
    Failover        = (0, "Failover")
    NPlusM          = (1, "N+m")
    NotRedundant    = (2, "NotRedundant")
    Sharing         = (3, "Sharing")
    Sparing         = (4, "Sparing")

    def __init__(self, code: int, name: str):
        self._code = code
        self._name = name
    
    @property
    def code(self):
        return self._code
    
    @property
    def name(self):
        return self._name
    



class RfRedundancyModel(BaseModel):
    """
    Health
    @see https://www.dmtf.org/sites/default/files/standards/documents/DSP0268_2024.1.pdf Section 4.12
    """
    odata_type: str          = Field(default=None, alias="@odata.type")
    odata_id: str            = Field(alias="@odata.id")
    Actions: Optional[Dict[str, Any]]  = Field(default={}, description="The available actions for this resource.")
    MaxNumSupported: Optional[int] = Field(default=None, description="The maximum number of members allowable for this particular redundancy group.")
    MemberId: str                  = Field(default=None, description="The unique identifier for the member within an array.")
    MinNumNeeded: int              = Field(default=None, description="The minimum number of members needed for this group to be redundant.")
    Mode: RfRedundancyMode         = Field(default=None, description="The redundancy mode of the group.")
    Name: str                      = Field(default=None, description="The name of the resource or array member.")
    Oem: Optional[Dict[str, Any]]  = Field(default=None, description="See the OEM object definition in the Using this guide clause.")
    RedundancyEnabled: bool        = Field(default=None, description="An indication of whether redundancy is enabled.")
    RedundancySet: List[Dict]      = Field(default=[], description="The links to components of this redundancy set.")
    Status: RfStatusModel          = Field(default=RfStatusModel(), description="The status and health of the resource and its subordinate or dependent resources.")
    

    def to_dict(self) -> dict:
        """
        Only dump fields that are defined in the model
        (i.e., drop None values and extra fields)
        """
        return self.model_dump(
                    by_alias=True,
                    include=set(self.__class__.model_fields.keys()),
                    exclude_none=True
                )
                

class RfRedundantGroup(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Redundancy.v1_5_0.json#/definitions/RedundantGroup
        "required": [
            "RedundancyType",
            "MinNeededInGroup",
            "Status",
            "RedundancyGroup"
        ]
    """
    GroupName: Optional[str] = Field(default=None)
    MaxSupportedInGroup: Optional[int] = Field(default=None)
    MinNeededInGroup: int = Field(default=0)
    RedundancyGroup: List[RfResourceModel] = Field(default=None)
    RedundancyGroup_odata_count: Optional[int] = Field(default=None, alias="RedundancyGroup@odata.count")
    RedundancyType: RfRedundancyType = Field(default=None)
    Status: RfStatusModel = Field(default=None)