import { RemoteCache } from './RemoteCache.js';

// /** rate limits requests for target using discrete window.
//  * Discrete window is a simple rate limiting algorithm that allows a certain number of requests per time window.
//  * Window starts when the first request is made. Relies on TTL for target cache entry to reset the window.
//  * @param target the target to rate limit. this is used as the key in the cache, e.g. the IP address of the requester
//  * @param limit the number of requests allowed per second
//  * @param window_length the size of the time window in milliseconds
//  * @param cache the remote cache to use to monitor the rate limit
//  * @returns `status` "OK" or "DENIED"; `saturation` is the number of requests made in the current window; if 0 then the target
//  *  did not exist in the cache (i.e. first request)
//  */
// export function fixed_window(target: string, limit: number, window_length: number, cache: RemoteCache): { status: string; counter: number; } {
// 	let saturation: number | null = cache.get(target);

// 	if (saturation) { // target cache entry exists

// 		//// cache1.set(target, target_cache + 1, 1000); // set() resets the ttl (just like in Redis)! undesirable!
// 		cache.incr(target); // incr() does not reset ttl (just like in Redis)

// 		if (saturation < limit) { // increment the saturation
// 			return { status: 'OK', counter: saturation };
// 		} else { // we hit saturation threshold
// 			return { status: 'DENIED', counter: saturation };
// 		}

// 	} else { // target cache entry does not exist

// 		cache.set(target, 1, window_length);
// 		return { status: 'OK', counter: 0 };

// 	}
// }



export function fixed_window(cache: RemoteCache, key: string, limit: number, window_length_ms: number = 1000): { status: string; counter: number; } {
	let counter: number | null = cache.get(key);

	if (counter !== null )  {
		if (counter < limit) {
			cache.incr(key);
			return { status: "OK", counter: counter + 1 };
		} else {
			return { status: "DENIED", counter };
		}
	} else {
		cache.set(key, 1, window_length_ms);
		return { status: "OK", counter: 1 };
	}
}

function enforcedAvg(cache: RemoteCache, key: string, limitRps: number): { status: string } {
  const exclusionWindow = 1000 / limitRps;

  const cacheTarget = cache.get(key);

  if (cacheTarget !== undefined) {
    return { status: "DENIED" };
  } else {
    cache.set(key, 1, exclusionWindow);
    return { status: "OK" };
  }
}

// function sliding_window(cache: RemoteCache, key: string, limit: number, window_length_ms: number = 1000) {

//   let times: Date[] = cache.get(key);
//   if (times !== undefined) { // cache entry exists

//     // remove all times that are outside the window
//     times = times.filter(time => (new Date()).getTime() - time.getTime() < window_length_ms);

//     if (times.length < limit) {
//       times.push(new Date());
//       cache.set(key, times, window_length_ms);
//       return {"status": "OK", "counter": times.length, "new": false};
//     } else {
//       return {"status": "DENIED", "counter": times.length, "new": false};
//     }

//   } else {
//     cache.set(key, [new Date()], window_length_ms);
//     return {"status": "OK", "counter": 1, "new": true};
//   }
// }

// function leakyBucket(cache: RemoteCache,
// 	key: string,
// 	limit: number,
// 	windowLengthMs = 1000,
// 	mode: 'soft' | 'hard' = 'soft'
//   ) {
// 	let leakRate: number;
// 	if (mode === 'soft') {
// 	  leakRate = limit; // leak at limit-many requests per window
// 	} else if (mode === 'hard') {
// 	  leakRate = 1; // leak at 1 request per window
// 	} else {
// 	  throw new Error(`Invalid mode: ${mode}`);
// 	}
  
// 	const entry: {
// 		counter: number;
// 		time: Date;
// 	  } | undefined = dummyCache.get(key);
  
// 	if (entry !== undefined) {
// 	  // unpack the cache entry because `['key']` notation is ugly
// 	  let { counter, time } = entry;
  
// 	  const deltaTimeMs = dummyTime.now().getTime() - time.getTime(); // time since last request
// 	  counter = Math.max(counter - (deltaTimeMs * leakRate) / windowLengthMs, 0); // get the extrapolated counter value
  
// 	  if (counter + 1 < limit) {
// 		// increment the counter
// 		dummyCache.set(
// 		  key,
// 		  {
// 			counter: counter + 1,
// 			time: dummyTime.now(),
// 		  },
// 		  (counter + 1) * 1000 / leakRate
// 		);
  
// 		// set the target cache entry with ttl
// 		return { status: 'OK', counter: counter + 1, new: false };
// 	  } else {
// 		// we hit counter threshold
// 		return { status: 'DENIED', counter, new: false };
// 	  }
// 	} else {
// 	  // cache entry does not exist
// 	  dummyCache.set(
// 		key,
// 		{
// 		  counter: 1,
// 		  time: dummyTime.now(),
// 		},
// 		windowLengthMs / leakRate
// 	  ); // set the target cache entry with ttl
// 	  return { status: 'OK', counter: 1, new: true };
// 	}
//   }
