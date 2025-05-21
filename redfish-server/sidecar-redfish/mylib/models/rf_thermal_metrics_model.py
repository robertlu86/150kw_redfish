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
from enum import Enum
from mylib.models.rf_base_model import RfResourceBaseModel, RfResourceCollectionBaseModel





class RfThermalMetricsModel(RfResourceBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/ThermalMetrics.v1_3_2.json#/definitions/ThermalMetrics
    """
    # "@odata.context": {1 item},
    # "@odata.etag": {1 item},
    # # "@odata.id": {1 item},
    # # "@odata.type": {1 item},
    # "Actions": {3 items},
    # "AirFlowCubicMetersPerMinute": {6 items},
    # "DeltaPressurekPa": {6 items},
    # "Description": {2 items},
    # "EnergykWh": {5 items},
    # "HeaterSummary": {4 items},
    # # "Id": {2 items},
    # # "Name": {2 items},
    # "Oem": {3 items},
    # "PowerWatts": {5 items},
    # "TemperatureReadingsCelsius": {5 items},
    # "TemperatureReadingsCelsius@odata.count": {1 item},
    # "TemperatureSummaryCelsius": {3 items}
    pass





    