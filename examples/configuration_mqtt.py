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
    _mbproto.print_decoded_msg(data.data_payload)


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
                        help='Target port: 1 - Port 1, 2 - Port 2')
    parser.add_argument('--cmd',
                        required=True,
                        type=str,
                        choices=['reset', 'diag', 'dev_mode', 'ant_cfg', 'port_cfg'],
                        help='Command Types')
    parser.add_argument('--dev-mode',
                        required=False,
                        type=int,
                        choices=[0, 1],
                        help='Device mode: 0 - Modbus Master, 1 - Modbus Sniffer')
    parser.add_argument('--ant-cfg',
                        required=False,
                        type=int,
                        choices=[0, 1],
                        help='Antenna config: 0 - Internal Antenna, 1 - External Antenna')
    parser.add_argument('--port-cfg',
                        required=False,
                        nargs=3,
                        help='Port Serial configuration: <baudrate> <parity (0 - none, 1 - odd, 2 - even)> <stop_bits (1 or 2)>')

    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO)

    wni = WirepasNetworkInterface(args.host,
                                  args.port,
                                  args.username,
                                  args.password,
                                  insecure=args.insecure)
    
    # Register a callback for uplink traffic
    wni.register_uplink_traffic_cb(on_uplink_data_transmitted, gateway=args.gw, sink=args.sink, src_ep = 66, dst_ep = 77)

    mbproto = MBProto()

    if args.cmd == "reset":
        payload_coded = mbproto.create_device_reset()
    elif args.cmd == "diag":
        payload_coded = mbproto.create_diagnostics()
    elif args.cmd == "dev_mode":
        if args.dev_mode is None:
            parser.error("Argument --dev-mode is required")
        mbproto.device_mode = args.dev_mode
        payload_coded = mbproto.create_device_mode()
    elif args.cmd == "ant_cfg":
        if args.ant_cfg is None:
            parser.error("Argument --ant-cfg is required")
        mbproto.antenna_config = args.ant_cfg
        payload_coded = mbproto.create_antenna_config()
    elif args.cmd == "port_cfg":
        if args.target_port is None or args.port_cfg is None:
            parser.error("Both --target-port and --port-cfg are required")
        try:
            mbproto.target_port = args.target_port
            mbproto.baudrate_config = int(args.port_cfg[0])
            mbproto.parity_bit = int(args.port_cfg[1])
            mbproto.stop_bits = int(args.port_cfg[2])
        except ValueError as e:
            parser.error(e)
        payload_coded = mbproto.create_port_config()

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