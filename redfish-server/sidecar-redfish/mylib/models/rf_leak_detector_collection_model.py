
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







class RfLeakDetectorCollectionModel(RfResourceCollectionBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/LeakDetectorCollection.json#/definitions/LeakDetectorCollection
    """
    # 所有欄位都同 RfResourceCollectionBaseModel 
    pass

