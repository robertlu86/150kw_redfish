from typing import Dict, Any, Optional, Union, Tuple
from flask import Response
import json

def error_response(msg: str, http_status: int, code: Optional[str] = None) -> Union[str, Dict[str, Any], Response]:
    """
    Create a standardized error response.
    
    Args:
        msg: Error message
        status: HTTP status code
        
    Returns:
        Error response in the requested format
    """
    if not code:
        return Response(msg, status= http_status)
    
    error = {
        'error': {
            'code': code if code else 'Base.GeneralError',
            'message': msg
        }
    }
    return Response(json.dumps(error), status=http_status, content_type="application/json")
        

ERROR_INTERNAL = error_response('Internal Server Error', 500)

ERROR_PROPERTY_MISSING = error_response('Property Missing', 400, 'Base.PropertyMissing')

ERROR_PROPERTY_TYPE = error_response('Property Type Error', 400, 'Base.PropertyValueTypeError')

ERROR_PROPERTY_FORMAT = error_response('Property Value Format Error', 400, 'Base.PropertyValueFormatError')

ERROR_PROPERTY_VALUE_NOT_IN_LIST = error_response('Property Value Not In List', 400, 'Base.PropertyValueNotInList')
ERROR_PROPERTY_VALUE_OUT_OF_RANGE = error_response('Property Value Out of Range', 400, 'Base.PropertyValueOutOfRange')

ERROR_RESOURCE_NOT_FOUND = error_response('Resource Not Found', 404, 'Base.ResourceNotFound')

ERROR_DELETE_SUCCESS = Response(json.dumps({'message':'OK'}), 200, {'Content-Type': 'application/json'})

ERROR_PASSWORD_FORMAT = error_response('Password must contain at least one uppercase letter, '
                                       'one lowercase letter, one digit, and one special character',
                                       400,
                                       'Base.PropertyValueFormatError')

ERROR_USERNAME_FORMAT = error_response('User name must follow pattern ^[A-Za-z][A-Za-z0-9@_.-]{0,14}[A-Za-z0-9]$',
                                        400,
                                        'Base.PropertyValueFormatError')