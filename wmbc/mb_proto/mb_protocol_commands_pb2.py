# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: mb_protocol_commands.proto
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
    'mb_protocol_commands.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import wmbc.mb_proto.mb_protocol_enums_pb2 as mb__protocol__enums__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1amb_protocol_commands.proto\x12\x15wmb.proto.mb_protocol\x1a\x17mb_protocol_enums.proto\"\x0c\n\nEmptyFrame\"I\n\x0f\x44\x65viceModeFrame\x12\x36\n\x0b\x64\x65vice_mode\x18\x01 \x01(\x0e\x32!.wmb.proto.mb_protocol.ModbusMode\"X\n\x14\x41ntennaSettingsFrame\x12@\n\x10\x61ntenna_settings\x18\x01 \x01(\x0e\x32&.wmb.proto.mb_protocol.AntennaSettings\"\xf4\x01\n\x11PortSettingsFrame\x12\x36\n\x0bmodbus_port\x18\x01 \x01(\x0e\x32!.wmb.proto.mb_protocol.ModbusPort\x12\x32\n\tport_baud\x18\x02 \x01(\x0e\x32\x1f.wmb.proto.mb_protocol.PortBaud\x12\x36\n\x0bport_parity\x18\x03 \x01(\x0e\x32!.wmb.proto.mb_protocol.PortParity\x12;\n\x0eport_stop_bits\x18\x04 \x01(\x0e\x32#.wmb.proto.mb_protocol.PortStopBits\"b\n\x12ModbusOneShotFrame\x12\x36\n\x0bmodbus_port\x18\x01 \x01(\x0e\x32!.wmb.proto.mb_protocol.ModbusPort\x12\x14\n\x0cmodbus_frame\x18\x02 \x01(\x0c\"\x94\x01\n\x15ModbusPeriodicalFrame\x12\x36\n\x0bmodbus_port\x18\x01 \x01(\x0e\x32!.wmb.proto.mb_protocol.ModbusPort\x12\x1b\n\x13\x63onfiguration_index\x18\x02 \x01(\r\x12\x10\n\x08interval\x18\x03 \x01(\r\x12\x14\n\x0cmodbus_frame\x18\x04 \x01(\x0c\"\xcb\x03\n\x08\x43mdFrame\x12\x38\n\x0b\x65mpty_frame\x18\x01 \x01(\x0b\x32!.wmb.proto.mb_protocol.EmptyFrameH\x00\x12\x43\n\x11\x64\x65vice_mode_frame\x18\x02 \x01(\x0b\x32&.wmb.proto.mb_protocol.DeviceModeFrameH\x00\x12M\n\x16\x61ntenna_settings_frame\x18\x03 \x01(\x0b\x32+.wmb.proto.mb_protocol.AntennaSettingsFrameH\x00\x12G\n\x13port_settings_frame\x18\x04 \x01(\x0b\x32(.wmb.proto.mb_protocol.PortSettingsFrameH\x00\x12J\n\x15modbus_one_shot_frame\x18\x05 \x01(\x0b\x32).wmb.proto.mb_protocol.ModbusOneShotFrameH\x00\x12O\n\x17modbus_periodical_frame\x18\x06 \x01(\x0b\x32,.wmb.proto.mb_protocol.ModbusPeriodicalFrameH\x00\x42\x0b\n\tcmd_frameb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'mb_protocol_commands_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_EMPTYFRAME']._serialized_start=78
  _globals['_EMPTYFRAME']._serialized_end=90
  _globals['_DEVICEMODEFRAME']._serialized_start=92
  _globals['_DEVICEMODEFRAME']._serialized_end=165
  _globals['_ANTENNASETTINGSFRAME']._serialized_start=167
  _globals['_ANTENNASETTINGSFRAME']._serialized_end=255
  _globals['_PORTSETTINGSFRAME']._serialized_start=258
  _globals['_PORTSETTINGSFRAME']._serialized_end=502
  _globals['_MODBUSONESHOTFRAME']._serialized_start=504
  _globals['_MODBUSONESHOTFRAME']._serialized_end=602
  _globals['_MODBUSPERIODICALFRAME']._serialized_start=605
  _globals['_MODBUSPERIODICALFRAME']._serialized_end=753
  _globals['_CMDFRAME']._serialized_start=756
  _globals['_CMDFRAME']._serialized_end=1215
# @@protoc_insertion_point(module_scope)
