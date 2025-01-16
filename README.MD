# WMB Protocol Package

A Python implementation of the WMB protocol for communication with WMB devices.

## Installation

```bash
# Clone the repository
git clone [repository-url]
cd wmb-controller

# Install dependencies
pip install -r requirements.txt
```

## Protocol Buffer Files

The package includes pre-compiled Protocol Buffer files, so it can be used directly after installation. However, if you need to recompile the Protocol Buffer files, you'll need to:

1. Install the Protocol Buffer compiler (protoc):
   - Follow installation instructions at: https://grpc.io/docs/protoc-installation/
   - Make sure protoc is available in your system PATH

2. Run the compilation script:
   ```bash
   # On Windows
   scripts/compile_protos.bat
   
   # On Linux/Mac
   # TODO
   ```

This will regenerate the Protocol Buffer Python files in the `wmb_protocol` directory.


## Project Structure

```
wmb-protocol/
├── wmb_protocol/                 # Main package directory
│   ├── __init__.py              # Package initialization
│   ├── wmb_protocol_decoder.py  # Protocol decoder implementation
│   ├── wmb_protocol_encoder.py  # Protocol encoder implementation
│   ├── mb_protocol_pb2.py       # Generated Protocol Buffer files
│   ├── mb_protocol_commands_pb2.py
│   ├── mb_protocol_answers_pb2.py
│   └── mb_protocol_enums_pb2.py
├── scripts/
│   └── compile_protos.bat       # Script to compile Protocol Buffer files
├── example.py                   # Example usage of the protocol messages generation and decoding
├── wmbc.py                      # Command-line interface implementation
└── README.MD                    # This documentation
```

## Usage Examples

### Basic command generation and decoding (example.py)
```python
from wmb_protocol import decode_response, create_device_reset
from wmb_protocol import print_hex_bytes

# Print hex bytes of device reset command
print_hex_bytes(create_device_reset())

# Test data to decode
test_data = "\x47\x01\x18\x01\x2a\x04\x0a\x02\x0a\x00\xef\x30"
frame = test_data.encode('utf-8')

# Decode the message
success, error, message = decode_response(frame)

if success:
    print(f"Successfully decoded message: {message}")
else:
    print(f"Error decoding message: {error}")
```

## Available Commands
The following commands are available through the wmb_protocol package:

### Device Management Commands
- `create_device_reset()`
  - Generate a device reset command
- `create_diagnostics()`
  - Generate a diagnostics request command
- `create_device_mode(mode: ModbusMode)`
  - Generate a device mode configuration command
  - Available modes:
    - `MODBUS_MODE_MASTER` (0)
    - `MODBUS_MODE_SNIFFER` (1)

### Configuration Commands  
- `create_antenna_config(config: AntennaSettings)`
  - Generate an antenna configuration command
  - Available settings:
    - `ANTENNA_INTERNAL` (0)
    - `ANTENNA_EXTERNAL` (1)

- `create_baudrate_config(port: ModbusPort, baudrate: ModbusBaud)`
  - Generate a baudrate configuration command
  - Available ports:
    - `MODBUS_PORT_ZERO` (1)
    - `MODBUS_PORT_ONE` (2)
  - Available baudrates:
    - `MODBUS_BAUD_4800` (12)
    - `MODBUS_BAUD_9600` (13)
    - `MODBUS_BAUD_19200` (14) 
    - `MODBUS_BAUD_28800` (15)
    - `MODBUS_BAUD_38400` (16)
    - `MODBUS_BAUD_57600` (17)
    - `MODBUS_BAUD_76800` (18)
    - `MODBUS_BAUD_115200` (19)

### Modbus Commands
- `create_modbus_oneshot(port: ModbusPort, modbus_frame: bytes)`
  - Generate a one-shot Modbus command
  - Available ports:
    - `MODBUS_PORT_ZERO` (1)
    - `MODBUS_PORT_ONE` (2)

- `create_modbus_periodic(port: ModbusPort, config_index: int, interval_seconds: int, modbus_frame: bytes)`
  - Generate a periodic Modbus command
  - Available ports:
    - `MODBUS_PORT_ZERO` (1)
    - `MODBUS_PORT_ONE` (2)
  - config_index: Value between 1-64 to identify the periodic configuration
  - interval_seconds: Time between executions (0-2592000 seconds, max 30 days)

### Utility Functions
- `print_hex_bytes(bytes_data: bytes)`
  - Print byte data in hex format
- `decode_response(frame: bytes)` 
  - Decode received protocol messages

For detailed usage of each command, refer to the example.py file.

## License

Apache-2.0 License © 2025 CTHINGS.CO