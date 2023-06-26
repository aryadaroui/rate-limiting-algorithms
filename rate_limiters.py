'''Rate limiting algorithms. For more information, see https://aryadee.dev
'''
#--------------------------------------------------------------------------------------
# Written by Arya "Dee" Daroui, Jun 2023
# MIT License
# You may remove this comment block, but you may want to leave link to blog post above.
#--------------------------------------------------------------------------------------

import math
import globals  # TODO: rename this to experiment_globals

cache = globals.cache

def discrete_window(key: str, threshold: float, window_length_ms: float = 1000) -> dict:
	'''Rate limits requests for target using discrete window.
    
    Discrete window is a simple rate limiting algorithm that allows a certain number of requests per time window.
    Window starts when the first request is made. Relies on TTL for target cache entry to reset the window.
    
    `key`: The key to rate limit, e.g. the IP address of the requester. This is the key used for the cache.
    
    `threshold`: The number of requests allowed per `window_length_ms`
    
    `window_length_ms`: The size of the time window in milliseconds.
    
    returns: A dictionary containing `status` "OK" or "DENIED"; `saturation` is the number of requests made in the current window; if 0 then the target did not exist in the cache (i.e. first request).
    '''

	saturation = cache.get(key)

	if saturation is not None:  # target cache entry exists
		# cache.incr(key)  # incr() does not reset ttl (just like in Redis)

		if saturation < threshold:
			cache.incr(key)  # incr() does not reset ttl (just like in Redis)
			return {"status": "OK", "saturation": saturation + 1}
		else:  # we hit saturation threshold
			return {"status": "DENIED", "saturation": saturation}

	else:  # target cache entry does not exist
		cache.set(key, 1, window_length_ms)  # set the target cache entry with ttl
		return {"status": "OK", "saturation": 1}  # should this be 1?

def exclusion_window(key: str, rps_threshold: float):
	'''Rate limits requests for target using exclusion window. Could also be described as enforced average'''
	exclusion_window = 1000 / rps_threshold

	cache_target = cache.get(key)

	if cache_target is not None:  # target cache entry exists
		return {"status": "DENIED"}
	else:  # target cache entry does not exist
		cache.set(key, 1, exclusion_window)  # set the target cache entry with ttl
		return {"status": "OK"}

def sliding_window(key: str, threshold: float, window_length_ms: float = 1000):

	entry: dict = cache.get(key)

	if entry is not None:  # cache entry exists
		times: list = entry['times']

		# remove all times that are outside the window
		times = [time for time in times if globals.CURRENT_TIME - time < window_length_ms]

		if len(times) < threshold:
			times.append(globals.CURRENT_TIME)
			cache.set(key, {'times': times}, window_length_ms) #TODO: make method for storing list / set in cache
			return {"status": "OK", "saturation": len(times), "new": False}
		else:
			return {"status": "DENIED", "saturation": len(times), "new": False}

	else:
		cache.set(key, {'times': [globals.CURRENT_TIME]}, window_length_ms)
		return {"status": "OK", "saturation": 1, "new": True}

def extrapolating_window(key: str, threshold: float, window_length_ms: float = 1000, mode = 'soft') -> dict:

	def extrapolating_window_soft(key: str, threshold: float, window_length_ms: float = 1000) -> dict:

		entry: dict = cache.get(key)

		if entry is not None:  # cache entry exists

			saturation = entry['saturation']
			time = entry['time']

			delta_time_s = (globals.CURRENT_TIME - time) / 1000  # time in seconds since last request
			window_length_s = window_length_ms / 1000  # window length in seconds

			saturation = max(saturation - (delta_time_s * threshold) / window_length_s, 0)  # steady state limit

			if saturation + 1 < threshold:  # increment the saturation
				cache.set(
					key, {
						'saturation': saturation + 1,
						'time': globals.CURRENT_TIME
					}, (saturation + 1) * 1000 / threshold
				)
				
				# set the target cache entry with ttl
				return {"status": "OK", "saturation": saturation + 1, "new": False}
			else:  # we hit saturation threshold
				return {"status": "DENIED", "saturation": saturation, "new": False}

		else:  # cache entry does not exist
			cache.set(
				key, {
					'saturation': 1,
					'time': globals.CURRENT_TIME
				}, window_length_ms / threshold
			)  # set the target cache entry with ttl
			return {"status": "OK", "saturation": 1, "new": True}

	def extrapolating_window_hard(key: str, threshold: float, window_length_ms: float = 1000) -> dict:

		entry: dict = cache.get(key)

		if entry is not None:  # cache entry exists

			saturation = entry['saturation']
			time = entry['time']

			delta_time_s = (globals.CURRENT_TIME - time) / 1000  # time in seconds since last request
			window_length_s = window_length_ms / 1000  # window length in seconds

			saturation = max(saturation - (delta_time_s) / window_length_s, 0)  # transient limit

			if saturation + 1 < threshold:  # increment the saturation
				cache.set(
					key, {
						'saturation': saturation + 1,
						'time': globals.CURRENT_TIME
					}, (saturation + 1) * 1000
				)
				
				# set the target cache entry with ttl
				return {"status": "OK", "saturation": saturation + 1, "new": False}
			else:  # we hit saturation threshold
				return {"status": "DENIED", "saturation": saturation, "new": False}

		else:  # cache entry does not exist
			cache.set(
				key, {
					'saturation': 1,
					'time': globals.CURRENT_TIME
				}, window_length_ms
			)  # set the target cache entry with ttl
			return {"status": "OK", "saturation": 1, "new": True}

	if mode == 'soft':
		return extrapolating_window_soft(key, threshold, window_length_ms)
	elif mode == 'hard':
		return extrapolating_window_hard(key, threshold, window_length_ms)
	else:
		raise ValueError('Invalid mode')
