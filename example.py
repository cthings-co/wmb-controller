from wmb_protocol import decode_response, create_device_reset
from wmb_protocol import print_hex_bytes
from wmb_protocol import ModbusPort, ModbusBaud, create_baudrate_config

# Print hex bytes of device reset command
print_hex_bytes(create_device_reset())

# Print hex bytes of baudrate config command for Port 1 at 9600 baud
print_hex_bytes(create_baudrate_config(ModbusPort.MODBUS_PORT_ONE, ModbusBaud.MODBUS_BAUD_9600))

# Test data to decode
test_data = b'\x08\x47\x10\x01\x18\x01\x2a\x04\x0a\x02\x0a\x00\xef\x30'
frame = test_data  # No encoding needed

# Decode the message
success, error, message = decode_response(frame)

if success:
    print(f"Successfully decoded message: {message}")
else:
    print(f"Error decoding message: {error}")

