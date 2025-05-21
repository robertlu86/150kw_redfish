
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







class RfCoolantConnectorCollectionModel(RfResourceCollectionBaseModel):
    """
    @see https://www.dmtf.org/sites/default/files/standards/documents/DSP0266_1.22.0.html#resource-collections
    """
    # 所有欄位都同 RfResourceCollectionBaseModel 
    pass

