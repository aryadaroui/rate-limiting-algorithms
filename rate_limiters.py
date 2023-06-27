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

def fixed_window(key: str, limit: float, window_length_ms: float = 1000) -> dict:
	'''Rate limits requests for target using fixed window.
    
    Fixed window is a simple rate limiting algorithm that allows a certain number of requests per time window. The window does **not** slide. Window starts when the first request is made. Relies on TTL for target cache entry to reset the window.
    
    `key`: The key to rate limit, e.g. the IP address of the requester. This is the key used for the cache.
    
    `limit`: The number of requests allowed per `window_length_ms`
    
    `window_length_ms`: The size of the time window in milliseconds.
    
    returns: A dictionary containing `status` "OK" or "DENIED"; `counter` is the number of requests made in the current window; if 0 then the target did not exist in the cache (i.e. first request).
    '''

	counter = cache.get(key)

	if counter is not None:  # target cache entry exists
		# cache.incr(key)  # incr() does not reset ttl (just like in Redis)

		if counter < limit:
			cache.incr(key)  # incr() does not reset ttl (just like in Redis)
			return {"status": "OK", "counter": counter + 1}
		else:  # we hit limit
			return {"status": "DENIED", "counter": counter}

	else:  # target cache entry does not exist
		cache.set(key, 1, window_length_ms)  # set the target cache entry with ttl
		return {"status": "OK", "counter": 1}  # should this be 1?

def enforced_avg(key: str, limit_rps: float):
	'''Rate limits requests for target using exclusion window. Could also be described as enforced average'''
	exclusion_window = 1000 / limit_rps

	cache_target = cache.get(key)

	if cache_target is not None:  # target cache entry exists
		return {"status": "DENIED"}
	else:  # target cache entry does not exist
		cache.set(key, 1, exclusion_window)  # set the target cache entry with ttl
		return {"status": "OK"}

def sliding_window(key: str, limit: float, window_length_ms: float = 1000):

	entry: dict = cache.get(key)

	if entry is not None:  # cache entry exists
		times: list = entry

		# remove all times that are outside the window
		times = [time for time in times if globals.CURRENT_TIME - time < window_length_ms]

		if len(times) < limit:
			times.append(globals.CURRENT_TIME)
			cache.set(key, times, window_length_ms)
			return {"status": "OK", "counter": len(times), "new": False}
		else:
			return {"status": "DENIED", "counter": len(times), "new": False}

	else:
		cache.set(key, [globals.CURRENT_TIME], window_length_ms)
		return {"status": "OK", "counter": 1, "new": True}

def leaky_bucket(key: str, limit: float, window_length_ms: float = 1000, mode = 'soft') -> dict:

	if mode == 'soft':
		rate = limit
	elif mode == 'hard':
		rate = 1
	else:
		raise ValueError('Invalid mode')

	entry: dict = cache.get(key)

	if entry is not None:  # cache entry exists

		counter = entry['counter']
		time = entry['time']

		delta_time_s = (globals.CURRENT_TIME - time) / 1000  # time in seconds since last request
		window_length_s = window_length_ms / 1000  # window length in seconds



		counter = max(counter - (delta_time_s * rate) / window_length_s, 0)  # steady state limit

		if counter + 1 < limit:  # increment the counter
			cache.set(
				key, {
					'counter': counter + 1,
					'time': globals.CURRENT_TIME
				}, (counter + 1) * 1000 / rate
			)
			
			# set the target cache entry with ttl
			return {"status": "OK", "counter": counter + 1, "new": False}
		else:  # we hit counter threshold
			return {"status": "DENIED", "counter": counter, "new": False}

	else:  # cache entry does not exist
		cache.set(
			key, {
				'counter': 1,
				'time': globals.CURRENT_TIME
			}, window_length_ms / rate
		)  # set the target cache entry with ttl
		return {"status": "OK", "counter": 1, "new": True}
