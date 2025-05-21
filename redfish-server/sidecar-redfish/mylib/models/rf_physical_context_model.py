'''
@see https://redfish.dmtf.org/schemas/v1/PhysicalContext.json#/definitions/PhysicalContext
'''
import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pydantic import (
    BaseModel,
    ConfigDict,
    Field, 
    computed_field,
    model_validator,
    #validator, # deprecated
    field_validator,
)
from typing_extensions import Self
from enum import Enum

from mylib.models.rf_base_model import RfResourceBaseModel, RfResourceCollectionBaseModel


class RfLogicalContext(str, Enum):
    Capacity = "Capacity"
    Environment = "Environment"
    Network = "Network"
    Performance = "Performance"
    Security = "Security"
    Storage = "Storage"

class RfPhysicalContext(str, Enum):
    Room = "Room"
    Intake = "Intake"
    Exhaust = "Exhaust"
    LiquidInlet = "LiquidInlet"
    LiquidOutlet = "LiquidOutlet"
    Front = "Front"
    Back = "Back"
    Upper = "Upper"
    Lower = "Lower"
    CPU = "CPU"
    CPUSubsystem = "CPUSubsystem"
    GPU = "GPU"
    GPUSubsystem = "GPUSubsystem"
    FPGA = "FPGA"
    Accelerator = "Accelerator"
    ASIC = "ASIC"
    Backplane = "Backplane"
    SystemBoard = "SystemBoard"
    PowerSupply = "PowerSupply"
    PowerSubsystem = "PowerSubsystem"
    VoltageRegulator = "VoltageRegulator"
    Rectifier = "Rectifier"
    StorageDevice = "StorageDevice"
    StorageSubsystem = "StorageSubsystem"
    NetworkingDevice = "NetworkingDevice"
    ExpansionSubsystem = "ExpansionSubsystem"
    ComputeBay = "ComputeBay"
    StorageBay = "StorageBay"
    NetworkBay = "NetworkBay"
    ExpansionBay = "ExpansionBay"
    PowerSupplyBay = "PowerSupplyBay"
    Memory = "Memory"
    MemorySubsystem = "MemorySubsystem"
    Chassis = "Chassis"
    Fan = "Fan"
    CoolingSubsystem = "CoolingSubsystem"
    Motor = "Motor"
    Transformer = "Transformer"
    ACUtilityInput = "ACUtilityInput"
    ACStaticBypassInput = "ACStaticBypassInput"
    ACMaintenanceBypassInput = "ACMaintenanceBypassInput"
    DCBus = "DCBus"
    ACOutput = "ACOutput"
    ACInput = "ACInput"
    PowerOutlet = "PowerOutlet"
    TrustedModule = "TrustedModule"
    Board = "Board"
    Transceiver = "Transceiver"
    Battery = "Battery"
    Pump = "Pump"
    Filter = "Filter"
    Reservoir = "Reservoir"
    Switch = "Switch"
    Manager = "Manager"


class RfPhysicalSubContext(str, Enum):
    Input = "Input"
    Output = "Output"


    