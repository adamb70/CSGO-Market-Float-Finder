from pysteamkit import vdf
from pysteamkit.protobuf import steammessages_clientserver_pb2
from pysteamkit.steam_base import EMsg, EAccountType
from pysteamkit.steam3 import msg_base
from pysteamkit.util import Util


class SteamApps():
	def __init__(self, client):
		self.client = client
		
		self.licenses = None
		self.app_cache = dict()
		self.package_cache = dict()
		self.ticket_cache = dict()
		self.cdn_token_cache = dict()
		
		self.client.register_listener(self)
		self.client.register_message(EMsg.ClientLicenseList, msg_base.ProtobufMessage, steammessages_clientserver_pb2.CMsgClientLicenseList)
#		self.client.register_message(EMsg.PICSProductInfoResponse, msg_base.ProtobufMessage, steammessages_clientserver_pb2.CMsgPICSProductInfoResponse)
#		self.client.register_message(EMsg.PICSAccessTokenResponse, msg_base.ProtobufMessage, steammessages_clientserver_pb2.CMsgPICSAccessTokenResponse)
#		self.client.register_message(EMsg.PICSChangesSinceResponse, msg_base.ProtobufMessage, steammessages_clientserver_pb2.CMsgPICSChangesSinceResponse)
		self.client.register_message(EMsg.ClientGetDepotDecryptionKeyResponse, msg_base.ProtobufMessage, steammessages_clientserver_pb2.CMsgClientGetDepotDecryptionKeyResponse)
		self.client.register_message(EMsg.ClientGetAppOwnershipTicketResponse, msg_base.ProtobufMessage, steammessages_clientserver_pb2.CMsgClientGetAppOwnershipTicketResponse)
		self.client.register_message(EMsg.ClientGetCDNAuthTokenResponse, msg_base.ProtobufMessage, steammessages_clientserver_pb2.CMsgClientGetCDNAuthTokenResponse)
		
	def get_licenses(self):
		if self.licenses:
			return self.licenses
			
		if self.client.account_type == EAccountType.Individual:
			self.client.wait_for_message(EMsg.ClientLicenseList)
			return self.licenses
			
		return None
		
	def get_depot_key(self, depot_id, app_id=0):
		message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientGetDepotDecryptionKey, EMsg.ClientGetDepotDecryptionKey)

		message.body.depot_id = depot_id
		message.body.app_id = app_id
		
		response = self.client.wait_for_job(message, EMsg.ClientGetDepotDecryptionKeyResponse)
		return response.body
		
		
	def get_product_info(self, apps=None, packages=None):
		message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgPICSProductInfoRequest, EMsg.PICSProductInfoRequest)

		if apps:
			for app in apps:
				app_info = message.body.apps.add()
				app_info.only_public = False
				if isinstance(app, tuple):
					app_info.appid, app_info.access_token = app
				else:
					app_info.appid = app
	
		if packages:
			for package in packages:
				package_info = message.body.packages.add()
				if isinstance(package, tuple):
					package_info.appid, package_info.access_token = package
				else:
					package_info.packageid = package
		
		message.body.meta_data_only = False
		
		response = self.client.wait_for_job(message, EMsg.PICSProductInfoResponse)

		for app in response.body.apps:
			self.app_cache[app.appid] = vdf.loads(app.buffer)['appinfo']

		for package in response.body.packages:
			kv = vdf.loadbinary(package.buffer[4:])
			self.package_cache[package.packageid] = kv[0][str(package.packageid)]

		return response.body

	def get_access_tokens(self, apps=None, packages=None):
		message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgPICSAccessTokenRequest, EMsg.PICSAccessTokenRequest)
		
		if apps:
			message.body.appids.extend(apps)

		if packages:
			message.body.packageids.extend(packages)
			
		response = self.client.wait_for_job(message, EMsg.PICSAccessTokenResponse)
		
		return response.body
	
	def get_app_ticket(self, appid):
		if self.client.account_type != EAccountType.Individual:
			return None
		
		if self.ticket_cache.get(appid):
			return self.ticket_cache[appid]
			
		message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientGetAppOwnershipTicket, EMsg.ClientGetAppOwnershipTicket)
		
		message.body.app_id = appid
		
		response = self.client.wait_for_job(message, EMsg.ClientGetAppOwnershipTicketResponse)
		
		self.ticket_cache[appid] = response.body
		return response.body
		
	def get_changes_since(self, last_change_number, send_app_changes=True, send_package_changes=False):
		message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgPICSChangesSinceRequest, EMsg.PICSChangesSinceRequest)
		
		message.body.since_change_number = last_change_number
		message.body.send_app_info_changes = send_app_changes
		message.body.send_package_info_changes = send_package_changes
		
		response = self.client.wait_for_job(message, EMsg.PICSChangesSinceResponse)
		return response.body
		
	def get_cdn_auth_token(self, appid, host):
		if self.cdn_token_cache.get((appid, host)):
			return self.cdn_token_cache[(appid, host)]
			
		message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientGetCDNAuthToken, EMsg.ClientGetCDNAuthToken)
		
		message.body.app_id = appid
		message.body.host_name = host
		
		response = self.client.wait_for_job(message, EMsg.ClientGetCDNAuthTokenResponse)
		
		self.cdn_token_cache[(appid, host)] = response.body
		return response.body
	
	def has_license_for_app(self, appid):
		for (packageid, package) in self.package_cache.items():
			if appid in package['appids'].values():
				return True
		return False
		
	def has_license_for_depot(self, depotid):
		for (packageid, package) in self.package_cache.items():
			if depotid in package['depotids'].values():
				return True
		return False
		
	def handle_message(self, emsg_real, msg):
		emsg = Util.get_msg(emsg_real)
		
		if emsg == EMsg.ClientLicenseList:
			self.handle_license_list(msg)
			
	def handle_license_list(self, msg):
		message = msg_base.ProtobufMessage(steammessages_clientserver_pb2.CMsgClientLicenseList)
		message.parse(msg)

		self.licenses = message.body.licenses
		
