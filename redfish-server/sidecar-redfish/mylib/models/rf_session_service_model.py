from mylib.models.rf_base_model import RfResourceBaseModel
from typing import Optional, Dict, Any
from pydantic import (
    BaseModel,
    ConfigDict,
    Field, 
    computed_field,
    model_validator,
    #validator, # deprecated
    field_validator,
)
from mylib.models.setting_model import SettingModel

class RfSessionServiceModel(BaseModel):
    #Base on DSP2046
    SessionTimeout: Optional[int] = Field(default=None,ge=30,le=86400)  # In seconds, must be between 30 and 86400 (24 hours)
   
