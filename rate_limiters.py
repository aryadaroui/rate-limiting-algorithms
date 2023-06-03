import globals
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
		return {"status": "OK", "saturation": 0}
	
def exclusion_window(target: str, rps_threshold: float):
	'''Rate limits requests for target using exclusion window. Could also be described as enforced average'''
	exclusion_window = 1000 / rps_threshold

	cache_target = cache.get(target)

	if cache_target is not None:  # target cache entry exists
		return {"status": "DENIED"}
	else:  # target cache entry does not exist
		cache.set(target, 1, exclusion_window)  # set the target cache entry with ttl
		return {"status": "OK"}