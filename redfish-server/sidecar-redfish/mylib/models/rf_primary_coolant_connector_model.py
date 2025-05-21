
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

from mylib.models.rf_base_model import RfResourceBaseModel, RfResourceCollectionBaseModel
from mylib.models.rf_status_model import RfStatusModel

class RfPrimaryCoolantConnectorCollectionModel(RfResourceCollectionBaseModel):
    def __init__(self, cdu_id: str, **kwargs):
        super().__init__(**kwargs)
        self.odata_type = "#CoolantConnectorCollection.CoolantConnectorCollection"
        self.Name = "Primary (supply side) Cooling Loop Connection Collection"
        self.odata_id = f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/PrimaryCoolantConnectors"
        
        member_cnt = int(os.environ.get('REDFISH_PRIMARYCOOLANTCONNECTOR_COLLECTION_CNT', 0))
        for sn in range(1, member_cnt + 1):
            self.Members.append({"@odata.id": f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/PrimaryCoolantConnectors/{sn}"})
        self.Members_odata_count = member_cnt


# class RfPrimaryCoolantConnectorModel(RfResourceBaseModel):
#     Description: Optional[str] = Field(default="Primary input from facility chiller")
#     Status: Optional[RfStatusModel]   = None

#     Coolant: Optional[Dict[str, Any]] = None
#     CoolantConnectorType: Optional[str] = None
#     FlowLitersPerMinute: Optional[Dict[str, Any]] = None
#     HeatRemovedkW: Optional[Dict[str, Any]] = None
#     SupplyTemperatureCelsius: Optional[Dict[str, Any]] = None
#     ReturnTemperatureCelsius: Optional[Dict[str, Any]] = None
#     DeltaTemperatureCelsius: Optional[Dict[str, Any]] = None
#     SupplyPressurekPa: Optional[Dict[str, Any]] = None
#     ReturnPressurekPa: Optional[Dict[str, Any]] = None
#     DeltaPressurekPa: Optional[Dict[str, Any]] = None
#     Oem: Optional[Dict[str, Any]] = None

#     model_config = ConfigDict(
#         extra='allow',
#     )

#     def __init__(self, cdu_id: str, **kwargs):
#         super().__init__(**kwargs)
#         self.odata_type = "#CoolantConnector.v1_1_0.CoolantConnector"
#         self.Name = "Mains Input from Chiller"

#         # cdu_id = self.__pydantic_extra__.get('cdu_id')
#         self.odata_id = f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/PrimaryCoolantConnectors/{self.Id}"





    