import argparse
import asyncio
import logging
import json
import struct
import mbproto.mb_protocol_pb2 as mb_protocol
from mbproto.mb_protocol_iface import MBProto
from google.protobuf.json_format import MessageToJson
from pymodbus.client import ModbusFrameGenerator
from pymodbus.framer import FramerType
from wmbc.wmbc import WMBController

logging.basicConfig(level=logging.INFO)


def mbd_to_float(input: bytes | bytearray | list[int]) -> float:
    assert len(input) == 4
    # parse with endianness: BACD (here, inverted to CDAB)
    return struct.unpack("<f", bytes([input[2], input[3], input[0], input[1]]))[0]

def print_answer(msg: mb_protocol.MbMessage, args: None) -> None:
    _mbproto = MBProto()
    _json_str = MessageToJson(msg, always_print_fields_with_no_presence=True, preserving_proto_field_name=True)
    _dict = json.loads(_json_str)
    if (msg.cmd == mb_protocol.Cmd.CMD_MODBUS_ONE_SHOT or msg.cmd == mb_protocol.Cmd.CMD_MODBUS_PERIODICAL):
        if (msg.payload.payload_answer_frame.ack_frame.acknowladge == 0):
            data = msg.payload.payload_answer_frame.modbus_response_frame.modbus_frame
            modbus_frame = _mbproto.decode_modbus_frame(data)
            _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame'] = modbus_frame
    if 'modbus_response_frame' in _dict['payload']['payload_answer_frame']:
        if 'ReadInputRegistersResponse' in _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']:
            result = _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']['ReadInputRegistersResponse']['registers']
            result_bytes: bytearray = bytearray()
            for val in result:
                val_bytes: bytes = val.to_bytes(length=2, byteorder="little")
                result_bytes.extend(val_bytes)
            result_float: float = mbd_to_float(input=result_bytes)
            logging.info("Voltage is: %f [V]", result_float)

async def main():
    parser = argparse.ArgumentParser(description='LE 01MQ demo for WMB Controller - reads AI voltage values over Wirepas \
        (assumes the Sink is preconfigured with correct Network Address and Channel).')
    parser.add_argument(
        '--dst-addr',
        required=False,
        type=int,
        default=21,
        help='Wirepas destination address'
    )
    parser.add_argument(
        '--modbus-addr',
        required=False,
        type=int,
        default=1,
        help='Modbus slave address'
    )
    parser.add_argument(
            '--target-port',
            required=False,
            type=int,
            choices=[1, 2],
            default=1,
            help='Target port: 1 - Port 1, 2 - Port 2'
    )
    parser.add_argument(
            '--period',
            required=False,
            type=int,
            default=20,
            help='Period in seconds'
    )

    args = parser.parse_args()
    args_dict = vars(args)

    generator = ModbusFrameGenerator(framer=FramerType.RTU, slave=args_dict.get('modbus_addr'))
    # Read out Amperes
    read_regs_frame = generator.read_input_registers(address=0x0, count=2)

    args_dict.update({'cmd':"modbus_1s", 'modbus_frame':read_regs_frame})

    WMBC = WMBController(**args_dict)
    WMBC.initialize_sink()
    await WMBC.run_periodically(args_dict.get('period'), _callback = print_answer)

if __name__ == "__main__":
    asyncio.run(main())
