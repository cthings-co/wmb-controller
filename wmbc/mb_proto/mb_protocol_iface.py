import logging
import json
import wmbc.mb_proto.mb_protocol_pb2 as mb_protocol
import wmbc.mb_proto.mb_protocol_commands_pb2 as mb_commands
import wmbc.mb_proto.mb_protocol_enums_pb2 as mb_enums
import wmbc.mb_proto.mb_protocol_answers_pb2 as mb_answers
from google.protobuf.json_format import MessageToJson
from crccheck.crc import Crc16Dds110
from typing import List, Optional, Tuple, Union

from pymodbus.client import ModbusFrameGenerator
from pymodbus.framer import FramerType

logging.basicConfig(level=logging.INFO)


class MBProto():
    # Protocol constants
    PROTOCOL_HEADER = 0x47
    PROTOCOL_VERSION = 0x01

    def __init__(self):
        pass

    def _create_message(self):
        """Creates a base message with common fields"""
        message = mb_protocol.MbMessage()
        message.header = self.PROTOCOL_HEADER
        message.version = self.PROTOCOL_VERSION
        return message
    
    def _add_crc(self, data: bytes) -> bytes:
        """Add CRC to serialized message"""
        crcinst = Crc16Dds110()
        crcinst.process(data)
        crc = crcinst.final()
        return data + bytes([crc >> 8, crc & 0xFF])
    
    def create_device_reset(self) -> bytes:
        """Creates device reset command"""
        message = self._create_message()
        message.cmd = mb_protocol.Cmd.CMD_DEV_RESET
        
        # Create command frame with empty frame
        cmd_frame = mb_commands.CmdFrame()
        cmd_frame.empty_frame.CopyFrom(mb_commands.EmptyFrame())
        message.payload.payload_cmd_frame.CopyFrom(cmd_frame)
        
        return self._add_crc(message.SerializeToString())
    
    def create_diagnostics(self) -> bytes:
        """Creates diagnostics request command"""
        message = self._create_message()
        message.cmd = mb_protocol.Cmd.CMD_DIAGNOSTICS
        
        # Create command frame with empty frame
        cmd_frame = mb_commands.CmdFrame()
        cmd_frame.empty_frame.CopyFrom(mb_commands.EmptyFrame())
        message.payload.payload_cmd_frame.CopyFrom(cmd_frame)
        
        return self._add_crc(message.SerializeToString())
    
    def create_device_mode(self) -> bytes:
        """Creates device mode command"""
        message = self._create_message()
        message.cmd = mb_protocol.Cmd.CMD_DEV_MODE
        
        # Step 1: Create the device mode frame
        device_mode_frame = mb_commands.DeviceModeFrame()
        device_mode_frame.device_mode = self._device_mode
        
        # Step 2: Create the command frame and attach device mode frame
        cmd_frame = mb_commands.CmdFrame()
        cmd_frame.device_mode_frame.CopyFrom(device_mode_frame)
        
        # Step 3: Attach the command frame to the message
        message.payload.payload_cmd_frame.CopyFrom(cmd_frame)
        
        # Step 4: Serialize and add CRC
        return self._add_crc(message.SerializeToString())
    
    def create_antenna_config(self) -> bytes:
        # Step 1: Create the base message
        message = self._create_message()  # This sets header and version
        message.cmd = mb_protocol.Cmd.CMD_ANTENA_CONFIG  # Set command type
        
        # Step 2: Create the antenna settings frame
        antenna_frame = mb_commands.AntennaSettingsFrame()
        antenna_frame.antenna_settings = self._antenna_config
        
        # Step 3: Create the command frame and attach antenna settings frame
        cmd_frame = mb_commands.CmdFrame()
        cmd_frame.antenna_settings_frame.CopyFrom(antenna_frame)
        
        # Step 4: Attach the command frame to the message
        message.payload.payload_cmd_frame.CopyFrom(cmd_frame)
     
        # Step 5: Serialize and add CRC
        return self._add_crc(message.SerializeToString())
    
    def create_port_config(self) -> bytes:
        """Creates port configuration command"""
        # Step 1: Create the base message
        message = self._create_message()
        message.cmd = mb_protocol.Cmd.CMD_PORT_CONFIG
        
        # Step 2: Create the port settings frame
        port_settings_frame = mb_commands.PortSettingsFrame()
        port_settings_frame.modbus_port = self._target_port
        port_settings_frame.port_baud = self._baudrate_config
        port_settings_frame.port_parity = self._parity_bit
        port_settings_frame.port_stop_bits = self._stop_bits
        
        # Step 3: Create the command frame and attach port settings frame
        cmd_frame = mb_commands.CmdFrame()
        cmd_frame.port_settings_frame.CopyFrom(port_settings_frame)
        
        # Step 4: Attach the command frame to the message
        message.payload.payload_cmd_frame.CopyFrom(cmd_frame)
        
        # Step 5: Serialize and add CRC
        return self._add_crc(message.SerializeToString())
    
    def create_modbus_oneshot(self, modbus_frame: bytes) -> bytes:
        """Creates Modbus one-shot command"""
        if len(modbus_frame) > 256:
            raise ValueError("Modbus frame exceeds maximum size of 256 bytes")
        
        # Step 1: Create the base message
        message = self._create_message()
        message.cmd = mb_protocol.Cmd.CMD_MODBUS_ONE_SHOT
        
        # Step 2: Create the modbus one-shot frame
        oneshot_frame = mb_commands.ModbusOneShotFrame()
        oneshot_frame.modbus_port = self._target_port
        oneshot_frame.modbus_frame = modbus_frame
        
        # Step 3: Create the command frame and attach one-shot frame
        cmd_frame = mb_commands.CmdFrame()
        cmd_frame.modbus_one_shot_frame.CopyFrom(oneshot_frame)
        
        # Step 4: Attach the command frame to the message
        message.payload.payload_cmd_frame.CopyFrom(cmd_frame)
        
        # Step 5: Serialize and add CRC
        return self._add_crc(message.SerializeToString())
    
    def create_modbus_periodic(
        self,
        config_index: int,
        interval_seconds: int,
        modbus_frame: bytes
    ) -> bytes:
        """Creates Modbus periodic command"""
        if not (1 <= config_index <= 64):
            raise ValueError("Config index must be between 1 and 64")
        if not (0 <= interval_seconds <= 2592000):
            raise ValueError("Interval must be between 0 and 2592000 seconds")
        if len(modbus_frame) > 256:
            raise ValueError("Modbus frame exceeds maximum size of 256 bytes")
        
        # Step 1: Create the base message
        message = self._create_message()
        message.cmd = mb_protocol.Cmd.CMD_MODBUS_PERIODICAL
        
        # Step 2: Create the modbus periodic frame
        periodic_frame = mb_commands.ModbusPeriodicalFrame()
        periodic_frame.modbus_port = self._target_port
        periodic_frame.configuration_index = config_index
        periodic_frame.interval = interval_seconds
        periodic_frame.modbus_frame = modbus_frame
        
        # Step 3: Create the command frame and attach periodic frame
        cmd_frame = mb_commands.CmdFrame()
        cmd_frame.modbus_periodical_frame.CopyFrom(periodic_frame)
        
        # Step 4: Attach the command frame to the message
        message.payload.payload_cmd_frame.CopyFrom(cmd_frame)
        
        # Step 5: Serialize and add CRC
        return self._add_crc(message.SerializeToString())

    def decode_response(self, frame: bytes) -> Tuple[bool, Optional[str], Optional[mb_protocol.MbMessage]]:
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

    def decode_modbus_frame(self, frame: bytes) -> dict:
        generator = ModbusFrameGenerator()
        decoded_frame = generator.parse_response(frame)
        parameters = {}
        parameters['dev_id'] = decoded_frame.dev_id
        parameters['transaction_id'] = decoded_frame.transaction_id
        parameters['address'] = decoded_frame.address
        parameters['count'] = decoded_frame.count
        parameters['bits'] = decoded_frame.bits
        parameters['registers'] = decoded_frame.registers
        parameters['status'] = decoded_frame.status
        result = {}
        result[decoded_frame.__class__.__name__] = parameters
        return result

    def decode_modbus_p_config(self, value):
        modp_cfg = dict()
        modp_cfg["enable"] = ((value & 0xF0000000) != 0)
        modp_cfg["port"] = ((value & 0xF000000) >> 24)
        modp_cfg["interval"] = value & 0xFFFFFF
        return modp_cfg

    def print_decoded_msg(self, frame: bytes, decode_modbus_frame=True) -> None:
        ret, err, msg = self.decode_response(frame)
        if (not ret):
            logging.error("Failed to decode frame!:%s", err)
            return
        json_str = MessageToJson(msg, always_print_fields_with_no_presence=True, preserving_proto_field_name=True)
        _dict = json.loads(json_str)
        if (msg.cmd == mb_protocol.Cmd.CMD_MODBUS_ONE_SHOT or msg.cmd == mb_protocol.Cmd.CMD_MODBUS_PERIODICAL):
            if (msg.payload.payload_answer_frame.ack_frame.acknowladge == 0):
                # Swap ASCII to binary
                data = msg.payload.payload_answer_frame.modbus_response_frame.modbus_frame
                if decode_modbus_frame:
                    modbus_frame = self.decode_modbus_frame(data)
                    _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame'] = modbus_frame
                else:
                    hex_list = [f"0x{byte:02x}" for byte in data]
                    _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame'] = hex_list

        if (msg.cmd == mb_protocol.Cmd.CMD_DIAGNOSTICS):
            decoded_cfgs = list()
            for idx, cfg in enumerate(_dict['payload']['payload_answer_frame']['diagnostics_ans_frame']['modbus_configurations']):
                cfg = self.decode_modbus_p_config(cfg['configuration'])
                cfg['id'] = idx + 1
                decoded_cfgs.append(cfg)
            _dict['payload']['payload_answer_frame']['diagnostics_ans_frame']['modbus_configurations'] = decoded_cfgs
        logging.info(json.dumps(_dict, indent=2))

    @property
    def device_mode(self):
        return self._device_mode

    @device_mode.setter
    def device_mode(self, value):
        if (value == 0):
            value = mb_enums.MODBUS_MODE_MASTER
        elif (value == 1):
            value = mb_enums.MODBUS_MODE_SNIFFER
        else:
            raise ValueError("Unsupported device mode!")
        self._device_mode = value

    @property
    def antenna_config(self):
        return self._antenna_config

    @antenna_config.setter
    def antenna_config(self, value):
        if (value == 0):
            value = mb_enums.ANTENNA_INTERNAL
        elif (value == 1):
            value = mb_enums.ANTENNA_EXTERNAL
        else:
            raise ValueError("Unsupported antenna config!")
        self._antenna_config = value

    @property
    def target_port(self):
        return self._target_port

    @target_port.setter
    def target_port(self, value):
        # PORT_ZERO -> Port 1 (Channel 1)
        if (value == 1):
            value = mb_enums.MODBUS_PORT_ZERO
        # PORT_ONE -> Port 2 (Channel 2)
        elif (value == 2):
            value = mb_enums.MODBUS_PORT_ONE
        else:
            raise ValueError("Unsupported port index!")
        self._target_port = value

    @property
    def baudrate_config(self):
        return self._baudrate_config

    @baudrate_config.setter
    def baudrate_config(self, value):
        if (value > mb_enums.PortBaud.PORT_BAUD_115200):
            # Identified as baudrate
            if (value == 4800):
                value = mb_enums.PortBaud.PORT_BAUD_4800
            elif (value == 9600):
                value = mb_enums.PortBaud.PORT_BAUD_9600
            elif (value == 19200):
                value = mb_enums.PortBaud.PORT_BAUD_19200
            elif (value == 28800):
                value = mb_enums.PortBaud.PORT_BAUD_28800
            elif (value == 38400):
                value = mb_enums.PortBaud.PORT_BAUD_38400
            elif (value == 57600):
                value = mb_enums.PortBaud.PORT_BAUD_57600
            elif (value == 76800):
                value = mb_enums.PortBaud.PORT_BAUD_76800
            elif (value == 115200):
                value = mb_enums.PortBaud.PORT_BAUD_115200
            else:
                raise ValueError("Unsupported baudrate config!")
        else:
            raise ValueError("Unsupported baudrate config!")
        # Store proto enum
        self._baudrate_config = value

    @property
    def stop_bits(self):
        return self._stop_bits

    @stop_bits.setter
    def stop_bits(self, value):
        if (value == 1):
            value = mb_enums.PortStopBits.PORT_STOP_BITS_1
        elif (value == 2):
            value = mb_enums.PortStopBits.PORT_STOP_BITS_2
        else:
            raise ValueError("Unsupported stop bits value!")
        self._stop_bits = value

    @property
    def parity_bit(self):
        return self._parity_bit

    @parity_bit.setter
    def parity_bit(self, value):
        if (value == 0):
            value = mb_enums.PortParity.PORT_PARITY_NONE
        elif (value == 1):
            value = mb_enums.PortParity.PORT_PARITY_ODD
        elif (value == 2):
            value = mb_enums.PortParity.PORT_PARITY_EVEN
        else:
            raise ValueError("Unsupported parity bit value!")
        self._parity_bit = value
