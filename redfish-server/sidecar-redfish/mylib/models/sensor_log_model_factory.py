from pydantic import BaseModel, Field, ConfigDict, create_model
import yaml
from typing import Type, Optional
from mylib.models.sensor_log_model import (
    SensorLogBaseModel,
    SensorLogModel,
)

        

"""
Usage:
    model_instance = SensorLogModelFactory.create_model(
        "CustomerBSensorLogModel", 
        {"field1": 1.0, "field2": 2.0, "field3": 3.0}
    )
"""
class SensorLogModelFactory:
    registered_models = {
        "SensorLogModel": SensorLogModel,
        # "CustomerASensorLogModel": CustomerASensorLogModel,
        # "CustomerBSensorLogModel": CustomerBSensorLogModel,
    }

    @classmethod
    def get_model(cls, model_name: str) -> Type[SensorLogModel]:
        """
        Return the model class based on the given model name
        """
        model_class = cls.registered_models.get(model_name)
        if model_class is None:
            raise ValueError(f"Unknown model name: {model_name}")
        return model_class
    
    @classmethod
    def create_model(cls, model_name: str, data: dict=None) -> SensorLogModel:
        """
        Create a model instance based on the given model name
        """
        model_class = cls.get_model(model_name)
        if data is None:
            return model_class()
        else:
            return model_class(**data)

    
