import { RemoteCache } from './RemoteCache.js';

/** rate limits requests for target using discrete window.
 * Discrete window is a simple rate limiting algorithm that allows a certain number of requests per time window.
 * Window starts when the first request is made. Relies on TTL for target cache entry to reset the window.
 * @param target the target to rate limit. this is used as the key in the cache, e.g. the IP address of the requester
 * @param threshold the number of requests allowed per second (default 5)
 * @param cache the remote cache to use to monitor the rate limit
 * @returns `status` "OK" or "DENIED"; `saturation` is the number of requests made in the current window; if 0 then the target
 *  did not exist in the cache (i.e. first request)
 */
export function discrete_window(target: string, threshold: number, cache: RemoteCache): { status: string; saturation: number; } {
	let saturation: number | null = cache.get(target);

	if (saturation) { // target cache entry exists
		if (saturation < threshold) {
			// increment the saturation
			// cache1.set(target, target_cache + 1, 1000); // set() resets the ttl (just like in Redis)! undesirable!
			cache.incr(target); // incr() does not reset ttl (just like in Redis)
			return { status: 'OK', saturation: saturation };
		} else { // we hit saturation threshold
			cache.incr(target); // optional. useful to know how many requests were denied
			return { status: 'DENIED', saturation: saturation };
		}
	} else { // target cache entry does not exist
		cache.set(target, 1, 1000);
		return { status: 'OK', saturation: 0 };
	}
}