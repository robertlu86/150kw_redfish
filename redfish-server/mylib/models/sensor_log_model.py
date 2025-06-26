# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional, Literal, Union, get_args
from pydantic import BaseModel, Field, field_validator

class SensorLogBaseModel(BaseModel):
    class Config:
        # Allow get value by field name or alias. 
        # Use SensorLogModel.parse_obj(your_dict) to parse row by field name or alias, NOT SensorLogModel(**your_dict)
        # allow_population_by_field_name = True # Deprecated
        validate_by_name = True 
    
    @classmethod
    def __get_redfish_type(cls, type_name):
        """
        @see https://redfish.dmtf.org/schemas/v1/MetricDefinition.v1_3_4.json#/definitions/MetricDefinition
        """
        TYPE_MAPPING = {
            "bool": "Boolean",
            "datetime": "DateTime",
            "float": "Decimal",
            "int": "Integer",
            "str": "String",
            "enum": "Enumeration"
        }
        return TYPE_MAPPING.get(type_name, 'unknown')

    @classmethod
    def __parse_field_type_name(cls, annotation):
        """
        @note: 
            get_args(typing.Optional[float]) => (<class 'float'>, <class 'NoneType'>)
        """
        if getattr(annotation, '__origin__', None) is Union:
            types = [t for t in get_args(annotation) if t is not type(None)]
            return types[0].__name__ if types else 'None'
        return annotation.__name__
    
    @classmethod
    def to_metric_definitions(cls) -> dict:
        ret = []
        for field_name, field_info in cls.model_fields.items():
            type_name = cls.__parse_field_type_name(field_info.annotation) # ex: typing.Optional[float]
            redfish_type = cls.__get_redfish_type(type_name)
            alias = field_info.alias
            extra = field_info.json_schema_extra or {} # pydantic v2 use `json_schema_extra`
            # value = getattr(cls, field_name)  # 獲取欄位值
            ret.append({
                "FieldName": field_name,
                "Alias": alias,
                # "Type": type_name,
                "MetricDataType": redfish_type,
                "Units": extra.get("units", None)
            })
        return ret

    def to_dict(self) -> dict:
        """
        Only dump fields that are defined in the model
        (i.e., drop None values and extra fields)
        """
        return self.model_dump(
                    by_alias=True,
                    include=set(self.__class__.model_fields.keys()),
                    exclude_none=True
                )

"""
依Pydantic V2的設計
每一個專案、客戶，自己定義一個model繼承SensorLogBaseModel
"""
class SensorLogModel(SensorLogBaseModel):
    """
    Sensor log model from webUI/logs/sensor/sensor_log.json
    Fields are defined based on redfish_info.yaml MetricDefinitions.
    """
    
    # Time related
    time: Optional[datetime] = Field(default=None, json_schema_extra={"units": None})
    
    # Temperature sensors
    coolant_supply_temperature: Optional[float] = Field(default=None, alias="Coolant Supply Temperature (T1)", json_schema_extra={"units": "°C"})
    coolant_supply_temperature_spare: Optional[float] = Field(default=None, alias="Coolant Supply Temperature Spare (T1sp)", json_schema_extra={"units": "°C"})
    coolant_return_temperature: Optional[float] = Field(default=None, alias="Coolant Return Temperature (T2)", json_schema_extra={"units": "°C"})
    coolant_return_temperature_spare: Optional[float] = Field(default=None, alias="Coolant Return Temperature Spare (T2sp)", json_schema_extra={"units": "°C"})
    
    # Pressure sensors
    coolant_supply_pressure: Optional[float] = Field(default=None, alias="Coolant Supply Pressure (P1)", json_schema_extra={"units": "kPa"})
    coolant_supply_pressure_spare: Optional[float] = Field(default=None, alias="Coolant Supply Pressure Spare (P1sp)", json_schema_extra={"units": "kPa"})
    coolant_return_pressure: Optional[float] = Field(default=None, alias="Coolant Return Pressure (P2)", json_schema_extra={"units": "kPa"})
    coolant_return_pressure_spare: Optional[float] = Field(default=None, alias="Coolant Return Pressure Spare (P2sp)", json_schema_extra={"units": "kPa"})
    differential_pressure: Optional[float] = Field(default=None, alias="Differential Pressure (Pd=P1-P2)", json_schema_extra={"units": "kPa"})
    filter_inlet_pressure: Optional[float] = Field(default=None, alias="Filter Inlet Pressure (P3)", json_schema_extra={"units": "kPa"})
    filter_outlet_pressure: Optional[float] = Field(default=None, alias="Filter Outlet Pressure (P4)", json_schema_extra={"units": "kPa"})
    
    # Flow and environmental sensors
    coolant_flow_rate: Optional[float] = Field(default=None, alias="Coolant Flow Rate (F1)", json_schema_extra={"units": "LPM"}) # LPM = Liters per minute (公制)，GPM(英制)
    ambient_temperature: Optional[float] = Field(default=None, alias="Ambient Temperature (Ta)", json_schema_extra={"units": "°C"})
    relative_humidity: Optional[float] = Field(default=None, alias="Relative Humidity (RH)", json_schema_extra={"units": "%"})
    dew_point: Optional[float] = Field(default=None, alias="Dew Point (TDp)", json_schema_extra={"units": "°C"})
    
    # Water quality sensors
    ph: Optional[float] = Field(default=None, alias="pH (PH)", json_schema_extra={"units": "pH"})
    conductivity: Optional[float] = Field(default=None, alias="Conductivity (CON)", json_schema_extra={"units": "µS/cm"})
    turbidity: Optional[float] = Field(default=None, alias="Turbidity (Tur)", json_schema_extra={"units": "NTU"})
    
    # Power and current
    instant_power_consumption: Optional[float] = Field(default=None, alias="Instant Power Consumption", json_schema_extra={"units": "kW"})
    average_current: Optional[float] = Field(default=None, alias="Average Current", json_schema_extra={"units": "A"})
    heat_capacity: Optional[float] = Field(default=None, alias="Heat Capacity", json_schema_extra={"units": "kW"})
    
    # Pump and fan speeds (actual)
    coolant_pump1: Optional[float] = Field(default=None, alias="Coolant Pump1[%]", json_schema_extra={"units": "%"})
    coolant_pump2: Optional[float] = Field(default=None, alias="Coolant Pump2[%]", json_schema_extra={"units": "%"})
    coolant_pump3: Optional[float] = Field(default=None, alias="Coolant Pump3[%]", json_schema_extra={"units": "%"})
    fan_speed1: Optional[float] = Field(default=None, alias="Fan Speed1[%]", json_schema_extra={"units": "%"})
    fan_speed2: Optional[float] = Field(default=None, alias="Fan Speed2[%]", json_schema_extra={"units": "%"})
    fan_speed3: Optional[float] = Field(default=None, alias="Fan Speed3[%]", json_schema_extra={"units": "%"})
    fan_speed4: Optional[float] = Field(default=None, alias="Fan Speed4[%]", json_schema_extra={"units": "%"})
    fan_speed5: Optional[float] = Field(default=None, alias="Fan Speed5[%]", json_schema_extra={"units": "%"})
    fan_speed6: Optional[float] = Field(default=None, alias="Fan Speed6[%]", json_schema_extra={"units": "%"})
    # fan_speed7: Optional[float] = Field(default=None, alias="Fan Speed7[%]", json_schema_extra={"units": "%"})
    # fan_speed8: Optional[float] = Field(default=None, alias="Fan Speed8[%]", json_schema_extra={"units": "%"})
    
    # Settings
    mode_selection: Optional[str] = Field(default=None, alias="Mode Selection", json_schema_extra={"units": None}) # Auto|Manual|Stop
    target_coolant_temperature_setting: Optional[float] = Field(default=None, alias="Target Coolant Temperature Setting", json_schema_extra={"units": "°C"})
    target_coolant_pressure_setting: Optional[float] = Field(default=None, alias="Target Coolant Pressure Setting", json_schema_extra={"units": "kPa"})
    pump_swap_time_setting: Optional[float] = Field(default=None, alias="Pump Swap Time Setting", json_schema_extra={"units": "hours"})
    
    # Pump and fan speed settings
    pump1_speed_setting: Optional[float] = Field(default=None, alias="Pump1 Speed Setting", json_schema_extra={"units": "%"})
    pump2_speed_setting: Optional[float] = Field(default=None, alias="Pump2 Speed Setting", json_schema_extra={"units": "%"})
    pump3_speed_setting: Optional[float] = Field(default=None, alias="Pump3 Speed Setting", json_schema_extra={"units": "%"})
    fan_1_speed_setting: Optional[float] = Field(default=None, alias="Fan 1 Speed Setting", json_schema_extra={"units": "%"})
    fan_2_speed_setting: Optional[float] = Field(default=None, alias="Fan 2 Speed Setting", json_schema_extra={"units": "%"})
    fan_3_speed_setting: Optional[float] = Field(default=None, alias="Fan 3 Speed Setting", json_schema_extra={"units": "%"})
    fan_4_speed_setting: Optional[float] = Field(default=None, alias="Fan 4 Speed Setting", json_schema_extra={"units": "%"})
    fan_5_speed_setting: Optional[float] = Field(default=None, alias="Fan 5 Speed Setting", json_schema_extra={"units": "%"})
    fan_6_speed_setting: Optional[float] = Field(default=None, alias="Fan 6 Speed Setting", json_schema_extra={"units": "%"})
    # fan_7_speed_setting: Optional[float] = Field(default=None, alias="Fan 7 Speed Setting", json_schema_extra={"units": "%"})
    # fan_8_speed_setting: Optional[float] = Field(default=None, alias="Fan 8 Speed Setting", json_schema_extra={"units": "%"})
    # fan_9_speed_setting: Optional[float] = Field(default=None, alias="Fan 9 Speed Setting", json_schema_extra={"units": "%"})
    # fan_10_speed_setting: Optional[float] = Field(default=None, alias="Fan 10 Speed Setting", json_schema_extra={"units": "%"})
    
