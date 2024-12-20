import mb_protocol_pb2 as mb_protocol
import mb_protocol_enums_pb2 as mb_protocol_enums
from crccheck.crc import Crc16Dds110
message = mb_protocol.MbMessage()

# # Set the basic fields
# message.header = 0x47
# message.version = 0x01
# message.cmd = mb_protocol.Cmd.CMD_DEV_RESET



# try:
#     serialized_message = message.SerializeToString()
#     print("Serialized message:", serialized_message)

#     new_message = mb_protocol.MbMessage()
#     new_message.ParseFromString(serialized_message)
#     print("Deserialized message:", new_message)
# except Exception as e:
#     print(f"Error: {e}")

# Test with specific hex data
#hex_string = "08 47 10 01 18 07 2a 0c 12 0a 1a 08 10 01 22 04 00 00 00 00"
# test_data = "\x08G\x10\x01\x18\x01*\x02\n\x00X\xfd"
test_data = "\x08\x47\x10\x01\x18\x01\x2a\x04\x0a\x02\x0a\x00\xef\x30"

# Separate message data from CRC
message_data = test_data[:-2].encode('latin1')  # Convert to bytes immediately
crc_bytes = test_data[-2:].encode('latin1')    # Convert to bytes immediately

print("Message data:", message_data)
print("CRC bytes:", crc_bytes)

try:
    test_message = mb_protocol.MbMessage()
    test_message.ParseFromString(message_data)  # Now passing bytes
    print("Parsed message:", test_message)
    
    # Verify CRC
    crcinst = Crc16Dds110()
    crcinst.process(message_data)
    calculated_crc = crcinst.final()
    received_crc = int.from_bytes(crc_bytes, 'big')  # Convert 2 bytes to integer in little-endian
    
    if calculated_crc == received_crc:
        print("CRC verification passed")
    else:
        print(f"CRC verification failed. Calculated: {calculated_crc:04x}, Received: {received_crc:04x}")
except Exception as e:
    print(f"Error parsing test data: {e}")
