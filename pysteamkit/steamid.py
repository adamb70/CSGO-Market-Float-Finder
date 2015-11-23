class SteamID(object):
	def __init__(self, steamid=0):
		self.steamid = steamid
		
	@classmethod
	def make_from(self, account, instance, universe, accounttype):
		return self((account & 0xFFFFFFFF) | (instance & 0xFFFFF) << 32 | (accounttype & 0xF) << 52 | (universe & 0xFF) << 56)
	
	def __masked_set(self, value, offset, mask):
		return (self.steamid & ~(mask << offset)) | ((value & mask) << offset)
		
	@property
	def account(self):
		return self.steamid & 0xFFFFFFFF
	@account.setter
	def account(self, value):
		self.steamid = self.__masked_set(value, 0, 0xFFFFFFFF)
		
	@property
	def instance(self):
		return (self.steamid >> 32) & 0xFFFFF
	@instance.setter
	def instance(self, value):
		self.steamid = self.__masked_set(value, 32, 0xFFFFF)

	@property
	def accounttype(self):
		return (self.steamid >> 52) & 0xF
	@accounttype.setter
	def accounttype(self, value):
		self.steamid = self.__masked_set(value, 52, 0xF)
		
	@property
	def universe(self):
		return (self.steamid >> 56) & 0xFF
	@universe.setter
	def universe(self, value):
		self.steamid = self.__masked_set(value, 56, 0xFF)
		
	def __cmp__(self, other):
		return other.steamid - self.steamid
		
	def __str__(self):
		return 'SteamID(%d)' % (self.steamid,)
