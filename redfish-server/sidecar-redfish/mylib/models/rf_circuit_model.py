from typing import Literal
from pydantic import (
    BaseModel,
    Field,
    validator, # deprecated
    field_validator,
)
from enum import Enum


        

class RfNominalVoltageType(str, Enum):
    """
    @see https://redfish.dmtf.org/schemas/v1/Circuit.json#/definitions/NominalVoltageType
    """
    AC100To127V = "AC100To127V"
    AC100To240V = "AC100To240V"
    AC100To277V = "AC100To277V"
    AC120V = "AC120V"
    AC200To240V = "AC200To240V"
    AC200To277V = "AC200To277V"
    AC208V = "AC208V"
    AC230V = "AC230V"
    AC240V = "AC240V"
    AC240AndDC380V = "AC240AndDC380V"
    AC277V = "AC277V"
    AC277AndDC380V = "AC277AndDC380V"
    AC400V = "AC400V"
    AC480V = "AC480V"
    DC48V = "DC48V"
    DC240V = "DC240V"
    DC380V = "DC380V"
    DCNeg48V = "DCNeg48V"
    DC16V = "DC16V"
    DC12V = "DC12V"
    DC9V = "DC9V"
    DC5V = "DC5V"
    DC3_3V = "DC3_3V"
    DC1_8V = "DC1_8V"

class RfCircuitModel(BaseModel):
    pass
                
