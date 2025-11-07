import argparse
import json
import struct
import threading
import logging
from wirepas_mqtt_library import WirepasNetworkInterface
import wirepas_mesh_messaging as wmm
import wmbc.mb_proto.mb_protocol_pb2 as mb_protocol
import wmbc.mb_proto.mb_protocol_answers_pb2 as mb_answers
from wmbc.mb_proto.mb_protocol_iface import MBProto
from google.protobuf.json_format import MessageToJson
from pymodbus.client import ModbusFrameGenerator
from pymodbus.framer import FramerType

callback_event = threading.Event()

def mbd_to_float(input: bytes | bytearray | list[int]) -> float:
    assert len(input) == 4
    # parse with endianness: BACD (here, inverted to CDAB)
    return struct.unpack("<f", bytes([input[2], input[3], input[0], input[1]]))[0]

def on_uplink_data_transmitted(data):
    _mbproto = MBProto()
    _ret, _err, _msg = _mbproto.decode_response(data.data_payload)
    _json_str = MessageToJson(_msg, always_print_fields_with_no_presence=True, preserving_proto_field_name=True)
    _dict = json.loads(_json_str)
    if (_msg.cmd == mb_protocol.Cmd.CMD_MODBUS_ONE_SHOT or _msg.cmd == mb_protocol.Cmd.CMD_MODBUS_PERIODICAL):
        if (_msg.payload.payload_answer_frame.ack_frame.acknowladge == mb_answers.Acknowladge.ACKNOWLADGE_UNKNOWN):
            _modbus_data = _msg.payload.payload_answer_frame.modbus_response_frame.modbus_frame
            _modbus_frame = _mbproto.decode_modbus_frame(_modbus_data)
            _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame'] = _modbus_frame
        elif(_msg.payload.payload_answer_frame.ack_frame.acknowladge == mb_answers.Acknowladge.ACKNOWLADGE_ACK):
            logging.info("Configuration added")
            callback_event.set()
    if (_msg.payload.payload_answer_frame.modbus_response_frame.configuration_index == 1):
        if 'modbus_response_frame' in _dict['payload']['payload_answer_frame']:
            if 'ReadInputRegistersResponse' in _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']:
                _result = _dict['payload']['payload_answer_frame']['modbus_response_frame']['modbus_frame']['ReadInputRegistersResponse']['registers']
                _result_bytes: bytearray = bytearray()
                for val in _result:
                    _val_bytes: bytes = val.to_bytes(length=2, byteorder="little")
                    _result_bytes.extend(_val_bytes)
                _result_float: float = mbd_to_float(input=_result_bytes)
                logging.info("Voltage is: %f [V]", _result_float)

def set_configuration(modbus_frame: bytes, config_index: int, interval_seconds: int, serial_port: int):
    mbproto = MBProto()
    mbproto.target_port = serial_port
    payload_coded = mbproto.create_modbus_periodic(config_index, interval_seconds, modbus_frame)
    try:
        res = wni.send_message(args.gw, args.sink, args.node, 77, 66, payload_coded)
        if res != wmm.GatewayResultCode.GW_RES_OK:
            print("Cannot send data to %s:%s res=%s" % (args.gw, args.sink, res))
    except TimeoutError:
        print("Cannot send data to %s:%s", args.gw, args.sink)

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
    parser.add_argument('--modbus-interval',
                        required=False,
                        type=int,
                        default=120,
                        help='Interval in seconds')

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

    for i in range(1, 9):
        callback_event.clear()
        if i == 1:
            modbus_frame = generator.read_input_registers(address=0x00, count=2)
        elif i == 2:
            modbus_frame = generator.read_input_registers(address=0x06, count=2)
        elif i == 3:
            modbus_frame = generator.read_input_registers(address=0x0b, count=18)
        elif i == 4:
            modbus_frame = generator.read_input_registers(address=0x24, count=2)
        elif i == 5:
            modbus_frame = generator.read_input_registers(address=0x46, count=2)
        elif i == 6:
            modbus_frame = generator.read_input_registers(address=0x48, count=8)
        elif i == 7:
            modbus_frame = generator.read_input_registers(address=0x56, count=2)
        elif i == 8:
            modbus_frame = generator.read_input_registers(address=0x156, count=4)
        set_configuration(modbus_frame, i, args.modbus_interval, args.target_port)
        callback_event.wait()

    logging.info("Entering infinite polling, press Ctrl+C to exit")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Loop interrupted by user.")