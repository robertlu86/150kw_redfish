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
    field_serializer,
)

from mylib.models.rf_status_model import RfStatusModel
from mylib.models.rf_base_model import RfResourceBaseModel, RfResourceCollectionBaseModel
from mylib.models.rf_physical_context_model import RfPhysicalContext, RfPhysicalSubContext



class MySensorBaseExcerpt(BaseModel):
    """
    Impl. field_serializer for `Reading`
    @note 
        Not redfish defined. So the class name start with `My`, not `Rf`.
    """
    @field_serializer('Reading', check_fields=False)
    def serialize_reading(cls, value):
        if value is None:
            return None
        if isinstance(value, float):
            decimal_places = int(os.getenv("DECIMAL_PLACES", 2)) # 小數點精確位數
            return round(value, decimal_places)
        elif isinstance(value, int):
            return int(value)
        else:
            return value

class RfSensorVoltageExcerpt(BaseModel): # 完全同 SensorCurrentExcerpt，但仍定義一個
    """
    @see https://redfish.dmtf.org/schemas/v1/Sensor.v1_9_1.json#/definitions/SensorVoltageExcerpt
    """
    CrestFactor: Optional[int] = Field(
        default=None, 
        description="The crest factor for this sensor.",
        extra={
            "longDescription": "This property shall contain the ratio of the peak measurement divided by the RMS measurement and calculated over same N line cycles. A sine wave would have a value of 1.414."
        }
    )
    DataSourceUri: Optional[str] = Field(default=None)
    Reading: Optional[float] = Field(default=None)
    THDPercent: Optional[int] = Field(
        default=None, 
        description="The total harmonic distortion percent (% THD).", 
        extra={
            "minimum": 0,
            "units": "%", 
            "longDescription": "This property shall contain the total harmonic distortion of the `Reading` property in percent units, typically `0` to `100`."
        }
    )

class RfSensorPowerExcerpt(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Sensor.v1_9_1.json#/definitions/SensorPowerExcerpt
    """
    ApparentVA: Optional[int] = Field(
        default=None, 
        description="The product of voltage and current for an AC circuit, in volt-ampere units.",
        extra={
            "units": "V.A",
            "longDescription": "This property shall contain the product of voltage (RMS) multiplied by current (RMS) for a circuit. This property can appear in sensors of the `Power` `ReadingType`, and shall not appear in sensors of other `ReadingType` values."
        }
    )
    DataSourceUri: Optional[str] = Field(default=None)
    PhaseAngleDegrees: Optional[int] = Field(
        default=None, 
        description="The phase angle (degrees) between the current and voltage waveforms.",
        extra={
            "maximum": 90,
            "minimum": -90,
            "longDescription": "This property shall contain the phase angle, in degree units, between the current and voltage waveforms for an electrical measurement. This property can appear in sensors with a `ReadingType` containing `Power`, and shall not appear in sensors with other `ReadingType` values."
        }
    )
    PowerFactor: Optional[int] = Field(
        default=None, 
        description="The power factor for this sensor.",
        extra={
            "maximum": 1,
            "minimum": -1,
            "longDescription": "This property shall identify the quotient of real power (W) and apparent power (VA) for a circuit. `PowerFactor` is expressed in unit-less 1/100ths. This property can appear in sensors containing a `ReadingType` value of `Power`, and shall not appear in sensors of other `ReadingType` values."
        }
    )
    ReactiveVAR: Optional[int] = Field(
        default=None, 
        description="The square root of the difference term of squared apparent VA and squared power (Reading) for a circuit, in VAR units.",
        extra={
            "units": "V.A",
            "longDescription": "This property shall contain the arithmetic mean of product terms of instantaneous voltage and quadrature current measurements calculated over an integer number of line cycles for a circuit. This property can appear in sensors of the `Power` `ReadingType`, and shall not appear in sensors of other `ReadingType` values."
        }
    )
    Reading: Optional[float] = Field(default=None)

class RfSensorPumpExcerpt(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Sensor.v1_9_1.json#/definitions/SensorPumpExcerpt
    """
    DataSourceUri: Optional[str] = Field(default=None)
    Reading: Optional[float] = Field(default=None)
    SpeedRPM: Optional[float] = Field(default=None, extra={"units": "{rev}/min"}) # yes: {rev} is constant str, not variable
    

class RfSensorCurrentExcerpt(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Sensor.v1_9_1.json#/definitions/SensorCurrentExcerpt
    """
    CrestFactor: Optional[int] = Field(
        default=None, 
        description="The crest factor for this sensor.",
        extra={
            "longDescription": "(This property shall contain the ratio of the peak measurement divided by the RMS measurement and calculated over same N line cycles. A sine wave would have a value of 1.414.)"
        }
    )
    DataSourceUri: Optional[str] = Field(default=None)
    Reading: Optional[float] = Field(default=None)
    THDPercent: Optional[int] = Field(
        default=None, 
        description="The total harmonic distortion percent (% THD).", 
        extra={
            "minimum": 0,
            "units": "%", 
            "longDescription": "This property shall contain the total harmonic distortion of the `Reading` property in percent units, typically `0` to `100`."
        }
    )

class RfSensorFanArrayExcerpt(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Sensor.v1_9_1.json#/definitions/SensorFanArrayExcerpt
    """
    DataSourceUri: Optional[str] = Field(default=None)
    DeviceName: Optional[str] = Field(default=None)
    PhysicalContext: Optional[RfPhysicalContext] = Field(default=None)
    PhysicalSubContext: Optional[RfPhysicalSubContext] = Field(default=None)
    Reading: Optional[float] = Field(default=None)
    SpeedRPM: Optional[float] = Field(default=None, extra={"units": "{rev}/min"}) # yes: {rev} is constant str, not variable


class RfSensorExcerpt(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Sensor.v1_9_1.json#/definitions/SensorExcerpt
    """
    DataSourceUri: Optional[str] = Field(default=None)
    Reading: Optional[float] = Field(default=None)
    

class RfSensorFanExcerpt(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Sensor.v1_9_1.json#/definitions/SensorFanExcerpt
    """
    DataSourceUri: Optional[str] = Field(default=None)
    Reading: Optional[float] = Field(default=None)
    SpeedRPM: Optional[float] = Field(default=None, extra={"units": "{rev}/min"}) # yes: {rev} is constant str, not variable
    

class RfSensorEnergykWhExcerpt(BaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Sensor.v1_9_1.json#/definitions/SensorEnergykWhExcerpt
    """
    ApparentkVAh: Optional[float] = Field(default=None, extra={"units": "kV.A.h",})
    DataSourceUri: Optional[str] = Field(default=None)
    LifetimeReading: Optional[float] = Field(default=None)
    ReactivekVARh: Optional[float] = Field(default=None, extra={"units": "kV.A.h"})
    Reading: Optional[float] = Field(default=None)
    SensorResetTime: Optional[str] = Field(default=None)
    

class RfSensorCollectionModel(RfResourceCollectionBaseModel):
    odata_type: str   = Field(default="#SensorCollection.SensorCollection", alias="@odata.type")
    Name: str         = Field(default="Sensor Collection")
    Members_odata_count: int      = Field(default=0, alias="Members@odata.count")
    Members: List[Dict[str, Any]] = Field(default=[], description='[{"@odata.id": "/redfish/v1/Chassis/1/Sensors/PrimaryFlowLitersPerMinute"}, ...]')
    Oem: Dict[str, Any]           = Field(default={})
    odata_id: Optional[str]       = Field(default=None, alias="@odata.id", description="/redfish/v1/Chassis/<chassis_id>/Sensors")

    def build_odata_id(self, chassis_id: str):
        return f"/redfish/v1/Chassis/{chassis_id}/Sensors"


class RfSensorModel(RfResourceBaseModel):
    '''
    @note properties 67 items
    '''
    odata_type: str   = Field(default="#Sensor.v1_1_0.Sensor", alias="@odata.type")
    Id: str           = Field(default="", description="ex: PrimaryFlowLitersPerMinute|PrimaryHeatRemovedkW|..., 會放到odata_id的最後一層")
    Name: str         = Field(default="")
    Reading: float    = Field(default=0.0, description="ex: 23.5")
    ReadingUnits: str = Field(default="", description="ex: L/min, kW, kPa, ...")
    odata_id: Optional[str]         = Field(default=None, alias="@odata.id", description="")
    Status: Optional[RfStatusModel]   = None
    Oem: Dict[str, Any] = None

    model_config = ConfigDict(
        extra='allow',
        exclude_none=True # 排除 None 的值
    )

    def build_odata_id(self, chassis_id: str):
        return f"/redfish/v1/Chassis/{chassis_id}/Sensors/{self.Id}"

    @model_validator(mode='after')
    def _set_odata_id(self, **kwargs):
        """
        @see https://docs.pydantic.dev/latest/concepts/validators/#model-validators
        """
        # chassis_id = values.get('chassis_id')
        # values['@odata.id'] = f"/redfish/v1/Chassis/{chassis_id}/Sensors/{self.Id}"
        chassis_id = self.__pydantic_extra__.get('chassis_id')
        self.odata_id = f"/redfish/v1/Chassis/{chassis_id}/Sensors/{self.Id}"
        return self


    # @computed_field
    # @property
    # def odata_id(self) -> str:
    #     # chassis_id = self.__pydantic_extra__['chassis_id']
    #     chassis_id = self.chassis_id
    #     return f"/redfish/v1/Chassis/{chassis_id}/Sensors/{self.Id}"
    
