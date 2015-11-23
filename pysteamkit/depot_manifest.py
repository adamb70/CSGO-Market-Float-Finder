import struct
import base64
import os
import StringIO
import time
import zipfile
from operator import attrgetter

from pysteamkit.crypto import CryptoUtil
from pysteamkit.protobuf import content_manifest_pb2


class DepotManifest(object):
	PROTOBUF_PAYLOAD_MAGIC = 0x71F617D0
	PROTOBUF_METADATA_MAGIC = 0x1F4812BE
	PROTOBUF_SIGNATURE_MAGIC = 0x1B81B817
	
	def __init__(self):
		self.metadata = content_manifest_pb2.ContentManifestMetadata()
		self.payload = content_manifest_pb2.ContentManifestPayload()
		self.signature = content_manifest_pb2.ContentManifestSignature()
		self.last_written = 0
		self.file_mapping = None
		
	@property
	def files(self):
		return sorted(self.payload.mappings, key=attrgetter('filename'))
		
	@property
	def file_dictionary(self):
		if self.file_mapping:
			return self.file_mapping
		file_mapping = dict()
		for file in self.payload.mappings:
			file_mapping[file.filename] = file
		self.file_mapping = file_mapping
		return file_mapping
		
	def get_files_changed(self, other):
		my_files = self.file_dictionary
		other_files = other.file_dictionary
		my_file_set = set(my_files.keys())
		other_file_set = set(other_files.keys())
		
		deleted = my_file_set - other_file_set
		files_changed = [file.filename for file in other_files.values() if file.filename not in my_files or my_files[file.filename].sha_content != file.sha_content]

		return (files_changed, list(deleted))
	
	def decrypt_filenames(self, depot_key):
		if not self.metadata.filenames_encrypted:
			return True
			
		for mapping in self.payload.mappings:
			filename = base64.b64decode(mapping.filename)
			
			try:
				filename = CryptoUtil.symmetric_decrypt(filename, depot_key)
			except Exception:
				print("Unable to decrypt filename for depot manifest")
				return False
			
			mapping.filename = filename.rstrip(' \t\r\n\0')

		self.metadata.filenames_encrypted = False
		return True
			
	def parse(self, input):
		zip_buffer = StringIO.StringIO(input)
		with zipfile.ZipFile(zip_buffer, 'r') as zip:
			payload = zip.read('z')
				
		magic, payload_len = struct.unpack_from('<II', payload)
		
		if magic != DepotManifest.PROTOBUF_PAYLOAD_MAGIC:
			raise Exception("Expecting protobuf payload")
			
		self.payload = content_manifest_pb2.ContentManifestPayload()
		self.payload.ParseFromString(payload[8:8+payload_len])

		pos_1 = 8+payload_len
		magic, meta_len = struct.unpack_from('<II', payload[pos_1:])

		if magic != DepotManifest.PROTOBUF_METADATA_MAGIC:
			raise Exception("Expecting protobuf metadata")
		
		self.metadata = content_manifest_pb2.ContentManifestMetadata()
		self.metadata.ParseFromString(payload[8+pos_1:8+pos_1+meta_len])
		
		pos_2 = 8+pos_1+meta_len
		magic, sig_len = struct.unpack_from('<II', payload[pos_2:])

		if magic != DepotManifest.PROTOBUF_SIGNATURE_MAGIC:
			raise Exception("Expecting protobuf signature")
			
		self.signature = content_manifest_pb2.ContentManifestSignature()
		self.signature.ParseFromString(payload[8+pos_2:8+pos_2+sig_len])

	def serialize(self):
		payload_body = self.payload.SerializeToString()

		payload = struct.pack('<II', DepotManifest.PROTOBUF_PAYLOAD_MAGIC, len(payload_body))
		payload += payload_body
		
		meta_body = self.metadata.SerializeToString()
		
		payload += struct.pack('<II', DepotManifest.PROTOBUF_METADATA_MAGIC, len(meta_body))
		payload += meta_body
		
		signature_body = self.signature.SerializeToString()
		
		payload += struct.pack('<II', DepotManifest.PROTOBUF_SIGNATURE_MAGIC, len(signature_body))
		payload += signature_body
		
		zip_buffer = StringIO.StringIO(input)
		with zipfile.ZipFile(zip_buffer, 'w') as zip:
			zip.writestr('z', payload)
			
		return zip_buffer.getvalue()
