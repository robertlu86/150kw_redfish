'''
這是Redfish的managers service
'''
import subprocess, json
from mylib.services.base_service import BaseService
from mylib.models.rf_networkprotocol_model import RfNetworkProtocolModel
from mylib.models.rf_snmp_model import RfSnmpModel
from mylib.adapters.webapp_api_adapter import WebAppAPIAdapter
from mylib.models.rf_resource_model import RfResetType

class RfTelemetryService(BaseService):
    pass