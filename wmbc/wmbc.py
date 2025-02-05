import logging
import os
import sys
import argparse
from time import time, sleep
import asyncio
import signal

from wsctrl.sink_ctrl import SinkController, Nbor
from wmbc.mb_proto import mb_protocol_enums_pb2 as mb_enums
from wmbc.mb_proto.mb_protocol_iface import MBProto


logging.basicConfig(level=logging.INFO)
   

def signal_exit(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_exit)


class WMBController():
    """
    Implementation of WMB controller
    """

    MB_PROTO_SRC_EP = 77
    MB_PROTO_DST_EP = 66

    def __init__(self, **kwargs):

        logging.info("Starting WMB Controller")
        self._cmd_type = kwargs.get("cmd")
        self._dst_addr = kwargs.get("dst_addr")
        self._dev_mode = kwargs.get("dev_mode")
        self._ant_cfg = kwargs.get("ant_cfg")
        self._target_port = kwargs.get("target_port")
        self._port_cfg = kwargs.get("port_cfg")
        self._modbus_file = kwargs.get("modbus_file")
        self._modbus_interval = kwargs.get("modbus_interval")
        self._modbus_cfg_idx = kwargs.get("modbus_cfg_idx")
        self._polling_only = self._cmd_type is None
        if (self._cmd_type != "scan" and self._cmd_type is not None):
            assert self._dst_addr > 0, "Destination address cannot be 0!"
            self._client = SinkController(self._dst_addr & 0xFFFFFFFF, self.MB_PROTO_SRC_EP, self.MB_PROTO_DST_EP)
        else:
            self._client = SinkController(self._dst_addr, pm=True)

        self._mbproto = MBProto()
        if self._cmd_type == "reset":
            self._payload_coded = self._mbproto.create_device_reset()
        elif self._cmd_type == "diag":
            self._payload_coded = self._mbproto.create_diagnostics()
        elif self._cmd_type == "dev_mode":
            self._mbproto.device_mode = self._dev_mode
            self._payload_coded = self._mbproto.create_device_mode()
        elif self._cmd_type == "ant_cfg":
            self._mbproto.antenna_config = self._ant_cfg
            self._payload_coded = self._mbproto.create_antenna_config()
        elif self._cmd_type == "port_cfg":
            self._mbproto.target_port = self._target_port
            self._mbproto.baudrate_config = int(self._port_cfg[0])
            self._mbproto.parity_bit = int(self._port_cfg[1])
            self._mbproto.stop_bits = int(self._port_cfg[2])
            self._payload_coded = self._mbproto.create_port_config()
        elif self._cmd_type == "modbus_1s":
            try:
                with open(self._modbus_file, 'rb') as f:
                    self._payload_coded = f.read()
            except FileNotFoundError:
                raise FileNotFoundError(f"File {self._modbus_file} does not exist!")
            except Exception as e:
                raise e(f"Unhandled exception")
            self._mbproto.target_port = self._target_port
            self._payload_coded = self._mbproto.create_modbus_oneshot(self._payload_coded)
        elif self._cmd_type == "modbus_p":
            try:
                with open(self._modbus_file, 'rb') as f:
                    self._payload_coded = f.read()
            except FileNotFoundError:
                raise FileNotFoundError(f"File {self._modbus_file} does not exist!")
            except Exception as e:
                raise e(f"Unhandled exception")
            self._mbproto.target_port = self._target_port
            self._payload_coded = self._mbproto.create_modbus_periodic(self._modbus_cfg_idx, self._modbus_interval,
                                                                       self._payload_coded)
        elif self._cmd_type != "scan":
            raise ValueError("Unsupported command type!")

    def _stop_sinks(self):
        self._client.deinitialize_sink()

    def _start_sinks(self):
        self._client.initialize_sink()

    def send_command(self):
        if self._client and self._payload_coded:
            self._client.send(self._payload_coded)

    def scan_network(self):
        if self._client:
            self._client.scan_network()
        else:
            logging.warning("Cannot scan network. SinkController not initialized!")

    def initialize_sink(self):
        self._start_sinks()

    def deinitialize_sink(self):
        self._stop_sinks()

    async def run(self):
        if self._cmd_type == "scan":
            self.scan_network()
        elif self._cmd_type is not None:
            self.send_command()

        logging.info("Entering infinite polling, press Ctrl+C to exit")
        while True:
            response = await self._client.async_receive()
            ret, _, msg = self._mbproto.decode_response(response.payload)
            logging.info(msg)


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
