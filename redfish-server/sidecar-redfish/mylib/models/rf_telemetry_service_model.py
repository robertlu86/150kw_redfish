from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import (
    BaseModel,
    Field, 
    computed_field,
    model_validator,
    #validator, # deprecated
    field_validator,
)
from mylib.models.rf_base_model import RfResourceBaseModel, RfResourceCollectionBaseModel




class RfTelemetryServiceModel(RfResourceBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/TelemetryService.v1_4_0.json#/definitions/TelemetryService
    @note properties 22 items
    @note 
        required: [
            "@odata.id",
            "@odata.type",
            "Id",
            "Name"
        ]
    """
    ...

