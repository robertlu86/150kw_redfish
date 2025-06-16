from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import (
    BaseModel,
    Field, 
    computed_field,
    model_validator,
    #validator, # deprecated
    field_validator,
)
from mylib.models.rf_base_model import RfResourceBaseModel, RfResourceCollectionBaseModel



# Enum classes
class RfCalculable(str, Enum):
    NonCalculatable = "NonCalculatable"
    Summable = "Summable"
    NonSummable = "NonSummable"

class RfCalculationAlgorithmEnum(str, Enum):
    Average = "Average"
    Maximum = "Maximum"
    Minimum = "Minimum"

class RfImplementationType(str, Enum):
    PhysicalSensor = "PhysicalSensor"
    Calculated = "Calculated"
    Synthesized = "Synthesized"
    DigitalMeter = "DigitalMeter"

class RfMetricDataType(str, Enum):
    Boolean = "Boolean"
    DateTime = "DateTime"
    Decimal = "Decimal"
    Integer = "Integer"
    String = "String"
    Enumeration = "Enumeration"

class RfMetricType(str, Enum):
    Numeric = "Numeric"
    Discrete = "Discrete"
    Gauge = "Gauge"
    Counter = "Counter"
    Countdown = "Countdown"

# Supporting models
class RfCalculationParamsType(BaseModel):
    ResultMetric: Optional[str] = Field(default=None)
    SourceMetric: Optional[str] = Field(default=None)

class RfWildcard(BaseModel):
    Name: Optional[str] = Field(default=None)
    Values: Optional[List[Optional[str]]] = Field(default=None)

class RfOemActions(Dict[str, Any]):
    pass

class RfActions(BaseModel):
    Oem: Optional[RfOemActions] = Field(default=None)

# Main MetricDefinition model
class RfMetricDefinitionModel(RfResourceBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/MetricDefinition.v1_0_0.json
    @note properties 29 items
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
    # odata_id: Optional[str] = Field(default=None, alias="@odata.id")
    # odata_type: Optional[str] = Field(default=None, alias="@odata.type")
    Accuracy: Optional[float] = Field(default=None)
    Actions: Optional[RfActions] = Field(default=None)
    Calculable: Optional[RfCalculable] = Field(default=None)
    CalculationAlgorithm: Optional[RfCalculationAlgorithmEnum] = Field(default=None)
    CalculationParameters: Optional[List[Optional[RfCalculationParamsType]]] = Field(default=None)
    CalculationTimeInterval: Optional[str] = Field(default=None)
    Calibration: Optional[float] = Field(default=None)
    Description: Optional[str] = Field(default=None)
    DiscreteValues: Optional[List[Optional[str]]] = Field(default=None)
    Id: Optional[str] = Field(default=None)
    Implementation: Optional[RfImplementationType] = Field(default=None)
    IsLinear: Optional[bool] = Field(default=None)
    MaxReadingRange: Optional[float] = Field(default=None)
    MetricDataType: Optional[RfMetricDataType] = Field(default=None)
    MetricProperties: Optional[List[Optional[str]]] = Field(default=None)
    MetricType: Optional[RfMetricType] = Field(default=None)
    MinReadingRange: Optional[float] = Field(default=None)
    # Name: Optional[str] = Field(default=None)
    Oem: Optional[dict] = Field(default=None)  # Resource.json#/definitions/Oem
    PhysicalContext: Optional[str] = Field(default=None)  # PhysicalContext.json reference
    Precision: Optional[int] = Field(default=None)
    SensingInterval: Optional[str] = Field(default=None)
    TimestampAccuracy: Optional[str] = Field(default=None)
    Units: Optional[str] = Field(default=None)
    Wildcards: Optional[List[Optional[RfWildcard]]] = Field(default=None)
