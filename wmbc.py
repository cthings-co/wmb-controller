import logging
import os
import sys
import argparse
from time import time, sleep

from wirepas_gateway.dbus.dbus_client import BusClient
from wirepas_gateway import __pkg_name__
import mb_protocol_enums_pb2 as mb_enums
from encoding import (
    create_device_reset,
    create_diagnostics,
    create_device_mode,
    create_antenna_config,
    create_baudrate_config,
    create_modbus_oneshot,
    create_modbus_periodic
)

from decoding import decode_response


EP_SRC_MAP = {
        "ping":   1,
        "stress-test":   1,
        "modbus": 64,
        "ctrl":   200,
        "fota":   201,
        "mb-command": 64,
}

EP_DST_MAP = {
        "ping": 1,
        "stress-test": 1,
        "mb-command": 64,
}


class Nbor():
    def __init__(self, nbor_tuple, **kwargs):
        self.address = nbor_tuple[0]
        self.link_rel = nbor_tuple[1]
        self.norm_rssi = nbor_tuple[2]
        self.cost = nbor_tuple[3]
        self.channel = nbor_tuple[4]
        self.nbor_type = nbor_tuple[5]
        self.tx_power = nbor_tuple[6]
        self.rx_power = nbor_tuple[7]
        self.last_update = nbor_tuple[8]

    def dump_info(self):
        logging.info("Address: {} | Link_rel: {} | RSSI: {} | Cost: {} | Channel: {} | Type: {} | TX_power: {} | RX_power: {} | Last_update: {}".format(self.address, self.link_rel, self.norm_rssi, self.cost, self.channel, self.nbor_type, self.tx_power, self.rx_power, self.last_update))


class WMBController(BusClient):
    """
    Implementation of WMB controller
    """

    # Maximum hop limit to send a packet is limited to 15 by API (4 bits)
    MAX_HOP_LIMIT = 15
    DEFAULT_QOS = 0

    def __init__(self, dst_addr, payload_coded, cmd_type=None, qos=0, initial_delay_ms=0,
                 is_unack_csma_ca=False, hop_limit=MAX_HOP_LIMIT, **kwargs):
        logging.info("Starting WMB Controller")

        super(WMBController, self).__init__(
            c_extension=True,
            **kwargs
        )
        self.dst_addr = dst_addr
        self.cmd_type = cmd_type
        self.qos = qos
        self.initial_delay_ms = initial_delay_ms
        self.is_unack_csma_ca = is_unack_csma_ca
        self.hop_limit = hop_limit
        self.polling_only = (self.cmd_type is None or self.cmd_type == "scan")
        self.nbors = []
        if (not self.polling_only):
            self.src_ep = EP_SRC_MAP[self.cmd_type]
            self.dst_ep = EP_DST_MAP[self.cmd_type]
            self.payload_coded = payload_coded

    def _stop_sinks(self):
        for sink in self.sink_manager.get_sinks():
            sink.write_config({"started": False})

    def _start_sinks(self):
        for sink in self.sink_manager.get_sinks():
            sink.write_config({"started": True})

    def send(self, payload_coded):
        for sink in self.sink_manager.get_sinks():
            res = sink.send_data(
                self.dst_addr,
                self.src_ep,
                self.dst_ep,
                self.qos,
                self.initial_delay_ms,
                payload_coded,
                self.is_unack_csma_ca,
                self.hop_limit
            )

    def scan_network(self):
        for sink in self.sink_manager.get_sinks():
            res = sink.start_scan()
            if (res == 1):
                for nbor in sink.get_nbors():
                    self.nbors.append(Nbor(nbor))

        logging.info("Detected Neighbors:")
        for n in self.nbors:
            n.dump_info()

    def on_data_received(
        self,
        sink_id,
        timestamp,
        src,
        dst,
        src_ep,
        dst_ep,
        travel_time,
        qos,
        hop_count,
        data,
    ):
        logging.debug("Received data: from {} dst: {} EP: {}->{}".format(src, dst, src_ep, dst_ep))
        
        # Decode response using decode_response
        success, error_msg, decoded_msg = decode_response(data)
        
        if success:
            logging.info("Decoded message: {}".format(decoded_msg))
        else:
            logging.error("Failed to decode message: {}".format(error_msg))
            
        if (self.cmd_type == "ping"):
            try:
                strdata = data.decode('utf-8')
                if (strdata == "pong"):
                    logging.info("Got pong! Exiting...")
                    self.loop.quit()
            except:
                pass

    def initialize_sink(self):
        self._start_sinks()

    def deinitialize_sink(self):
        self._stop_sinks()

    def launch(self):
        if (self.polling_only):
            # Only poll for messages
            self.run()
        else:
            # Send out command
            self.send(self.payload_coded)
            # Wait for response
            self.run()


def main():
    """
        Main for WMB Controller
    """

    parser = argparse.ArgumentParser(description='WMB Controller')
    parser.add_argument(
        '--dst-addr',
        required=False,
        type=int,
        help='Destination address'
    )
    parser.add_argument(
        '--cmd-type',
        required=False,
        type=str,
        help='Command Type (auto-selects EPs): "ping", "modbus", "ctrl", "fota", "stress-test", "scan", "mb-command"'
    )
    args = parser.parse_args()

    if (args.cmd_type is not None and args.cmd_type != "scan"):
        assert args.cmd_type in EP_SRC_MAP.keys(), "Invalid command type!"
        if (args.cmd_type == "ping"):
            payload_coded = "ping".encode('utf-8')
        elif (args.cmd_type == "modbus"):
            assert False, "Not supported"
        elif (args.cmd_type == "ctrl"):
            assert False, "Not supported"
        elif (args.cmd_type == "fota"):
            assert False, "Not supported"
        elif (args.cmd_type == "mb-command"):
            # Create a device reset command as an example
            payload_coded = create_device_reset()
        elif (args.cmd_type == "stress-test"):
            payload = str()
            for i in range(0, 1023):
                payload += 'x'
            payload += 'T'
            payload_coded = payload.encode('utf-8')
    else:
        payload_coded = None

    # Set default debug level
    debug_level = "info"
    try:
        debug_level = os.environ["WM_DEBUG_LEVEL"]
    except KeyError:
        pass

    debug_level = "{0}".format(debug_level.upper())

    # enable its logger
    logging.basicConfig(
        format=f'%(asctime)s | [%(levelname)s] {__pkg_name__}@%(filename)s:%(lineno)d:%(message)s',
        level=debug_level,
        stream=sys.stdout
    )

    WMBC = WMBController(args.dst_addr, payload_coded, cmd_type=args.cmd_type)
    WMBC.initialize_sink()
    if (args.cmd_type == "scan"):
        WMBC.scan_network()
    else:
        WMBC.launch()

if __name__ == "__main__":
    main()
