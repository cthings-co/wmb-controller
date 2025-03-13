# Wireless Modbus Bridge Controller

Wireless Modbus Bridge Controller is a reference software of how to use and manage Wireless Modbus Bridge device. It provides a dedicated `WMBController` interface which can be used in standalone application to manually send out configuration and Modbus data to the device or it can be integrated into a 3rd party software.

## Usage on live system

WMBC needs Wirepas `sinkService` running in the background.

System prequisities:

    apt install pkg-config libcairo2-dev libgirepository1.0-dev

For Debian 12 and lower versions pre-install:

    pip install pygobject==3.50

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

## Usage with pre-deployed Wirepas composition

Build docker image:

    cd docker/image && docker build -t wmbc-runner .

Run an example WMBC composition:

    cd docker/examples/wmbc && docker compose up

FOTA (Note: you need a binary provided by CTHINGS.CO):

    cd docker/examples/fota && docker compose up
