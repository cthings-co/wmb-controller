import argparse
import asyncio
from wmbc.wmbc import WMBController

async def main():
    """
        Main for WMB Controller
    """

    parser = argparse.ArgumentParser(description='WMB Controller - sends out MB Protocol requests over Wirepas \
            (assumes the Sink is preconfigured with correct Network Address and Channel).')
    parser.add_argument(
        '--dst-addr',
        required=False,
        type=int,
        default=0,
        help='Destination address'
    )
    parser.add_argument(
        '--cmd',
        required=False,
        type=str,
        choices=['scan', 'reset', 'diag', 'dev_mode', 'ant_cfg', 'port_cfg', 'modbus_1s', 'modbus_p'],
        help='Command Types'
    )
    parser.add_argument(
            '--dev-mode',
            required=False,
            type=int,
            choices=[0, 1],
            help='Device mode: 0 - Modbus Master, 1 - Modbus Sniffer'
    )
    parser.add_argument(
            '--ant-cfg',
            required=False,
            type=int,
            choices=[0, 1],
            help='Antenna config: 0 - Internal Antenna, 1 - External Antenna'
    )
    parser.add_argument(
            '--target-port',
            required=False,
            type=int,
            choices=[0, 1],
            help='Target port: 0 - Port 0, 1 - Port 1; Use it with port-cfg or modbus commands'
    )
    parser.add_argument(
            '--port-cfg',
            required=False,
            nargs=3,
            help='Port Serial configuration: <baudrate> <parity (0 - none, 1 - odd, 2 - even)> <stop_bits (1 or 2)>'
    )
    parser.add_argument(
            '--modbus-file',
            required=False,
            type=str,
            help='File with binary modbus frame needed for modbus_1s or modbus_p commands'
    )
    parser.add_argument(
            '--modbus-cfg-idx',
            required=False,
            type=int,
            help='Config index for periodic modbus frame'
    )
    parser.add_argument(
            '--modbus-interval',
            required=False,
            type=int,
            help='Interval for periodic modbus frame'
    )
    args = parser.parse_args()
    args_dict = vars(args)

    WMBC = WMBController(**args_dict)
    WMBC.initialize_sink()
    await WMBC.run()

if __name__ == "__main__":
    asyncio.run(main())
