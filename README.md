# Wireless Modbus Bridge Controller

Wireless Modbus Bridge Controller is a reference software of how to use and manage Wireless Modbus Bridge device. It provides a dedicated `WMBController` interface which can be used in standalone application to manually send out configuration and Modbus data to the device or it can be integrated into a 3rd party software.

## Usage

Install WMBC via `pip`:

    pip install wmbc

Example commands to use it in a manual standalone workflow:

* Getting diagnostic data from a device:
`python -m wmbc --cmd diag --dst-addr <addr>`
* Reseting a device:
`python -m wmbc --cmd reset --dst-addr <addr>`
* Switching between internal/external antenna:
`python -m wmbc --cmd ant_cfg --dst-addr <addr> --ant-cfg <0/1>`
* Modbus Port configuration
`python -m wmbc --cmd port_cfg --dst-addr <addr> --port-cfg <baud> <parity> <stop bits> --target-port <port id>`

For more details please check: `python -m wmbc --help`
For integration examples please check `examples` directory in this repository.

For more details about your commercial deployment please reach out: [support.cthings.co](https://cthings.atlassian.net/servicedesk/customer/portals)
