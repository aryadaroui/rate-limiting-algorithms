'''Rate limiting algorithms. For more information, see https://aryadee.dev
'''
#--------------------------------------------------------------------------------------
# Written by Arya "Dee" Daroui, Jun 2023   
# MIT License
# You may remove this comment block, but you may want to leave link to blog post above.
#--------------------------------------------------------------------------------------

import math
import globals # TODO: rename this to experiment_globals

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
		cache.incr(key)  # incr() does not reset ttl (just like in Redis)

		if saturation < threshold:  # increment the saturation
			return {"status": "OK", "saturation": saturation}
		else:  # we hit saturation threshold
			return {"status": "DENIED", "saturation": saturation}

	else:  # target cache entry does not exist
		cache.set(key, 1, window_length_ms)  # set the target cache entry with ttl
		return {"status": "OK", "saturation": 0}  # TODO: this should be 1


def exclusion_window(key: str, rps_threshold: float):
	'''Rate limits requests for target using exclusion window. Could also be described as enforced average'''
	exclusion_window = 1000 / rps_threshold

	cache_target = cache.get(key)

	if cache_target is not None:  # target cache entry exists
		return {"status": "DENIED"}
	else:  # target cache entry does not exist
		cache.set(key, 1, exclusion_window)  # set the target cache entry with ttl
		return {"status": "OK"}


def extrapolated_sliding_window(key: str, threshold: float, window_length_ms: float = 1000, mode = 'steady_state') -> dict:

	# unpack the cache entry by dict key name. no tuple unpacking funny business
	entry: dict = cache.get(key)

	if entry is not None:  # cache entry exists

		saturation = entry['saturation']
		time = entry['time']

		# max(x, 0) prevents x from going negative

		delta_time_s = (globals.CURRENT_TIME - time) / 1000  # time in seconds since last request
		window_length_s = window_length_ms / 1000  # window length in seconds

		# if mode == 'mixed':
		# 	if saturation > threshold:
		# 		mode = 'steady_state'
		# 	else:
		# 		mode = 'transient'

		if mode == 'steady_state':
			saturation = max(saturation - (delta_time_s * threshold) / window_length_s, 0)  # steady state limit
		elif mode == 'transient':
			saturation = max(saturation - (delta_time_s) / window_length_s, 0)  # transient limit
		else:
			raise ValueError('Invalid mode')

		if saturation + 1 < threshold:  # increment the saturation

			# update the cache entry
			cache.set(
			    key, {
			        'saturation': saturation + 1,
			        'time': globals.CURRENT_TIME
			    }, (saturation + 1) * window_length_ms
			)  # set the target cache entry with ttl
			return {"status": "OK", "saturation": saturation + 1, "new": False}
		else:  # we hit saturation threshold
			return {"status": "DENIED", "saturation": saturation, "new": False}

	else:  #  cache entry does not exist
		cache.set(
		    key, {
		        'saturation': 1,
		        'time': globals.CURRENT_TIME
		    }, window_length_ms
		)  # set the target cache entry with ttl
		return {"status": "OK", "saturation": 1, "new": True}


def simple_sliding_window(key: str, threshold: float, window_length_ms: float = 1000):

	entry: dict = cache.get(key)

	if entry is not None:  # cache entry exists
		times: list = entry['times']

		# remove all times that are outside the window
		times = [time for time in times if globals.CURRENT_TIME - time < window_length_ms]

		if len(times) < threshold:
			times.append(globals.CURRENT_TIME)
			cache.set(key, {'times': times}, window_length_ms)
			return {"status": "OK", "saturation": len(times), "new": False}
		else:
			return {"status": "DENIED", "saturation": len(times), "new": False}

	else:
		cache.set(key, {'times': [globals.CURRENT_TIME]}, window_length_ms)
		return {"status": "OK", "saturation": 1, "new": True}


# # may have just made sliding window again lol. may not use this anyway
# def leaky_bucket(key: str, rate: float, capacity: float) -> dict:
#     current_time = globals.CURRENT_TIME
#     cache_target = cache.get(key)

#     if cache_target is not None:
#         return {"status": "DENIED"}
#     else:
#         cache.set(key, {"water_level": 0, "last_leak": current_time}, capacity / rate)
#         return {"status": "OK"}

# def leaky_bucket_add_water(key: str, amount: float) -> bool:
#     current_time = globals.CURRENT_TIME
#     cache_target = cache.get(key)

#     if cache_target is None:
#         return False

#     water_level = cache_target["water_level"]
#     last_leak = cache_target["last_leak"]
#     time_since_last_leak = current_time - last_leak
#     rate = 1 / (cache_target["ttl"] / capacity)

#     water_level -= time_since_last_leak * rate
#     water_level = max(water_level, 0)

#     if water_level + amount <= capacity:
#         water_level += amount
#         cache.set(key, {"water_level": water_level, "last_leak": current_time}, cache_target["ttl"])
#         return True
#     else:
#         return False