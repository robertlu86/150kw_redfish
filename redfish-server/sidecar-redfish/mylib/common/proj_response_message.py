'''
我們有一些api的設計是回傳純字串，並非json格式
為了統一api回傳為json，我們設計一個ProjResponseNormalMessage
'''
from typing import List, Dict, Any
from pydantic import (
    BaseModel,
    Field, 
    computed_field,
    model_validator,
    #validator, # deprecated
    field_validator,
    field_serializer
)

class ProjResponseMessage(BaseModel):
    code: int = Field(default=None)
    message: str = Field(default="")
    
    def to_dict(self) -> dict:
        return self.model_dump(
                    by_alias=True,
                    include=set(self.__class__.model_fields.keys()),
                    exclude_none=True
                )

# class ProjResponseNormalMessage:
#     def __init__(self, message: str):
#         self.message = message
    
#     def to_dict(self):
#         return {
#             "message": self.message
#         }
    
# class ProjResponseErrorMessage:
#     def __init__(self, code: int, err_msg: str):
#         self.code = code
#         self.message = err_msg
    
#     def to_dict(self):
#         return {
#             "code": self.code,
#             "message": self.message
#         }
        
