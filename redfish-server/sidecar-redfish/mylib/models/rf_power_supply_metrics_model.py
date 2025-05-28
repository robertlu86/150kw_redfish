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
    RfSensorEnergykWhExcerpt, 
    RfSensorFanArrayExcerpt, 
    RfSensorFanExcerpt,
    RfSensorExcerpt,
    RfSensorCurrentExcerpt,
    RfSensorPowerExcerpt,
    RfSensorVoltageExcerpt
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
    EnergykWh: Optional[RfSensorEnergykWhExcerpt] = Field(default=None)
    FanSpeedPercent: Optional[RfSensorFanExcerpt] = Field(default=None)
    FanSpeedsPercent: Optional[List[RfSensorFanArrayExcerpt]] = Field(default=None)
    FanSpeedsPercent_odata_count: Optional[int] = Field(default=None, alias="FanSpeedsPercent@odata.count")
    FrequencyHz: Optional[RfSensorExcerpt] = Field(default=None)
    # "Id": {2 items},
    InputCurrentAmps: Optional[RfSensorCurrentExcerpt] = Field(default=None)
    InputPowerWatts: Optional[RfSensorPowerExcerpt] = Field(default=None)
    InputVoltage: Optional[RfSensorVoltageExcerpt] = Field(default=None)
    # "Name": {2 items},
    Oem: Optional[Dict] = Field(default=None)
    OutputPowerWatts: Optional[RfSensorPowerExcerpt] = Field(default=None)
    RailCurrentAmps: Optional[RfSensorCurrentExcerpt] = Field(default=None)
    RailCurrentAmps_odata_count: Optional[int] = Field(default=None, alias="RailCurrentAmps@odata.count")
    RailPowerWatts: Optional[RfSensorPowerExcerpt] = Field(default=None)
    RailPowerWatts_odata_count:  Optional[int] = Field(default=None, alias="RailPowerWatts@odata.count")
    RailVoltage: Optional[RfSensorVoltageExcerpt] = Field(default=None)
    RailVoltage_odata_count:  Optional[int] = Field(default=None, alias="RailVoltage@odata.count")
    Status: Optional[RfStatusModel] = Field(default=None)
    TemperatureCelsius: Optional[RfSensorExcerpt] = Field(default=None)


                
