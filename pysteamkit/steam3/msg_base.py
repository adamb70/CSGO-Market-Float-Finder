import struct

from pysteamkit.steam_base import EMsg, EUniverse, EResult
from pysteamkit.protobuf import steammessages_base_pb2


class MsgHdr:
	HeaderFmt = '<Iqq'
	HeaderLength = struct.calcsize(HeaderFmt)
	def __init__(self):
		self.emsg = EMsg.Invalid
		self.target_jobid = -1
		self.source_jobid = -1
	def parse(self, buffer):
		self.emsg, self.target_jobid, self.source_jobid = struct.unpack_from(MsgHdr.HeaderFmt, buffer)
		return MsgHdr.HeaderLength
	def serialize(self):
		return struct.pack(MsgHdr.HeaderFmt, self.emsg, self.target_jobid, self.source_jobid)

class ProtobufMsgHdr(object):
	HeaderFmt = 'II'
	HeaderLength = struct.calcsize(HeaderFmt)
	def __init__(self):
		self.emsg = EMsg.Invalid
		self.proto = steammessages_base_pb2.CMsgProtoBufHeader()
		
	@property
	def session_id(self):
		return self.proto.client_sessionid
	@session_id.setter
	def session_id(self, value):
		self.proto.client_sessionid = value
	@property
	def steamid(self):
		return self.proto.steamid
	@steamid.setter
	def steamid(self, value):
		self.proto.steamid = value
	@property
	def source_jobid(self):
		return self.proto.jobid_source
	@source_jobid.setter
	def source_jobid(self, value):
		self.proto.jobid_source = value
	@property
	def target_jobid(self):
		return self.proto.jobid_target
	@target_jobid.setter
	def target_jobid(self, value):
		self.proto.jobid_target = value

	def parse(self, buffer):
		self.emsg, len = struct.unpack_from('<II', buffer)
		self.proto.ParseFromString(buffer[ProtobufMsgHdr.HeaderLength:ProtobufMsgHdr.HeaderLength+len])
		return ProtobufMsgHdr.HeaderLength + len
	def serialize(self):
		headerproto = self.proto.SerializeToString()
		return struct.pack(ProtobufMsgHdr.HeaderFmt, self.emsg, len(headerproto)) + headerproto
		
class Message:
	def __init__(self, header, body, emsg=EMsg.Invalid):
		self.header = header()
		self.body = body()
		self.payload = None
		self.header.emsg = emsg
	def parse(self, buffer):
		header_length = self.header.parse(buffer)
		self.body.parse(buffer, header_length)
	def serialize(self):
		return self.header.serialize() + self.body.serialize() + (self.payload or '')

class ProtobufMessage(object):
	def __init__(self, body, emsg=EMsg.Invalid):
		self.header = ProtobufMsgHdr()
		self.body = body()
		self.payload = None
		self.header.emsg = emsg | 0x80000000
	def parse(self, buffer):
		header_length = self.header.parse(buffer)
		self.body.ParseFromString(buffer[header_length:])
	def serialize(self):
		return self.header.serialize() + self.body.SerializeToString() + (self.payload or '')
	@property
	def proto_header(self):
		return self.header.proto
		
class ChannelEncryptRequest:
	def __init__(self):
		self.protocol_version = 1
		self.universe = EUniverse.Invalid
	def parse(self, buffer, pos=0):
		self.protocol_version, self.universe = struct.unpack_from('<II', buffer, pos)
	def serialize(self):
		return struct.pack('II', self.protocol_version, self.universe)

class ChannelEncryptResponse:
	def __init__(self):
		self.protocol_version = 1
		self.key_size = -1
	def parse(self, buffer, pos=0):
		self.protocol_version, self.key_size = struct.unpack_from('<II', buffer, pos)
	def serialize(self):
		return struct.pack('II', self.protocol_version, self.key_size)

class ChannelEncryptResult:
	def __init__(self):
		self.result = EResult.Invalid
	def parse(self, buffer, pos=0):
		self.result, = struct.unpack_from('<I', buffer, pos)
	def serialize(self):
		return struct.pack('I', self.result)
