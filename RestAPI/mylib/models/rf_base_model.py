
from typing import Optional, List, Dict, Any
from pydantic import (
    BaseModel,
    Field, 
    computed_field,
    model_validator,
    #validator, # deprecated
    field_validator,
)



class RfResourceBaseModel(BaseModel):
    """
    @see https://www.dmtf.org/sites/default/files/standards/documents/DSP0266_1.22.0.html#resources
    """
    odata_type: str         = Field(default=None, description="", alias="@odata.type")
    Id: str                 = Field(default=None, description="")
    Name: str               = Field(default=None, description="")
    odata_id: Optional[str] = Field(default=None, description="", alias="@odata.id")


class RfResourceCollectionBaseModel(BaseModel):
    """
    @see https://www.dmtf.org/sites/default/files/standards/documents/DSP0266_1.22.0.html#resource-collections
    """
    # shall contain
    odata_id: Optional[str]       = Field(default="", description="", alias="@odata.id")
    odata_type: str               = Field(default="", description="", alias="@odata.type")
    Name: str                     = Field(default="", description="")
    Members: List[Dict[str, Any]] = Field(default=[], description="")
    Members_odata_count: int      = Field(default=0, description="", alias="Members@odata.count")
    
    # maybe contain 
    odata_context: Optional[str]            = Field(default=None, description="", alias="@odata.context")
    odata_etag: Optional[str]               = Field(default=None, description="", alias="@odata.etag")
    Description: Optional[str]              = Field(default=None, description="")
    Members_odata_nextLink: Optional[str]   = Field(default=None, description="", alias="Members@odata.nextLink")
    Oem: Optional[Dict[str, Any]]           = Field(default=None, description="")

class OemModel(BaseModel):
    """
    @see https://www.dmtf.org/sites/default/files/standards/documents/DSP0266_1.22.0.html#oem-resources
    """
    pass