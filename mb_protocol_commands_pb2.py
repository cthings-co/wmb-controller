# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: mb_protocol_commands.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import mb_protocol_enums_pb2 as mb__protocol__enums__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1amb_protocol_commands.proto\x12\x15wmb.proto.mb_protocol\x1a\x17mb_protocol_enums.proto\"\x12\n\nEmptyFrameJ\x04\x08\x01\x10\x02\"O\n\x0f\x44\x65viceModeFrame\x12\x36\n\x0b\x64\x65vice_mode\x18\x02 \x01(\x0e\x32!.wmb.proto.mb_protocol.ModbusModeJ\x04\x08\x01\x10\x02\"^\n\x14\x41ntennaSettingsFrame\x12@\n\x10\x61ntenna_settings\x18\x02 \x01(\x0e\x32&.wmb.proto.mb_protocol.AntennaSettingsJ\x04\x08\x01\x10\x02\"\x8d\x01\n\x15\x42\x61udrateSettingsFrame\x12\x36\n\x0bmodbus_port\x18\x02 \x01(\x0e\x32!.wmb.proto.mb_protocol.ModbusPort\x12\x36\n\x0bmodbus_baud\x18\x03 \x01(\x0e\x32!.wmb.proto.mb_protocol.ModbusBaudJ\x04\x08\x01\x10\x02\"h\n\x12ModbusOneShotFrame\x12\x36\n\x0bmodbus_port\x18\x02 \x01(\x0e\x32!.wmb.proto.mb_protocol.ModbusPort\x12\x14\n\x0cmodbus_frame\x18\x03 \x01(\x0cJ\x04\x08\x01\x10\x02\"\x9a\x01\n\x15ModbusPeriodicalFrame\x12\x36\n\x0bmodbus_port\x18\x02 \x01(\x0e\x32!.wmb.proto.mb_protocol.ModbusPort\x12\x1b\n\x13\x63onfiguration_index\x18\x03 \x01(\r\x12\x10\n\x08interval\x18\x04 \x01(\r\x12\x14\n\x0cmodbus_frame\x18\x05 \x01(\x0cJ\x04\x08\x01\x10\x02\"\xd3\x03\n\x08\x43mdFrame\x12\x38\n\x0b\x65mpty_frame\x18\x01 \x01(\x0b\x32!.wmb.proto.mb_protocol.EmptyFrameH\x00\x12\x43\n\x11\x64\x65vice_mode_frame\x18\x02 \x01(\x0b\x32&.wmb.proto.mb_protocol.DeviceModeFrameH\x00\x12M\n\x16\x61ntenna_settings_frame\x18\x03 \x01(\x0b\x32+.wmb.proto.mb_protocol.AntennaSettingsFrameH\x00\x12O\n\x17\x62\x61udrate_settings_frame\x18\x04 \x01(\x0b\x32,.wmb.proto.mb_protocol.BaudrateSettingsFrameH\x00\x12J\n\x15modbus_one_shot_frame\x18\x05 \x01(\x0b\x32).wmb.proto.mb_protocol.ModbusOneShotFrameH\x00\x12O\n\x17modbus_periodical_frame\x18\x06 \x01(\x0b\x32,.wmb.proto.mb_protocol.ModbusPeriodicalFrameH\x00\x42\x0b\n\tcmd_frameb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'mb_protocol_commands_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _EMPTYFRAME._serialized_start=78
  _EMPTYFRAME._serialized_end=96
  _DEVICEMODEFRAME._serialized_start=98
  _DEVICEMODEFRAME._serialized_end=177
  _ANTENNASETTINGSFRAME._serialized_start=179
  _ANTENNASETTINGSFRAME._serialized_end=273
  _BAUDRATESETTINGSFRAME._serialized_start=276
  _BAUDRATESETTINGSFRAME._serialized_end=417
  _MODBUSONESHOTFRAME._serialized_start=419
  _MODBUSONESHOTFRAME._serialized_end=523
  _MODBUSPERIODICALFRAME._serialized_start=526
  _MODBUSPERIODICALFRAME._serialized_end=680
  _CMDFRAME._serialized_start=683
  _CMDFRAME._serialized_end=1150
# @@protoc_insertion_point(module_scope)
