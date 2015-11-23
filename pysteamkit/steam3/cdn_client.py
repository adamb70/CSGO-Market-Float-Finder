import StringIO
import struct
import urllib2
import zipfile
import requests
from gevent import socket
from operator import itemgetter

from pysteamkit.crypto import CryptoUtil
from pysteamkit.steam_base import EResult
from pysteamkit.util import Util
from pysteamkit import vdf

try:
	import lzma
except ImportError:
	from backports import lzma

class CDNClient(object):
	def __init__(self, host, port, type, app_ticket=None, steamid=None):
		self.host = host
		self.port = port
		self.type = type
		self.app_ticket = app_ticket
		self.steamid = steamid
		self.depots = []
		self.cdn_auth_tokens = dict()
		
		self.session_key = None
		self.session_id = None
		self.req_counter = None
		
		self.csid = None
		self.session = requests.Session()
		self.error_count = 0
		
	def _make_request_url(self, action, params='', token=None):
		absolute_uri = '/%s/%s' % (action, params)
		url = 'http://%s:%s%s%s' % (self.host, self.port, absolute_uri, token if token else '')

		if self.type == 'CDN':
			return (url, {})
			
		self.req_counter += 1
		
		hash_buffer = struct.pack('<QQ', self.session_id, self.req_counter) + self.session_key + absolute_uri
		sha_hash = Util.sha1_hash(hash_buffer, True)

		headers = {'x-steam-auth': 'sessionid=%d;req-counter=%d;hash=%s;' % (self.session_id, self.req_counter, sha_hash)}
		return (url, headers)
		
	def mark_failed_request(self):
		self.error_count += 1
		return self.error_count <= 4
		
	def initialize(self):
		if self.type == 'CDN':
			return True
			
		self.session_key = CryptoUtil.create_session_key()
		crypted_key = CryptoUtil.rsa_encrypt(self.session_key)

		url = "http://%s:%s/initsession/" % (self.host, self.port)
		
		payload = dict(sessionkey = crypted_key)
		
		if self.app_ticket:
			payload['appticket'] = CryptoUtil.symmetric_encrypt(self.app_ticket, self.session_key)
		else:
			payload['anonymoususer'] = 1
			payload['steamid'] = self.steamid.steamid

		r = self.session.post(url, payload)
		
		if r.status_code != 200:
			return False
			
		sessionkv = vdf.loads(r.content)['response']
		self.csid = sessionkv['csid']
		self.session_id = int(sessionkv['sessionid']) & 0xFFFFFFFFFFFFFFFF
		self.req_counter = int(sessionkv['req-counter'])
		return True

	def auth_appticket(self, depotid, app_ticket):
		if depotid in self.depots:
			return True
			
		crypted_ticket = CryptoUtil.symmetric_encrypt(app_ticket, self.session_key)

		(url, headers) = self._make_request_url('authdepot')
		payload = dict(appticket = crypted_ticket)
	
		r = self.session.post(url, payload, headers=headers)
		
		if r.status_code != 200:
			return False
			
		self.depots.append(depotid)
		return True
		
	def auth_depotid(self, depotid):
		if depotid in self.depots:
			return True
			
		(url, headers) = self._make_request_url('authdepot')
		payload = dict(depotid = depotid)

		r = self.session.post(url, payload, headers=headers)
		
		if r.status_code != 200:
			return False
			
		self.depots.append(depotid)
		return True
		
	def auth_cdn_token(self, steamapps, appid, depotid):
		if self.type != 'CDN':
			return False
			
		if depotid in self.depots:
			return True
			
		token_response = steamapps.get_cdn_auth_token(depotid, self.host)
	
		if token_response.eresult != EResult.OK:
			return False
		
		self.cdn_auth_tokens[depotid] = token_response.token
		self.depots.append(depotid)
		return True
		
	def download_depot_manifest(self, depotid, manifestid):
		(url, headers) = self._make_request_url('depot', '%d/manifest/%d/5' % (int(depotid), int(manifestid)), token=self.cdn_auth_tokens.get(depotid))
		
		r = self.session.get(url, headers=headers)

		return (r.status_code, r.content if r.status_code == 200 else None)
			
	def download_depot_chunk(self, depotid, chunkid):
		(url, headers) = self._make_request_url('depot', '%d/chunk/%s' % (int(depotid), chunkid), token=self.cdn_auth_tokens.get(depotid))
		
		r = self.session.get(url, headers=headers)
		
		return (r.status_code, r.content if r.status_code == 200 else None)
		
	@staticmethod
	def process_chunk(chunk, depot_key):
		decrypted_chunk = CryptoUtil.symmetric_decrypt(chunk, depot_key)
		if decrypted_chunk[:2] == 'VZ':
			filter = lzma._decode_filter_properties(lzma.FILTER_LZMA1, decrypted_chunk[7:12])
			lzmadec = lzma.LZMADecompressor(lzma.FORMAT_RAW, None, [filter])
			return lzmadec.decompress(decrypted_chunk[12:len(decrypted_chunk)-10])
		else:
			zip_buffer = StringIO.StringIO(decrypted_chunk)
			with zipfile.ZipFile(zip_buffer, 'r') as zip:
				return zip.read(zip.namelist()[0])
		
		
	@staticmethod
	def fetch_server_list(host, port, cell_id):
		url = "http://%s:%d/serverlist/%d/%d/" % (host, port, cell_id, 20)
		
		r = requests.get(url)
		serverkv = vdf.loads(r.content)
			
		if serverkv.get('deferred') == '1':
			return None

		servers = []
		for id, child in serverkv['serverlist'].iteritems():
			if child.get('host').find(';')> 0:
				(h, p) = child.get('host').split(':')
			else:
				(h, p) = child.get('host'), 80
			
			load = child.get('weightedload')
			servers.append((h, p, load, child.get('type')))

		return sorted(servers, key=itemgetter(2))
