import os
from typing import Optional, List, Dict, Any
from pydantic import (
    BaseModel,
    Field, 
    computed_field,
    model_validator,
    #validator, # deprecated
    field_validator,
)
from mylib.models.rf_base_model import RfResourceCollectionBaseModel







class RfPumpCollectionModel(RfResourceCollectionBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/PumpCollection.json#/definitions/PumpCollection

    
    "Members@odata.count": 3,
    "Members": [
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/1"
        },
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/2"
        },
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps/3"
        }
    ],
    """

    Members_odata_count: int = Field(
        default_factory=lambda: int(os.getenv("REDFISH_PUMP_COLLECTION_CNT", "0")),
        alias="Members@odata.count"
    )
    Members: List[Dict[str, Any]] = Field(default=[], description="")
    # 所有欄位都同 RfResourceCollectionBaseModel 
    def __init__(self, cdu_id: str, **kwargs):
        """
        Example:
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/Pumps",
            "@odata.type": "#PumpCollection.PumpCollection",
            "Name": "Cooling Pump Collection",
        }
        """
        super().__init__(**kwargs)
        self.odata_id = f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Pumps"
        self.odata_type = "#PumpCollection.PumpCollection"
        member_cnt = int(os.environ.get('REDFISH_PUMP_COLLECTION_CNT', 0))
        for i in range(member_cnt):
            self.Members.append({  "@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/Pumps/{i+1}"})
        self.Name = "Cooling Pump Collection"
