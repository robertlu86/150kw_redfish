
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

from mylib.models.rf_base_model import RfResourceBaseModel
from mylib.models.rf_status_model import RfStatusModel, RfStatusHealth, RfStatusState

class RfLeakDetectorModel(RfResourceBaseModel):
    # Id: str = Field(default="1")
    # Status: RfStatusModel = Field(default=RfStatusModel())
    
    
    model_config = ConfigDict(
        extra='allow',
    )

    def __init__(self, cdu_id: str, **kwargs):
        """
        Example:
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/LeakDetection/LeakDetectors",
            "@odata.type": "#LeakDetectors.v1_6_0.LeakDetectors",
            "Id": f"{cdu_id}",
            "Name": "LeakDetectors",
            "Status": {
                "State": "Enabled",
                "Health": "Critical"
            }
        }
        """
        super().__init__(**kwargs)
        self.odata_id = f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/LeakDetection/LeakDetectors"
        self.odata_type = "#LeakDetectorCollection.LeakDetectorCollection"
        self.Name = "LeakDetectors"
        # self.Id = cdu_id






    