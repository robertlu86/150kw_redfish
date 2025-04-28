from pydantic import (
    BaseModel,
    Field,
    validator, # deprecated
    field_validator,
)

class StatusModel(BaseModel):
    Health: str = Field(default="", description="ex: OK")
    State: str = Field(default="", description="ex: Enabled")
    