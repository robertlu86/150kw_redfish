from typing import Literal
from pydantic import (
    BaseModel,
    Field,
    validator, # deprecated
    field_validator,
)
from enum import Enum
from mylib.models.rf_base_model import RfBaseModel
from typing import Optional, List, Dict, Any

        

class RfChassisModel(RfBaseModel):
    """
    @see https://redfish.dmtf.org/schemas/v1/Chassis.json#/definitions/Chassis
    @see https://redfish.dmtf.org/schemas/v1/Chassis.v1_26_0.json#/definitions/Chassis
    @note 65 items
    """
    # Odata_context: Optional[str] = Field(default=None, alias="@odata.context")
    # Odata_etag: Optional[str] = Field(default=None, alias="@odata.etag")
    # # "@odata.id": {1 item},
    # # "@odata.type": {1 item},
    # "Actions": {3 items},
    # "Assembly": {5 items},
    # "AssetTag": {4 items},
    # "Certificates": {5 items},
    # "ChassisType": {4 items},
    # "Controls": {5 items},
    # "DepthMm": {7 items},
    # "Description": {2 items},
    # "Doors": {4 items},
    # "Drives": {4 items},
    # "ElectricalSourceManagerURIs": {7 items},
    # "ElectricalSourceNames": {6 items},
    # "EnvironmentMetrics": {5 items},
    # "EnvironmentalClass": {5 items},
    # "FabricAdapters": {5 items},
    # "HeatingCoolingEquipmentNames": {6 items},
    # "HeatingCoolingManagerURIs": {7 items},
    # "HeightMm": {7 items},
    # "HotPluggable": {5 items},
    # "Id": {2 items},
    # "IndicatorLED": {6 items},
    # "LeakDetectors": {5 items},
    # "Links": {3 items},
    # "Location": {4 items},
    # "LocationIndicatorActive": {5 items},
    # "LogServices": {4 items},
    # "Manufacturer": {4 items},
    # "MaxPowerWatts": {6 items},
    # "Measurements": {7 items},
    # "MediaControllers": {7 items},
    # "Memory": {5 items},
    # "MemoryDomains": {5 items},
    # "MinPowerWatts": {6 items},
    # "Model": {4 items},
    # "Name": {2 items},
    # "NetworkAdapters": {5 items},
    # "Oem": {3 items},
    # "PCIeDevices": {5 items},
    # "PCIeSlots": {7 items},
    # "PartNumber": {4 items},
    # "PhysicalSecurity": {4 items},
    # "Power": {6 items},
    # "PowerState": {5 items},
    # "PowerSubsystem": {5 items},
    # "PoweredByParent": {5 items},
    # "Processors": {5 items},
    # "Replaceable": {5 items},
    # "SKU": {4 items},
    # "Sensors": {5 items},
    # "SerialNumber": {4 items},
    # "SparePartNumber": {5 items},
    # "Status": {3 items},
    # "Thermal": {6 items},
    # "ThermalDirection": {5 items},
    # "ThermalManagedByParent": {5 items},
    # "ThermalSubsystem": {5 items},
    # "TrustedComponents": {5 items},
    # "UUID": {5 items},
    # "Version": {5 items},
    # "WeightKg": {7 items},
    # "WidthMm": {7 items}
    pass
    

                
