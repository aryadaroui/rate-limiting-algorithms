'''Rate limiting algorithms. For more information, see https://aryadee.dev/blog/rate-limiting-algorithms
'''

#-------------------------------------------------------------------------------------
# Written by Arya "Dee" Daroui, Jun 2023
# MIT License
# You may remove this comment block, but you may want to leave link to blog post above.
#-------------------------------------------------------------------------------------

from experiment_globals import dummy_cache, dummy_time
from typing import Literal
from dataclasses import dataclass

# cache = experiment_globals.cache
# datetime = experiment_globals.datetime

# these dataclasses weren't used because of clarity in blog post
# but I encourage you to use them in your own code

@dataclass
class FixedWindowReturn:
	status: Literal["OK", "DENIED"]
	counter: int

@dataclass
class SlidingWindowReturn:
	status: Literal["OK", "DENIED"]
	counter: int
	new: bool

@dataclass
class EnforcedAvgReturn:
	status: Literal["OK", "DENIED"]

@dataclass
class LeakyBucketReturn:
	status: Literal["OK", "DENIED"]
	counter: int
	new: bool

def fixed_window(key: str, limit: float, window_length_ms: float = 1000) -> dict:
	'''Rate limits requests for target using fixed window.
    
    Fixed window is a simple rate limiting algorithm that allows a certain number of requests per time window. The window does **not** slide. Window starts when the first request is made. Relies on TTL for target cache entry to reset the window.
    
    `key`: The key to rate limit, e.g. the IP address of the requester. This is the key used for the cache.
    
    `limit`: The number of requests allowed per `window_length_ms`
    
    `window_length_ms`: The size of the time window in milliseconds.
    
    returns: A dictionary containing `status` "OK" or "DENIED"; `counter` is the number of requests made in the current window; if 0 then the target did not exist in the cache (i.e. first request).
    '''

	counter = dummy_cache.get(key)

	if counter is not None:  # target cache entry exists
		# cache.incr(key)  # incr() does not reset ttl (just like in Redis)

		if counter < limit:
			dummy_cache.incr(key)  # incr() does not reset ttl (just like in Redis)
			return {"status": "OK", "counter": counter + 1}
		else:  # we hit limit
			return {"status": "DENIED", "counter": counter}

	else:  # target cache entry does not exist
		dummy_cache.set(key, 1, window_length_ms)  # set the target cache entry with ttl
		return {"status": "OK", "counter": 1}  # should this be 1?

def enforced_avg(key: str, limit_rps: float):
	'''Rate limits requests for target using exclusion window. Could also be described as enforced average'''
	exclusion_window = 1000 / limit_rps

	cache_target = dummy_cache.get(key)

	if cache_target is not None:  # target cache entry exists
		return {"status": "DENIED"}
	else:  # target cache entry does not exist
		dummy_cache.set(key, 1, exclusion_window)  # set the target cache entry with ttl
		return {"status": "OK"}

def sliding_window(key: str, limit: float, window_length_ms: float = 1000):

	times: list = dummy_cache.get(key)
	if times is not None:  # cache entry exists

		# remove all times that are outside the window
		times = [time for time in times if dummy_time.now() - time < window_length_ms]

		if len(times) < limit:
			times.append(dummy_time.now())
			dummy_cache.set(key, times, window_length_ms)
			return {"status": "OK", "counter": len(times), "new": False}
		else:
			return {"status": "DENIED", "counter": len(times), "new": False}

	else:
		dummy_cache.set(key, [dummy_time.now()], window_length_ms)
		return {"status": "OK", "counter": 1, "new": True}

def leaky_bucket(key: str, limit: float, window_length_ms: float = 1000, mode = 'soft') -> dict:

	if mode == 'soft':
		leak_rate = limit # leak at limit-many requests per window
	elif mode == 'hard':
		leak_rate = 1 # leak at 1 request per window
	else:
		raise ValueError(f'Invalid mode: {mode}')

	entry: dict = dummy_cache.get(key)

	if entry is not None:  # cache entry exists

		# unpack the cache entry because `['key']` notation is ugly
		counter = entry['counter']
		time = entry['time']

		delta_time_ms = (dummy_time.now() - time)  # time since last request
		counter = max(counter - (delta_time_ms * leak_rate) / window_length_ms, 0) # get the extrapolated counter value

		if counter + 1 < limit:  # increment the counter
			dummy_cache.set(
				key, {
					'counter': counter + 1,
					'time': dummy_time.now()
				}, (counter + 1) * 1000 / leak_rate
			)
			
			# set the target cache entry with ttl
			return {"status": "OK", "counter": counter + 1, "new": False}
		else:  # we hit counter threshold
			return {"status": "DENIED", "counter": counter, "new": False}

	else:  # cache entry does not exist
		dummy_cache.set(
			key, {
				'counter': 1,
				'time': dummy_time.now()
			}, window_length_ms / leak_rate
		)  # set the target cache entry with ttl
		return {"status": "OK", "counter": 1, "new": True}
