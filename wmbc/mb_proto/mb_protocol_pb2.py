# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: mb_protocol.proto
# Protobuf Python Version: 5.28.2
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    28,
    2,
    '',
    'mb_protocol.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import wmbc.mb_proto.mb_protocol_commands_pb2 as mb__protocol__commands__pb2
import wmbc.mb_proto.mb_protocol_answers_pb2 as mb__protocol__answers__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11mb_protocol.proto\x12\x15wmb.proto.mb_protocol\x1a\x1amb_protocol_commands.proto\x1a\x19mb_protocol_answers.proto\"\x9c\x01\n\x07Payload\x12<\n\x11payload_cmd_frame\x18\x01 \x01(\x0b\x32\x1f.wmb.proto.mb_protocol.CmdFrameH\x00\x12\x42\n\x14payload_answer_frame\x18\x02 \x01(\x0b\x32\".wmb.proto.mb_protocol.AnswerFrameH\x00\x42\x0f\n\rpayload_frame\"\x86\x01\n\tMbMessage\x12\x0e\n\x06header\x18\x01 \x01(\r\x12\x0f\n\x07version\x18\x02 \x01(\r\x12\'\n\x03\x63md\x18\x03 \x01(\x0e\x32\x1a.wmb.proto.mb_protocol.Cmd\x12/\n\x07payload\x18\x05 \x01(\x0b\x32\x1e.wmb.proto.mb_protocol.Payload*\xb0\x01\n\x03\x43md\x12\x0f\n\x0b\x43MD_UNKNOWN\x10\x00\x12\x11\n\rCMD_DEV_RESET\x10\x01\x12\x13\n\x0f\x43MD_DIAGNOSTICS\x10\x02\x12\x10\n\x0c\x43MD_DEV_MODE\x10\x03\x12\x15\n\x11\x43MD_ANTENA_CONFIG\x10\x04\x12\x13\n\x0f\x43MD_PORT_CONFIG\x10\x05\x12\x17\n\x13\x43MD_MODBUS_ONE_SHOT\x10\x06\x12\x19\n\x15\x43MD_MODBUS_PERIODICAL\x10\x07\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'mb_protocol_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_CMD']._serialized_start=396
  _globals['_CMD']._serialized_end=572
  _globals['_PAYLOAD']._serialized_start=100
  _globals['_PAYLOAD']._serialized_end=256
  _globals['_MBMESSAGE']._serialized_start=259
  _globals['_MBMESSAGE']._serialized_end=393
# @@protoc_insertion_point(module_scope)
