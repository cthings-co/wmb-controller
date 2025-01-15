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

- `create_device_reset()` - Generate a device reset command
- `create_diagnostics()` - Generate a diagnostics request command
- `create_device_mode()` - Generate a device mode configuration command
- `create_antenna_config()` - Generate an antenna configuration command
- `create_baudrate_config()` - Generate a baudrate configuration command
- `create_modbus_oneshot()` - Generate a one-shot Modbus command
- `create_modbus_periodic()` - Generate a periodic Modbus command
- `print_hex_bytes()` - Utility function to print byte data in hex format
- `decode_response()` - Decode received protocol messages

For detailed usage of each command, refer to the example.py file.

## License

Apache-2.0 License © 2025 CTHINGS.CO