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

logging.basicConfig(level=logging.INFO)

def print_answer(msg: mb_protocol.MbMessage, callback_args: dict) -> None:
    voltage_range = callback_args.get('volt_range')
    dev_id = callback_args.get('modbus_addr')
    _mbproto = MBProto()
    _json_str = MessageToJson(msg, always_print_fields_with_no_presence=True, preserving_proto_field_name=True)
    _dict = json.loads(_json_str)
    if (msg.cmd == mb_protocol.Cmd.CMD_MODBUS_ONE_SHOT or msg.cmd == mb_protocol.Cmd.CMD_MODBUS_PERIODICAL):
        if (msg.payload.payload_answer_frame.ack_frame.acknowladge == 0):
            data = msg.payload.payload_answer_frame.modbus_response_frame.modbus_frame
            try:
                modbus_frame = _mbproto.decode_modbus_frame(data)
            except Exception as e:
                logging.error("Faild to decode Modbus Frame")
            else:
                _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame'] = modbus_frame
    if 'modbus_response_frame' in _dict['payload']['payload_answer_frame']:
        if 'ReadHoldingRegistersResponse' in _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']:
            if _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']['ReadHoldingRegistersResponse']['dev_id'] == dev_id:
                ai_regs = _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']['ReadHoldingRegistersResponse']['registers']
                if len(ai_regs) >= 4:
                    for iter in range(4):
                        logging.info("AI %d is: %f V",iter+1, (ai_regs[iter]*voltage_range[iter])/(2 ** 10))

async def main():
    parser = argparse.ArgumentParser(description='Inferix WIN-IO-4AIM demo for WMB Controller - reads AI voltage values over Wirepas \
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
            '--volt-range',
            required=False,
            nargs=4,
            type=int,
            choices=[5, 10],
            default=[10, 10, 10, 10],
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

    generator = ModbusFrameGenerator(framer=FramerType.RTU, slave=args_dict.get('modbus_addr'))
    read_regs_frame = generator.read_holding_registers(address=0, count=4)

    args_dict.update({'cmd':"modbus_1s", 'modbus_frame':read_regs_frame})
    callback_args_dict = {}
    callback_args_dict.update({'modbus_addr': args_dict['modbus_addr'], 'volt_range': args_dict['volt_range']})

    WMBC = WMBController(**args_dict)
    WMBC.initialize_sink()
    await WMBC.run_periodically(args_dict.get('period'), _callback = print_answer, callback_args = callback_args_dict)

if __name__ == "__main__":
    asyncio.run(main())
