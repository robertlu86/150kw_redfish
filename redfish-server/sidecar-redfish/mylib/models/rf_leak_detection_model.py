
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
from mylib.models.rf_leak_detector_collection_model import RfLeakDetectorCollectionModel
from mylib.models.rf_status_model import RfStatusModel, RfStatusHealth, RfStatusState

class RfLeakDetectionModel(RfResourceBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/LeakDetection.v1_1_0.json#/definitions/LeakDetection
    """
    Odata_context: Optional[str] = Field(default=None, alias="@odata.context")
    Odata_etag: Optional[str] = Field(default=None, alias="@odata.etag")
    # "@odata.id": {1 item},
    # "@odata.type": {1 item},
    Actions: Optional[Dict[str, Any]] = Field(default=None)
    Description: Optional[str] = Field(default=None)
    # "Id": {2 items},
    LeakDetectorGroups: Optional[List[Dict[str, Any]]] = Field(default=None)
    LeakDetectors: Optional[Dict[str, Any]] = Field(default=None)
    # "Name": {2 items},
    Oem: Optional[Dict[str, Any]] = Field(default=None)
    Status: Optional[RfStatusModel] = Field(default=None)
    
    
    model_config = ConfigDict(
        extra='allow',
    )
    
    def __init__(self, cdu_id: str, **kwargs):
        super().__init__(**kwargs)
        self.odata_type = "#LeakDetection.v1_1_0.LeakDetection"
        self.odata_id = f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/LeakDetection"
        self.Odata_context = "/redfish/v1/$metadata#LeakDetection.v1_1_0.LeakDetection"
        
        self.Id = "LeakDetection"
        self.Name = "Leak Detection"
        self.Description = "LeakDetection"
        
        
    
    








    