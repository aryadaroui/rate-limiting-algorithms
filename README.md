# rate-limiting-algorithms

Examples of simple rate limiting algorithms in TypeScript and Python. This was made for my blog post https://aryadee.dev/blog/rate-limiting-algorithms, but they've been written generically so that you can use them for yourself with minor tweaking.



**Work in progress, but I've obviously still published this repo publicly. If you're reading this message, it means I haven't cleaned things up yet. Use at your own peril.**

## Usage

##### These algorithms reside in functions in[ `rate_limiters.ts`]() and [`rate_limiters.py`]().

⚠️ **NOTE** ⚠️: I use a local dummy `RemoteCache` class to emulate a remote cache because that's a common implementation for rate limiting. _You must replace this with your own data storage service / method_. Similarly, the Python implementation uses a global `CURRENT_TIME` variable instead of the `datetime` package, so you'll have to change that too.

### Example

Suppose you  you have some function `request_handler()` that handles incoming network traffic. You can rate limit a specific target (e.g. the requester's IP address) by simply calling the rate limiting function and checking its "status". The rate limiter function queries your remote cache, using your target as a key.

```python
def request_handler(request_ip: str):
  
  rate_limiter_output = sliding_window(request_ip, limit=5.0, window_length_ms=1000.0)
  
  if rate_limiter_output['status'] == 'OK':
    # 🆗 process request
    # ...
  else:
    # ⛔️ deny request
    # ...
```

### Experiments / testing

To run the experiments:

```bash
npm install # to install dependencies
npm run start # to run the realtime TS experiments
```

```bash
python3 main.py # to run the Py experiments
```

The TypeScript experiments are run in real-time with worker threads, and spawn a Python process to plot the data. The Python experiments are run statically.

## Coverage

| Rate limiting algorithm             | Comment | TypeScript | Python |
| ----------------------------------- | :--------: | :----: | :---------------------------------: |
| `fixed_window(...)` |     Cross-window flaw     |   ✅   | ✅ |
| `enforced_avg(...)` |     No simultaneous requests     |   ⚠️   | ✅ |
| `sliding_window(...)` |     expensive data storage     |   ⚠️   | ✅ |
| `leaky_bucket(..., mode='soft')` |     ⭐️ slightly overshoots on fill ⭐️     |   ⚠️   | ✅ |
| `leaky_bucket(..., mode='hard')` |     Punitive steady state     |     ⚠️      |   ✅    |

 `leaky_bucket(..., mode='soft')` is the most flexible. Under continuous load, it will rate limit at steady state with a uniform distribution, and will allow transients of a maximum size of $2\times \text{limit} - 1$.

## Can I install this with NPM or PyPI? (No.)

Consider this more a collection of function snippets rather than a package. Currently, you **must** add functionality for your remote cache into the rate limiters internally, so it doesn't make sense to package it. I may add functionality to pass in a cache client or compliant set/get/incr functions in the future, which would make it more package-able.

Realistically, this is a small amount of code; just copy-paste it :-).

## Plots

[~Plots will go here~]

## License

MIT License. Attribution appreciated but not required.

You may want to maintain reference to this repo / blog post since there's no npm or pip package to track.

# Notes for myself

- For package-ability, a template class with abstract methods that user implements for their DB access
  - then they pass an instance of that class in to a generic `rate_limiter` constructor or function, which contains the desired rate limiting functions 

  - need to enforce strict typing on the data access; every rate limiter has different payloads
