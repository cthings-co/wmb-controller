#!/bin/bash

# Run from root directory

# Set directories
PROTO_DIR="wmb-proto"

# Compile proto files
mkdir -p generated
protoc -I="$PROTO_DIR" --python_out=generated \
    "$PROTO_DIR/mb_protocol.proto" \
    "$PROTO_DIR/mb_protocol_answers.proto" \
    "$PROTO_DIR/mb_protocol_commands.proto" \
    "$PROTO_DIR/mb_protocol_enums.proto"

find generated -type f -exec sed -i 's/import mb_protocol_enums_pb2/import wmbc.mb_proto.mb_protocol_enums_pb2/g' {} + >/dev/null
find generated -type f -exec sed -i 's/import mb_protocol_commands_pb2/import wmbc.mb_proto.mb_protocol_commands_pb2/g' {} + >/dev/null
find generated -type f -exec sed -i 's/import mb_protocol_answers_pb2/import wmbc.mb_proto.mb_protocol_answers_pb2/g' {} + >/dev/null

# Check for errors
if [[ $? -eq 0 ]]; then
    echo "Protocol buffers compiled successfully"
else
    echo "Error compiling protocol buffers"
    echo "Error code: $?"
fi
