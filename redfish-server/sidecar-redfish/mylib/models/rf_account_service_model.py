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

class RfAccountServiceModel(BaseModel):
    #Base on DSP2046
    AuthFailureLoggingThreshold: Optional[int] = Field(default=None,gt=0)
    MinPasswordLength: Optional[int] = Field(default=None,gt=0)
    AccountLockoutThreshold: Optional[int] = Field(default=None,ge=0,) # If 0 , the account is never locked.
    AccountLockoutDuration: Optional[int] = Field(default=None,ge=0) # In seconde,  if this value is 0 , no lockout will occur.
    AccountLockoutCounterResetAfter: Optional[int] = Field(default=None,gt=0) # In seconds, must <= AccountLockoutDuration.
    
    def save_to_settings(self):
        """
        Save each field of RfAccountServiceModel to SettingModel with the corresponding key.
        """
        for key, value in self.model_dump(exclude_none=True).items():
            namespaced_key = f"AccountService.{key}"
            
            if SettingModel.update_by_key_value(namespaced_key, value) == False:
                return False
        return True
    
    @classmethod
    def fetch_from_settings(cls):
        """
        Fetch each field of RfAccountServiceModel from SettingModel with the corresponding key.
        """
        values: dict[str, Any] = {}

        for field_name in cls.model_fields.keys():
            setting_key = f"AccountService.{field_name}"
            setting = SettingModel.get_by_key(setting_key)
            if setting:
                values[field_name] = setting.value
        return cls(**values)
