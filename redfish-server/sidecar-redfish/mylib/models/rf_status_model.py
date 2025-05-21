from typing import Literal
from pydantic import (
    BaseModel,
    Field,
    validator, # deprecated
    field_validator,
)
from enum import Enum

class RfStatusHealth(str, Enum):
    OK = "OK"
    Warning = "Warning"
    Critical = "Critical"

    @classmethod
    def numeric_map(cls) -> dict:
        return {
            "OK":       1 << 0,
            "Warning":  1 << 1,
            "Critical": 1 << 2,
        }
        

class RfStatusState(str, Enum):
    Absent = "Absent"
    Deferred = "Deferred"
    Disabled = "Disabled"
    Enabled = "Enabled"
    InTest = "InTest"
    Qualified = "Qualified"
    Quiesced = "Quiesced"
    StandbyOffline = "StandbyOffline"
    StandbySpare = "StandbySpare"
    Starting = "Starting"
    UnavailableOffline = "UnavailableOffline"
    Updating = "Updating"

class RfStatusModel(BaseModel):
    """
    Health
    @see https://www.dmtf.org/sites/default/files/standards/documents/DSP2046_2023.1.pdf Section 4.16
    +--------+---------------------------------------------------+
    |string  | Description                                       |
    +--------+---------------------------------------------------+
    |Critical| A critical condition requires immediate attention.|
    |OK      | Normal.                                           |
    |Warning | A condition requires attention.                   |
    +--------+---------------------------------------------------+
    """
    Health: RfStatusHealth = Field(default=RfStatusHealth.OK, description="")
    
    """
    State
    @see https://www.dmtf.org/sites/default/files/standards/documents/DSP2046_2023.1.pdf Section 4.16.3.4
    +------------------+---------------------------------------------------+
    |string            | Description                                       |
    +------------------+---------------------------------------------------+
    |Absent            | This function or device is not currently ...      |
    |Deferred          | The element does not process any commands ...     |
    |Disabled          | This function or resource is disabled.            |
    |Enabled           | This function or resource is enabled.             |
    |InTest            | This function or resource is undergoing ...       |
    |Qualified         | The element quality is within the acceptable ...  |
    |Quiesced          | The element is enabled but only processes a ...   |
    |StandbyOffline    | This function or resource is enabled but ...      |
    |StandbySpare      | This function or resource is part of a ...        |
    |Starting          | This function or resource is starting.            |
    |UnavailableOffline| This function or resource is present ...          |
    |Updating          | The element is updating and might be ...          |
    +------------------+---------------------------------------------------+
    """
    State: RfStatusState = Field(default=RfStatusState.Enabled, description="")
    

    @classmethod
    def from_dict(cls, status_dict: dict):
        health = status_dict.get("Health") or status_dict.get("health")
        state = status_dict.get("State") or status_dict.get("state")
        return cls(Health=health, State=state)



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
                
    def numeric_health_value(self) -> int:
        hashmap = RfStatusHealth.numeric_map()
        return hashmap[self.Health.value]