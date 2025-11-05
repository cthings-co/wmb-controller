import argparse
import json
import string
import logging
from wirepas_mqtt_library import WirepasNetworkInterface
import wirepas_mesh_messaging as wmm
import wmbc.mb_proto.mb_protocol_pb2 as mb_protocol
from wmbc.mb_proto.mb_protocol_iface import MBProto
from google.protobuf.json_format import MessageToJson
from pymodbus.client import ModbusFrameGenerator
from pymodbus.framer import FramerType

def on_uplink_data_transmitted(data):
    _mbproto = MBProto()
    _ret, _err, _msg = _mbproto.decode_response(data.data_payload)
    _json_str = MessageToJson(_msg, always_print_fields_with_no_presence=True, preserving_proto_field_name=True)
    _dict = json.loads(_json_str)
    if (_msg.cmd == mb_protocol.Cmd.CMD_MODBUS_ONE_SHOT or _msg.cmd == mb_protocol.Cmd.CMD_MODBUS_PERIODICAL):
        if (_msg.payload.payload_answer_frame.ack_frame.acknowladge == 0):
            _modbus_data = _msg.payload.payload_answer_frame.modbus_response_frame.modbus_frame
            _modbus_frame = _mbproto.decode_modbus_frame(_modbus_data)
            _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame'] = _modbus_frame
    if 'modbus_response_frame' in _dict['payload']['payload_answer_frame']:
        if 'ReadHoldingRegistersResponse' in _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']:
            _result = _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']['ReadHoldingRegistersResponse']['registers']
            logging.info("Holding registers: %s", _result)
        elif 'ReadCoilsResponse' in _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']:
            _result = _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']['ReadCoilsResponse']['bits']
            logging.info("LED is " + ("on" if _result[0] else "off"))
        elif 'WriteMultipleRegistersResponse' in _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']:
            _result = _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']['WriteMultipleRegistersResponse']['count']
            logging.info("Wrote %d registers", _result)
        elif 'WriteSingleCoilResponse' in _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']:
            _result = _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']['WriteSingleCoilResponse']['bits']
            logging.info("LED set to " + ("on" if _result else "off"))

def regs_type(value):
    if len(value) > 8:
        raise argparse.ArgumentTypeError("Regs must be up to characters long")
    if not all(c in string.ascii_letters + string.digits for c in value):
        raise argparse.ArgumentTypeError("Regs must contain only ASCII letters and digits")
    return value

if __name__ == "__main__":
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument('--host',
                        required=True,
                        help="MQTT broker address")
    parser.add_argument('--port',
                        required=False,
                        default=8883,
                        type=int,
                        help="MQTT broker port")
    parser.add_argument('--username', 
                        required=False,
                        default='mqttmasteruser',
                        help="MQTT broker username")
    parser.add_argument('--password',
                        required=True,
                        help="MQTT broker password")
    parser.add_argument('--insecure',
                        required=False,
                        dest='insecure',
                        action='store_true',
                        help="MQTT use unsecured connection")
    parser.add_argument('--gw',
                        required=True,
                        help="GW ID")
    parser.add_argument('--sink',
                        required=False,
                        default='sink0',
                        help="Sink ID")
    parser.add_argument('--node',
                        required=False,
                        default=21,
                        help="Node address")
    parser.add_argument('--modbus-addr',
                        required=False,
                        type=int,
                        default=1,
                        help='Modbus slave address')
    parser.add_argument('--target-port',
                        required=False,
                        type=int,
                        choices=[1, 2],
                        default=1,
                        help='Target port: 1 - Port 1, 2 - Port 2')
    parser.add_argument('--cmd',
                        required=True,
                        type=str,
                        choices=['write_coil', 'read_coil', 'write_regs', 'read_regs'],
                        help='Command Types')
    parser.add_argument('--led-num',
                        required=False,
                        type=int,
                        choices=[0, 1, 2],
                        help='LED number')
    parser.add_argument('--led-val',
                        required=False,
                        type=int,
                        choices=[0, 1],
                        help='LED value')
    parser.add_argument('--regs',
                        required=False,
                        type=regs_type,
                        help='Regs value')

    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO)

    wni = WirepasNetworkInterface(args.host,
                                  args.port,
                                  args.username,
                                  args.password,
                                  insecure=args.insecure)
    
    # Register a callback for uplink traffic
    wni.register_uplink_traffic_cb(on_uplink_data_transmitted, gateway=args.gw, sink=args.sink, src_ep = 66, dst_ep = 77)

    generator = ModbusFrameGenerator(framer=FramerType.RTU, slave=args.modbus_addr)

    if args.cmd == "write_coil":
        if args.led_num is None or args.led_val is None:
            parser.error("Both --led-num and --led-val arguments are required")
        led_value = args.led_val == 1
        modbus_frame = generator.write_coil(args.led_num, led_value)
    elif args.cmd == "read_coil":
        if args.led_num is None:
            parser.error("Argument --led-num is required")
        modbus_frame = generator.read_coils(args.led_num)
    elif args.cmd == "write_regs":
        if args.regs is None:
            parser.error("Argument --regs is required")
        modbus_frame = generator.write_registers(0, args.regs.encode('utf-8'))
    elif args.cmd == "read_regs":
        modbus_frame = generator.read_holding_registers(0, count=8)

    mbproto = MBProto()

    mbproto.target_port = args.target_port
    payload_coded = mbproto.create_modbus_oneshot(modbus_frame)

    try:
        res = wni.send_message(args.gw, args.sink, args.node, 77, 66, payload_coded)
        if res != wmm.GatewayResultCode.GW_RES_OK:
            print("Cannot send data to %s:%s res=%s" % (args.gw, args.sink, res))
    except TimeoutError:
        print("Cannot send data to %s:%s", args.gw, args.sink)

    logging.info("Entering infinite polling, press Ctrl+C to exit")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Loop interrupted by user.")