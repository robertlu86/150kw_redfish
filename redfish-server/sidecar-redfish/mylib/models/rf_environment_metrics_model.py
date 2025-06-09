
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

from mylib.models.rf_base_model import RfResourceBaseModel


class RfEnvironmentMetricsModel(RfResourceBaseModel):
    Id: str = Field(default="EnvironmentMetrics")
    odata_context: str = Field(
        default="/redfish/v1/$metadata#EnvironmentMetrics.v1_3_2.EnvironmentMetrics", 
        alias="@odata.context"
    )
    Description: Optional[str] = Field(default="Environmental Metrics of the Coolant Distribution Unit (CDU)")

    # 溫度（Celsius）
    TemperatureCelsius: Optional[dict] = Field(default={
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/TemperatureCelsius",
        "Reading": 0.0
    })
    # 露點（Celsius）
    DewPointCelsius: Optional[dict] = Field(default={
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/DewPointCelsius",
        "Reading": 0.0
    })
    # 相對濕度（百分比）
    HumidityPercent: Optional[dict] = Field(default={
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/HumidityPercent",
        "Reading": 0.0
    })
    # 絕對濕度（克／立方米)
    AbsoluteHumidity: Optional[dict] = Field(default={
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/AbsoluteHumidity",
        "Reading": "Null"
    })

    EnergykWh: Optional[dict] = Field(default={
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/EnergykWh",
        "Reading": 0.0
    })
    PowerWatts: Optional[dict] = Field(default={
        "DataSourceUri": "/redfish/v1/Chassis/1/Sensors/PowerConsume",
        "Reading": 0.0
    })

    Oem: Optional[dict] = Field(default={})
    
    model_config = ConfigDict(
        extra='allow',
    )

    def __init__(self, cdu_id: str, **kwargs):
        """
        Example:
        {
            "@odata.id": "/redfish/v1/ThermalEquipment/CDUs/1/EnvironmentMetrics",
            "@odata.type": "#EnvironmentMetrics.v1_3_2.EnvironmentMetrics",
            "@odata.context": "/redfish/v1/$metadata#EnvironmentMetrics.v1_3_2.EnvironmentMetrics",
        }
        """
        super().__init__(**kwargs)
        self.odata_id = f"/redfish/v1/ThermalEquipment/CDUs/{cdu_id}/EnvironmentMetrics"
        self.odata_type = "#EnvironmentMetrics.v1_3_2.EnvironmentMetrics"
        self.Name = "CDU Environment Metrics"






    