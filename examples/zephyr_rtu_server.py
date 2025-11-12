import argparse
import asyncio
import logging
import mbproto.mb_protocol_pb2 as mb_protocol
from mbproto.mb_protocol_iface import MBProto
from pymodbus.client import ModbusFrameGenerator
from pymodbus.framer import FramerType
from wmbc.wmbc import WMBController


logging.basicConfig(level=logging.INFO)


async def main():
    parser = argparse.ArgumentParser(description='Zephyr RTU Server demo for WMB Controller - LEDs control over Wirepas \
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
            required=True,
            type=int,
            choices=[1, 2],
            default=1,
            help='Target port: 1 - Port 1, 2 - Port 2'
    )
    parser.add_argument(
            '--led-num',
            required=True,
            type=int,
            choices=[0, 1, 2],
            help='LED number'
    )
    parser.add_argument(
            '--led-val',
            required=True,
            type=int,
            choices=[0, 1],
            help='LED value'
    )

    args = parser.parse_args()
    args_dict = vars(args)

    generator = ModbusFrameGenerator(framer=FramerType.RTU, slave=args_dict.get('modbus_addr'))
    led_value = args.led_val == 1
    write_led_frame = generator.write_coil(args.led_num, led_value)
    args_dict.update({'cmd':"modbus_1s", 'modbus_frame':write_led_frame})

    WMBC = WMBController(**args_dict)
    await WMBC.run()


if __name__ == "__main__":
    asyncio.run(main())
