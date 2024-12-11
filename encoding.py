from enum import Enum
from typing import Optional
import crcmod

# Constants
HEADER = 0x47
PROTOCOL_VERSION = 0x01
WIREPAS_MAX_PAYLOAD = 1024
MAX_OPTION_PAYLOAD_SIZE = 1017

class DeviceMode(Enum):
    MODBUS_MASTER = 0x00  # default
    MODBUS_SNIFFER = 0x01

class AntennaConfig(Enum):
    INTERNAL = 0x00  # default
    EXTERNAL = 0x01

class RS485Port(Enum):
    PORT_0 = 0x01
    PORT_1 = 0x02

class BaudRate(Enum):
    B4800 = 0x0C
    B9600 = 0x0D
    B19200 = 0x0E
    B28800 = 0x0F
    B38400 = 0x10
    B57600 = 0x11
    B76800 = 0x12
    B115200 = 0x13

class Command(Enum):
    DEVICE_RESET = 0x01
    DEVICE_DIAGNOSTICS = 0x02
    FOTA = 0x03
    DEVICE_MODE = 0x04
    ANTENNA_CONFIG = 0x05
    BAUDRATE_CONFIG = 0x06
    MODBUS_ONESHOT = 0x07
    MODBUS_PERIODIC = 0x08

# CRC16Dds110 function
crc16_func = crcmod.mkCrcFun(0x18005, initCrc=0x800D, rev=False)

def create_device_mode_payload(mode: DeviceMode) -> bytes:
    """Creates payload for Device Mode command"""
    return bytes([mode.value])

def create_antenna_config_payload(config: AntennaConfig) -> bytes:
    """Creates payload for Antenna Configuration command"""
    return bytes([config.value])

def create_baudrate_config_payload(port: RS485Port, baudrate: BaudRate) -> bytes:
    """Creates payload for Baudrate Configuration command"""
    return bytes([port.value, baudrate.value])

def create_modbus_oneshot_payload(port: RS485Port, modbus_frame: bytes) -> bytes:
    """Creates payload for Modbus One-shot command"""
    if port == RS485Port.NO_EFFECT:
        raise ValueError("Invalid port selection")
    return bytes([port.value]) + modbus_frame

def create_modbus_periodic_payload(
    port: RS485Port, 
    config_index: int,
    interval_seconds: int,
    modbus_frame: bytes
) -> bytes:
    """Creates payload for Modbus Periodic command"""
    if not (1 <= config_index <= 64):
        raise ValueError("Config index must be between 1 and 64")
    if not (0 <= interval_seconds <= 2592000):  # 30 days in seconds
        raise ValueError("Interval must be between 0 and 30 days")
    
    return bytes([port.value, config_index]) + interval_seconds.to_bytes(3, 'big') + modbus_frame

def create_payload(command: Command, options_payload: Optional[bytes] = None) -> bytes:
    """
    Creates a payload for WMBController according to the MB-Protocol specification.
    
    Args:
        command (Command): Command enum value
        options_payload (bytes, optional): Command-specific options payload
    
    Returns:
        bytes: Encoded payload ready for WMBController
        
    Raises:
        ValueError: If payload size exceeds Wirepas limit (102B) or invalid command/options
    """
    if options_payload is None:
        options_payload = b''

    # Validate options size
    if len(options_payload) > MAX_OPTION_PAYLOAD_SIZE:
        raise ValueError("Options payload size exceeds maximum allowed size")

    # Construct the frame
    ptu = len(options_payload)
    print(f"PTU: {ptu}")
    print(f"Options payload: {options_payload}")
    frame = bytearray([HEADER, PROTOCOL_VERSION, command.value]) + ptu.to_bytes(2, 'big') + options_payload


    # Calculate CRC
    crc = crc16_func(frame)
    frame += crc.to_bytes(2, 'big')

    # Check final size against Wirepas limit
    if len(frame) > WIREPAS_MAX_PAYLOAD:
        raise ValueError(f"Payload size ({len(frame)}B) exceeds Wirepas limit ({WIREPAS_MAX_PAYLOAD}B). Fragmentation not yet implemented.")

    return bytes(frame)


if __name__ == "__main__":
    print("MODBUS_MASTER payload:")
    options_payload = create_device_mode_payload(DeviceMode.MODBUS_SNIFFER)
    payload = create_payload(Command.DEVICE_MODE, options_payload)
    print(payload) 

    print("-" * 50)

    print("DEVICE_RESET payload:")
    payload = create_payload(Command.DEVICE_RESET)
    print(payload)

    print("-" * 50)

    print("DIAGNOSTICS payload:")
    payload = create_payload(Command.DEVICE_DIAGNOSTICS)
    print(payload)

    print("-" * 50)
    print("Device Mode payload:")
    options_payload = create_device_mode_payload(DeviceMode.MODBUS_SNIFFER)
    payload = create_payload(Command.DEVICE_MODE, options_payload)
    print(payload)

    print("-" * 50)
    print("Antenna Settings payload:")
    options_payload = create_antenna_config_payload(AntennaConfig.EXTERNAL)
    payload = create_payload(Command.ANTENNA_CONFIG, options_payload) 
    print(payload)

    print("-" * 50)
    print("Baudrate Settings payload:")
    options_payload = create_baudrate_config_payload(RS485Port.PORT_0, BaudRate.B19200)
    print(options_payload)
    payload = create_payload(Command.BAUDRATE_CONFIG, options_payload)
    print(payload)
