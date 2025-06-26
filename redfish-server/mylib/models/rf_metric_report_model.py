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

class RfActions(BaseModel):
    # Oem: Optional[RfOemActions] = Field(default=None) # why fail?
    Oem: Optional[Dict[str, Any]] = Field(default=None)

class RfMetricValue(BaseModel):
    MetricDefinition: Optional[Dict[str, Any]] = Field(default=None)  
    MetricId: Optional[str] = Field(default=None)
    MetricProperty: Optional[str] = Field(default=None)
    MetricValue: Optional[str] = Field(default=None)
    Oem: Optional[Dict[str, Any]] = Field(default=None)
    Timestamp: Optional[str] = Field(default=None)

class RfMetricReportModel(RfResourceBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/MetricReport.json
    @see https://redfish.dmtf.org/schemas/v1/MetricReport.v1_5_2.json#/definitions/MetricReport
    @note properties 14 items
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
    Actions: Optional[RfActions] = Field(default=None)
    Context: Optional[str] = Field(default=None)
    Description: Optional[str] = Field(default=None)
    # Id: Optional[str] = Field(default=None)
    MetricReportDefinition: Optional[Dict[str, Any]] = Field(default=None) # This could be a reference to another resource
    MetricValues: Optional[RfMetricValue] = Field(default=None)
    # Name: Optional[str] = Field(default=None)
    Oem: Optional[Dict[str, Any]] = Field(default=None)
    ReportSequence: Optional[str] = Field(default=None)
    Timestamp: Optional[str] = Field(default=None, description="The timestamp of the report in ISO 8601 format.")
