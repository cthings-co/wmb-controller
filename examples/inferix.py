import argparse
import asyncio
import logging
import json
import wmbc.mb_proto.mb_protocol_pb2 as mb_protocol
from wmbc.mb_proto.mb_protocol_iface import MBProto
from google.protobuf.json_format import MessageToJson
from pymodbus.client import ModbusFrameGenerator
from pymodbus.framer import FramerType
from wmbc.wmbc import WMBController

def print_answer(msg: mb_protocol.MbMessage, voltage_range: list) -> None:
    _mbproto = MBProto()
    _json_str = MessageToJson(msg, always_print_fields_with_no_presence=True, preserving_proto_field_name=True)
    _dict = json.loads(_json_str)
    if (msg.cmd == mb_protocol.Cmd.CMD_MODBUS_ONE_SHOT or msg.cmd == mb_protocol.Cmd.CMD_MODBUS_PERIODICAL):
        if (msg.payload.payload_answer_frame.ack_frame.acknowladge == 0):
            data = msg.payload.payload_answer_frame.modbus_response_frame.modbus_frame
            modbus_frame = _mbproto.decode_modbus_frame(data)
            _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame'] = modbus_frame

    if 'ReadHoldingRegistersResponse' in _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']:
        ai_regs = _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']['ReadHoldingRegistersResponse']['registers']
        for iter in range(4):
            logging.info("AI %d is: %f V",iter+1, (ai_regs[iter]*voltage_range[iter])/(2 ** 10))

async def main():
    parser = argparse.ArgumentParser(description='Inferix WIN-IO-4AIM demo for WMB Controller - reads AI voltage values over Wirepas \
        (assumes the Sink is preconfigured with correct Network Address and Channel).')
    parser.add_argument(
        '--wirepas-addr',
        required=False,
        type=int,
        default=2,
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
            choices=[0, 1],
            default=1,
            help='Target port: 0 - Port 0, 1 - Port 1'
    )
    parser.add_argument(
            '--volt-range',
            required=False,
            nargs=4,
            type=int,
            choices=[5, 10],
            default={10, 10, 10, 10},
            help='Voltage range of AIs'
    )
    parser.add_argument(
            '--period',
            required=False,
            default=20,
            help='Period in seconds'
    )

    args = parser.parse_args()
    args_dict = vars(args)
    logging.info(args_dict)
    generator = ModbusFrameGenerator(framer=FramerType.RTU, slave=args_dict.get('modbus_addr'))
    read_regs_frame = generator.read_holding_registers(address=0, count=4)
    logging.info(read_regs_frame)
    WMBC = WMBController(dst_addr=args_dict.get('wirepas_addr'), cmd="modbus_1s", target_port=args_dict.get('target_port'), modbus_frame=read_regs_frame)
    WMBC.initialize_sink()
    await WMBC.run_periodically(args_dict.get('period'), _callback = print_answer, callback_args=args_dict.get('volt_range'))
if __name__ == "__main__":
    asyncio.run(main())
