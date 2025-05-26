'''
@see https://redfish.dmtf.org/schemas/v1/PowerSupplyMetrics.v1_1_2.json
'''
from typing import *
from pydantic import (
    BaseModel,
    Field,
    validator, # deprecated
    field_validator,
)
from enum import Enum
from typing import Dict, Any
from pydantic import ConfigDict
from mylib.models.rf_sensor_model import (
    SensorEnergykWhExcerpt, 
    SensorFanArrayExcerpt, 
    SensorFanExcerpt,
    SensorExcerpt,
    SensorCurrentExcerpt,
    SensorPowerExcerpt,
    SensorVoltageExcerpt
)
from mylib.models.rf_status_model import RfStatusModel



        
class RfPowerSupplyMetricsModel(RfResourceBaseModel):
    
    class Actions(BaseModel):
        PowerSupplyMetrics_ResetMetrics: Optional[str] = Field(default=None, alias="#PowerSupplyMetrics.ResetMetrics")
        Oem: Optional[Dict[str, Any]] = Field(default=None)


    """
    @see https://redfish.dmtf.org/schemas/v1/PowerSupplyMetrics.v1_1_2.json#/definitions/PowerSupplyMetrics
    @note
        required: [
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
    Actions: Optional[Actions] = Field(default=None)
    Description: Optional[str] = Field(default=None)
    EnergykWh: Optional[SensorEnergykWhExcerpt] = Field(default=None)
    FanSpeedPercent: Optional[SensorFanExcerpt] = Field(default=None)
    FanSpeedsPercent: Optional[List[SensorFanArrayExcerpt]] = Field(default=None)
    FanSpeedsPercent_odata_count: Optional[int] = Field(default=None, alias="FanSpeedsPercent@odata.count")
    FrequencyHz: Optional[SensorExcerpt] = Field(default=None)
    # "Id": {2 items},
    InputCurrentAmps: Optional[SensorCurrentExcerpt] = Field(default=None)
    InputPowerWatts: Optional[SensorPowerExcerpt] = Field(default=None)
    InputVoltage: Optional[SensorVoltageExcerpt] = Field(default=None)
    # "Name": {2 items},
    Oem: Optional[Dict] = Field(default=None)
    OutputPowerWatts: Optional[SensorPowerExcerpt] = Field(default=None)
    RailCurrentAmps: Optional[SensorCurrentExcerpt] = Field(default=None)
    RailCurrentAmps_odata_count: Optional[int] = Field(default=None, alias="RailCurrentAmps@odata.count")
    RailPowerWatts: Optional[SensorPowerExcerpt] = Field(default=None)
    RailPowerWatts_odata_count:  Optional[int] = Field(default=None, alias="RailPowerWatts@odata.count")
    RailVoltage: Optional[SensorVoltageExcerpt] = Field(default=None)
    RailVoltage_odata_count:  Optional[int] = Field(default=None, alias="RailVoltage@odata.count")
    Status: Optional[RfStatusModel] = Field(default=None)
    TemperatureCelsius: Optional[SensorExcerpt] = Field(default=None)


                
