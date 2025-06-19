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





class RfMetricReportDefinitionModel(RfResourceBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/MetricReportDefinition.json
    @see https://redfish.dmtf.org/schemas/v1/MetricReportDefinition.v1_4_7.json#/definitions/MetricReportDefinition
    @note properties 24 items
    @note 
        required: [
            "@odata.id",
            "@odata.type",
            "Id",
            "Name"
        ]
    """
    ...


class RfMetricReportDefinitionCollectionModel(RfResourceCollectionBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/MetricReportDefinitionCollection.json
    """
    pass