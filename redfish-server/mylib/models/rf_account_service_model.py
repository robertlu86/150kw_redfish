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
    MinPasswordLength: Optional[int] = Field(default=None, gt=0, le=50) # Must be less than or equal to 50
    MaxPasswordLength: Optional[int] = Field(default=None, gt=0, le=50) # Must be less than or equal to 50
    AccountLockoutThreshold: Optional[int] = Field(default=None,ge=0,le=5) # If 0 , the account is never locked.
    AccountLockoutDuration: Optional[int] = Field(default=None,ge=0,le=1800) # In seconde,  if this value is 0 , no lockout will occur.
    AccountLockoutCounterResetAfter: Optional[int] = Field(default=None,ge=0,le=1800) # In seconds, must <= AccountLockoutDuration.
    
    


    def save_to_settings(self):
        """
        Save each field of RfAccountServiceModel to SettingModel with the corresponding key.
        """
        for key, value in self.model_dump(exclude_none=True).items():
            namespaced_key = f"AccountService.{key}"
            
            if SettingModel.save_key_value(namespaced_key, value) == False:
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
    
    
class RfAccountServiceUpdateModel(RfAccountServiceModel):
    
    @classmethod
    def check_field_high_low(cls, values: Dict[str, Any], high_field_name: str, low_field_name: str, compare: str = "gt"):

        if high_field_name not in values and low_field_name not in values:
            return
        high_value = low_value = 0
        
        if high_field_name in values:
            high_value = values[high_field_name]
        else:
            setting_key = f"AccountService.{high_field_name}"
            high_value = int(SettingModel.get_by_key(setting_key).value)
        
        if low_field_name in values:
            low_value = values[low_field_name]
        else:
            setting_key = f"AccountService.{low_field_name}"
            low_value = int(SettingModel.get_by_key(setting_key).value)
        
        if compare == "gt" and low_value >= high_value:
            raise ValueError(f"{low_field_name} must be less than {high_field_name}.")
        elif compare == "ge" and low_value > high_value:
            raise ValueError(f"{low_field_name} must be less than or equal to {high_field_name}.")
        return
    
    @model_validator(mode='before')
    def validate_fields(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # get model valid fields from schema
        schema = cls.model_json_schema()
        valid_fields = set(schema.get('properties', {}).keys())
        
        provided_keys = set(values.keys())
        
        valid_provided_keys = provided_keys.intersection(valid_fields)
        
        print(f"Valid provided keys: {valid_provided_keys}")
        
        # if no valid provided keys, raise an error
        if not valid_provided_keys:
            raise ValueError(f"None of the provided fields {list(provided_keys)} match valid fields: {list(valid_fields)}")
        
        # Other validations
        cls.check_field_high_low(values, 'MaxPasswordLength', 'MinPasswordLength', compare="ge")
        cls.check_field_high_low(values, 'AccountLockoutDuration', 'AccountLockoutCounterResetAfter', compare="ge")
        if values.get('MinPasswordLength') and values.get('MaxPasswordLength'):
            if values['MinPasswordLength'] > values['MaxPasswordLength']:
                raise ValueError("MinPasswordLength must be less than or equal to MaxPasswordLength.")
        return values