# Copyright (c) 2025 CTHINGS.CO
# SPDX-License-Identifier: Apache-2.0
"""
WMB Protocol Encoder

This module provides functions to create WMB protocol messages.
Each message includes a header, version, command payload, and CRC verification.
""" 
from . import mb_protocol_pb2 as mb_protocol
from . import mb_protocol_commands_pb2 as mb_commands
from . import mb_protocol_enums_pb2 as mb_enums
from crccheck.crc import Crc16Dds110

# Protocol constants
PROTOCOL_HEADER = 0x47
PROTOCOL_VERSION = 0x01

def create_message():
    """Creates a base message with common fields"""
    message = mb_protocol.MbMessage()
    message.header = PROTOCOL_HEADER
    message.version = PROTOCOL_VERSION
    return message

def add_crc(data: bytes) -> bytes:
    """Adds CRC to serialized message"""
    crcinst = Crc16Dds110()
    crcinst.process(data)
    crc = crcinst.final()
    return data + bytes([crc >> 8, crc & 0xFF])

def create_device_reset() -> bytes:
    """Creates device reset command"""
    message = create_message()
    message.cmd = mb_protocol.Cmd.CMD_DEV_RESET
    
    # Create command frame with empty frame
    cmd_frame = mb_commands.CmdFrame()
    cmd_frame.empty_frame.CopyFrom(mb_commands.EmptyFrame())
    message.payload.payload_cmd_frame.CopyFrom(cmd_frame)
    
    return add_crc(message.SerializeToString())

def create_diagnostics() -> bytes:
    """Creates diagnostics request command"""
    message = create_message()
    message.cmd = mb_protocol.Cmd.CMD_DIAGNOSTICS
    
    # Create command frame with empty frame
    cmd_frame = mb_commands.CmdFrame()
    cmd_frame.empty_frame.CopyFrom(mb_commands.EmptyFrame())
    message.payload.payload_cmd_frame.CopyFrom(cmd_frame)
    
    return add_crc(message.SerializeToString())

def create_device_mode(mode: mb_enums.ModbusMode) -> bytes:
    """Creates device mode command"""
    # Step 1: Create the base message
    message = create_message()
    message.cmd = mb_protocol.Cmd.CMD_DEV_MODE
    
    # Step 2: Create the device mode frame
    device_mode_frame = mb_commands.DeviceModeFrame()
    device_mode_frame.device_mode = mode
    
    # Step 3: Create the command frame and attach device mode frame
    cmd_frame = mb_commands.CmdFrame()
    cmd_frame.device_mode_frame.CopyFrom(device_mode_frame)
    
    # Step 4: Attach the command frame to the message
    message.payload.payload_cmd_frame.CopyFrom(cmd_frame)
    
    # Step 5: Serialize and add CRC
    return add_crc(message.SerializeToString())

def create_antenna_config(config: mb_enums.AntennaSettings) -> bytes:
    """Creates antenna configuration command"""
    # Step 1: Create the base message
    message = create_message()  # This sets header and version
    message.cmd = mb_protocol.Cmd.CMD_ANTENA_CONFIG  # Set command type
    
    # Step 2: Create the antenna settings frame
    antenna_frame = mb_commands.AntennaSettingsFrame()
    antenna_frame.antenna_settings = int(config)  # Convert enum to int to ensure proper setting
    
    # Step 3: Create the command frame and attach antenna settings frame
    cmd_frame = mb_commands.CmdFrame()
    cmd_frame.antenna_settings_frame.CopyFrom(antenna_frame)
    
    # Step 4: Attach the command frame to the message
    message.payload.payload_cmd_frame.CopyFrom(cmd_frame)
 
    # Step 5: Serialize and add CRC
    return add_crc(message.SerializeToString())

def create_baudrate_config(port: mb_enums.ModbusPort, baudrate: mb_enums.ModbusBaud) -> bytes:
    """Creates baudrate configuration command"""
    # Step 1: Create the base message
    message = create_message()
    message.cmd = mb_protocol.Cmd.CMD_BAUDRATE_CONFIG
    
    # Step 2: Create the baudrate settings frame
    baudrate_frame = mb_commands.BaudrateSettingsFrame()
    baudrate_frame.modbus_port = int(port)
    baudrate_frame.modbus_baud = int(baudrate)
    
    # Step 3: Create the command frame and attach baudrate settings frame
    cmd_frame = mb_commands.CmdFrame()
    cmd_frame.baudrate_settings_frame.CopyFrom(baudrate_frame)
    
    # Step 4: Attach the command frame to the message
    message.payload.payload_cmd_frame.CopyFrom(cmd_frame)
    
    # Step 5: Serialize and add CRC
    return add_crc(message.SerializeToString())

def create_modbus_oneshot(port: mb_enums.ModbusPort, modbus_frame: bytes) -> bytes:
    """Creates Modbus one-shot command"""
    if len(modbus_frame) > 256:
        raise ValueError("Modbus frame exceeds maximum size of 256 bytes")
    
    # Step 1: Create the base message
    message = create_message()
    message.cmd = mb_protocol.Cmd.CMD_MODBUS_ONE_SHOT
    
    # Step 2: Create the modbus one-shot frame
    oneshot_frame = mb_commands.ModbusOneShotFrame()
    oneshot_frame.modbus_port = port
    oneshot_frame.modbus_frame = modbus_frame
    
    # Step 3: Create the command frame and attach one-shot frame
    cmd_frame = mb_commands.CmdFrame()
    cmd_frame.modbus_one_shot_frame.CopyFrom(oneshot_frame)
    
    # Step 4: Attach the command frame to the message
    message.payload.payload_cmd_frame.CopyFrom(cmd_frame)
    
    # Step 5: Serialize and add CRC
    return add_crc(message.SerializeToString())

def create_modbus_periodic(
    port: mb_enums.ModbusPort,
    config_index: int,
    interval_seconds: int,
    modbus_frame: bytes
) -> bytes:
    """Creates Modbus periodic command"""
    if not (1 <= config_index <= 64):
        raise ValueError("Config index must be between 1 and 64")
    if not (0 <= interval_seconds <= 2592000):
        raise ValueError("Interval must be between 0 seconds and 30 days expressed in seconds")
    if len(modbus_frame) > 256:
        raise ValueError("Modbus frame exceeds maximum size of 256 bytes")
    
    # Step 1: Create the base message
    message = create_message()
    message.cmd = mb_protocol.Cmd.CMD_MODBUS_PERIODICAL
    
    # Step 2: Create the modbus periodic frame
    periodic_frame = mb_commands.ModbusPeriodicalFrame()
    periodic_frame.modbus_port = port
    periodic_frame.configuration_index = config_index
    periodic_frame.interval = interval_seconds
    periodic_frame.modbus_frame = modbus_frame
    
    # Step 3: Create the command frame and attach periodic frame
    cmd_frame = mb_commands.CmdFrame()
    cmd_frame.modbus_periodical_frame.CopyFrom(periodic_frame)
    
    # Step 4: Attach the command frame to the message
    message.payload.payload_cmd_frame.CopyFrom(cmd_frame)
    
    # Step 5: Serialize and add CRC
    return add_crc(message.SerializeToString())

   
def print_hex_bytes(bytes_data: bytes) -> None:
    """Print bytes as space-separated hex values"""
    print(' '.join(f'{b:02x}' for b in bytes_data))

