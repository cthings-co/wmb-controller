# Copyright (c) 2025 CTHINGS.CO
# SPDX-License-Identifier: Apache-2.0
"""
WMB Protocol Decoder

This module provides functions to decode and validate WMB protocol messages.
It handles CRC verification and protobuf message parsing.
""" 
from . import mb_protocol_pb2 as mb_protocol
from . import mb_protocol_commands_pb2 as mb_commands
from . import mb_protocol_enums_pb2 as mb_enums
from crccheck.crc import Crc16Dds110
from . import mb_protocol_answers_pb2 as mb_answers
from typing import List, Optional, Tuple, Union

def decode_response(frame: bytes) -> Tuple[bool, Optional[str], Optional[mb_protocol.MbMessage]]:
    """
    Main decoder function that validates and decodes response frames
    
    Args:
        frame: Bytes containing the response frame to decode
        
    Returns:
        Tuple containing:
        - Success flag (bool)
        - Error message (str) if success is False, None otherwise
        - Decoded message if success is True, None otherwise
    """
    if len(frame) < 2:  # Need at least 2 bytes for CRC
        return False, "Frame too short", None

    # Separate message data from CRC
    message_data = frame[:-2]
    received_crc_bytes = frame[-2:]

    # Calculate CRC
    crcinst = Crc16Dds110()
    crcinst.process(message_data)
    calculated_crc = crcinst.final()
    received_crc = int.from_bytes(received_crc_bytes, 'big')

    # Verify CRC
    if calculated_crc != received_crc:
        return False, f"CRC verification failed. Calculated: {calculated_crc:04x}, Received: {received_crc:04x}", None

    try:
        # Parse message using protobuf
        message = mb_protocol.MbMessage()
        message.ParseFromString(message_data)
        return True, None, message

    except Exception as e:
        return False, f"Error parsing message: {str(e)}", None
