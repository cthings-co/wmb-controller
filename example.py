from wmb_protocol import decode_response, create_device_reset
from wmb_protocol import print_hex_bytes
# Print hex bytes of device reset command
print_hex_bytes(create_device_reset())
# Test data to decode
test_data = "\x08\x47\x10\x01\x18\x01\x2a\x04\x0a\x02\x0a\x00\xef\x30"

# Convert string to bytes
frame = test_data.encode('latin1')

# Decode the message
success, error, message = decode_response(frame)

if success:
    print(f"Successfully decoded message: {message}")
else:
    print(f"Error decoding message: {error}")

