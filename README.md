# rate-limiting-algorithms

Examples of simple rate limiting algorithms in TypeScript and Python.

 **The blog post is not out yet, but obviously I've still published this repo publicly. If you're reading this message, it means I haven't cleaned things up yet. Use at your own peril.**

## Usage

This was created to accompany a blog post on rate limiting algorithms, but they've been written in a non-specific way, so you can easily use them for yourself. For more details about their characteristics see [~post not done~].

These algorithms reside in functions in `rate_limiters.ts` and `rate_limiters.py`.

**NOTE**: I use a local dummy `RemoteCache` class to emulate a remote cache because that's a common implementation for rate limiting [~talk about how RemoteCache mimics Redis behavior~]. _You must replace this with your own data storage service / method_. Similarly, the Python implementation uses a global `CURRENT_TIME` variable instead of the `datetime` package, so you'll have to change that too.

### Example

Suppose you have some function `request_handler()`. You can rate limit a specific target key (e.g. the requester's I.P.) by simply calling the rate limiting function and checking its "status".

```python
def request_handler(request_ip: str):
  
  rate_limiter_output = sliding_window(request_ip, limit=5.0, window_length_ms=1000.0)
  
  if rate_limiter_output['status'] == 'OK':
    # 🆗 process request
  else:
    # ⛔️ deny request
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

## Coverage

| Rate limiting algorithm             | Comment | TypeScript | Python |
| ----------------------------------- | :--------: | :----: | :---------------------------------: |
| `discrete_window(...)` |     burst inducing     |   ✅   | ✅ |
| `exclusion_window(...)`, |     burst intolerant. degenerated discrete window     |   ⚠️   | ✅ |
| `simple_sliding_window(...)` |     burst inducing. high bandwidth/storage cost     |   ⚠️   | ✅ |
| `extrapolated_sliding_window(mode='soft')` |     ⭐️ burst tolerant; steady-state limiting ⭐️     |   ⚠️   | ✅ |
| `extrapolated_sliding_window(mode='hard')` |     burst intolerant; transient limiting      |     ⚠️      |   ✅    |
| Leaky bucket                               |           not really a rate limiter           |     ❌      |   ❌    |

Leaky bucket is omitted because it's a traffic shaper; it modifies transmission rate rather than limiting (denying) traffic. However, you can get similar behavior out of the `extrapolated_sliding_window`.

## Can I install this with NPM or PyPI? (No.)

Consider this more a collection of function snippets rather than a package. You **must** add functionality for your remote cache into the rate limiters as an internal component, so there isn't a universal solution that I can/want to package.

This is a tiny amount of code; just copy-paste it :-).

## Plots

[~Plots will go here~]

## License

MIT License. Attribution appreciated but not required.

You *probably* should link to my blog post in your docstring, though.
