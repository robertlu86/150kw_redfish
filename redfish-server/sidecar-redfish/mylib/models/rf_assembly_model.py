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

from mylib.models.rf_base_model import RfResourceBaseModel, RfResourceCollectionBaseModel
from mylib.models.rf_status_model import RfStatusModel
from mylib.models.rf_resource_model import RfOemModel, RfLocationModel
from mylib.models.rf_physical_context_model import RfPhysicalContext, RfPhysicalSubContext

class RfAssembliesModel(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Assembly.v1_5_1.json#/definitions/AssemblyData
    @note: 
        "required": [
            "@odata.id",
            "MemberId"
        ]
    """
    model_config = ConfigDict(
        arbitrary_types_allowed=True # for Oem
    )


    # required
    odata_id: str = Field(alias="@odata.id")

    Actions: Optional[dict[str, Any]] = Field(default=None)
    BinaryDataURI: Optional[str] = Field(default=None)
    Description: Optional[str] = Field(default=None)
    EngineeringChangeLevel: Optional[str] = Field(default=None)
    ISOCountryCodeOfOrigin: Optional[str] = Field(default=None)
    Location: Optional[RfLocationModel] = None
    LocationIndicatorActive: Optional[bool] = Field(default=None)
    
    # required
    MemberId: str = Field(description="The unique identifier for the member within an array.")

    Model: Optional[str] = Field(default=None, description="The model number of the assembly.")
    Name: Optional[str] = Field(default=None)
    Oem: RfOemModel = Field(default=None)
    PartNumber: Optional[str] = Field(default=None)
    PhysicalContext: Optional[RfPhysicalContext] = Field(default=None)
    Producer: Optional[str] = Field(default=None)
    ProductionDate: Optional[str] = Field(default=None)
    Replaceable: Optional[bool] = Field(default=None)
    SKU: Optional[str] = Field(default=None)
    SerialNumber: Optional[str] = Field(default=None)
    SparePartNumber: Optional[str] = Field(default=None)
    Status: Optional[RfStatusModel] = None
    Vendor: Optional[str] = Field(default=None)
    Version: Optional[str] = Field(default=None)


class RfAssemblyModel(RfResourceBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Assembly.v1_5_1.json#/definitions/Assembly
    @note: 
        "required": [
            "@odata.id",
            "@odata.type",
            "Id",
            "Name"
        ]
    """
    odata_context: Optional[str] = Field(default=None, alias="@odata.context")
    odata_etag: Optional[str] = Field(default=None, alias="@odata.etag")
    # "@odata.id": {1 item},
    # "@odata.type": {1 item},
    Actions: Optional[Dict[str, Any]] = Field(default=None)
    Assemblies: Optional[List[RfAssembliesModel]] = Field(default=None)
    Assemblies_odata_count: Optional[int] = Field(default=None, alias="Assemblies@odata.count")
    Description: Optional[str] = Field(default=None)
    # "Id": {2 items},
    # "Name": {2 items},
    Oem: Optional[Dict[str, Any]] = Field(default=None)








    