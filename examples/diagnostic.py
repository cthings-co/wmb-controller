import argparse
import asyncio
import logging
import json
import mbproto.mb_protocol_pb2 as mb_protocol
from mbproto.mb_protocol_iface import MBProto
from google.protobuf.json_format import MessageToJson
from wmbc.wmbc import WMBController

logging.basicConfig(level=logging.INFO)

async def main():
    parser = argparse.ArgumentParser(description='Example of running diagnostics status periodically')
    parser.add_argument(
        '--dst-addr',
        required=False,
        type=int,
        default=21,
        help='Wirepas destination address'
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

    args_dict.update({'cmd':"diag"})

    WMBC = WMBController(**args_dict)
    WMBC.initialize_sink()
    await WMBC.run_periodically(period=args_dict.get('period'), print_default=True)

if __name__ == "__main__":
    asyncio.run(main())
