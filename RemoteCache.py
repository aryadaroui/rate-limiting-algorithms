import globals

class RemoteCache:
	''' A class that mimics a remote cache data store.
    '''

	def __init__(self):
		''' Creates a new instance of the `RemoteCache` class.
        '''
		self.data = {}

	def set(self, key, value, ttl = None):
		''' Sets data with optional TTL in milliseconds.
        
        `key`: The key to set.
        
        `value`: The value to set.
        
        `ttl`: The time-to-live in milliseconds.
        '''
		expiration = None
		if ttl:
			expiration = globals.CURRENT_TIME + ttl

		self.data[key] = {"value": value, "expiration": expiration}

	def get(self, key):
		''' Gets data if it exists and TTL has not expired.
        
        `key`: The key to get.
        
        returns: The value associated with the key, or None if the key does not exist or has expired.
        '''
		data = self.data.get(key)
		if not data:
			return None
		if 'expiration' in data and data["expiration"] <= globals.CURRENT_TIME:
			del self.data[key]
			return None
		return data["value"]

	def incr(self, key):
		''' Increments the value of a key. Does not reset TTL.
        
        `key`: The key to increment.
        '''
		if isinstance(self.data[key]["value"], int):
			self.data[key]["value"] += 1

	def reset(self):
		''' Resets the data store.
        '''
		self.data = {}