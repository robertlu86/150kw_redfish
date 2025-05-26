
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







class RfHeaterCollectionModel(RfResourceCollectionBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/HeaterCollection.json#/definitions/HeaterCollection
    """
    # 所有欄位都同 RfResourceCollectionBaseModel 
    pass

