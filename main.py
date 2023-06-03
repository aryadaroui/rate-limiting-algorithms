import rich.traceback

rich.traceback.install()

import inspect
from rich.pretty import pprint
from plot import *
from typing import Callable


def generate_times(rps: float, duration: float) -> list:
	''' Generates a list of times in milliseconds.'''
	times = []
	interval = 1000 / rps
	for i in range(int(rps * duration)):
		times.append((i + 1) * interval)  # i + 1 to make it not start at 0
	return times


RPS = 10  # requests per second
RPS_THRESHOLD = 5  # max requests per second to allow
DURATION = 2  # seconds
WINDOW_LENGTH_MS = 1000  # millisecond

CURRENT_TIME = 0
TIMES = generate_times(RPS, DURATION)


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
			expiration = CURRENT_TIME + ttl

		self.data[key] = {"value": value, "expiration": expiration}

	def get(self, key):
		''' Gets data if it exists and TTL has not expired.
        
        `key`: The key to get.
        
        returns: The value associated with the key, or None if the key does not exist or has expired.
        '''
		data = self.data.get(key)
		if not data:
			return None
		if data["expiration"] and data["expiration"] < CURRENT_TIME:
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


cache = RemoteCache()


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


def experiment(rate_limiter: Callable, rate_lmiter_args: dict, plotter: Callable):
	global CURRENT_TIME

	data = {
	    "experiment": {
	        "rate_limiter": rate_limiter.__name__,
	        "rps": RPS,
	        "duration": DURATION,
	        "threshold": RPS_THRESHOLD,
	    },
	    "plot": []
	}

	# rate limiter specific experiment data
	data["experiment"].update(rate_lmiter_args)

	pprint(data)

	for time in TIMES:
		CURRENT_TIME = time
		output = rate_limiter(**rate_lmiter_args)
		output["time"] = time
		data["plot"].append(output)

	plotter(data, 'Py')


if __name__ == "__main__":

	experiment(
	    discrete_window, {
	        'key': 'global',
	        'threshold': RPS_THRESHOLD,
	        'window_length_ms': WINDOW_LENGTH_MS
	    }, plot_discrete_window
	)
