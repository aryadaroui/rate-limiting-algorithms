# rate-limiting-algorithms

Examples of simple rate limiting algorithms in Python. This was made for my blog post https://aryadee.dev/blog/rate-limiting-algorithms, but they've been written generically so that you can use them for yourself with minor adjustments.

## Usage

These algorithms reside in functions in [`rate_limiters.py`](https://github.com/aryadaroui/rate-limiting-algorithms/blob/main/rate_limiters.py).

### ⚠️ Adjustments

To run my experiments I used `dummy_*` objects for simulation.

- You must replace my `dummy_cache` with your own data storage solution

- You must replace my `dummy_time` with realtime timestamp in **milliseconds**
  - There are dataclasses provided, but not used for clarity reasons in my blog post. You are encouraged to use them

### Example

Suppose you  you have some function `request_handler()` that handles incoming network traffic. You can rate limit a specific target (e.g. the requester's IP address) by simply calling the rate limiting function and checking its `"status"`. The rate limiter function queries your remote cache, using your target as a key.

```python
def request_handler(request_ip: str):
  
  limiter_result = leaky_bucket(request_ip, limit=5.0, window_length_ms=1000.0, mode='soft')
  
  if limiter_result['status'] == 'OK':
    # 🆗 process request
    # ...
  else:
    # ⛔️ deny request
    # ...
```

### Experiments / testing


#### Python

```bash
pip install -r requirements.txt # install dependencies in requirements.txt
python main.py # to run the Py experiments
```

## Coverage

| Rate limiting algorithm             | Comment |
| ----------------------------------- | :--------: 
| `fixed_window(...)` |     Cross-window overshoot     | 
| `enforced_avg(...)` |     strict; no simultaneity     |  
| `sliding_window(...)` |     expensive data storage     | 
| `leaky_bucket(..., mode='soft')` |     overshoots on bucket fill     |   
| `leaky_bucket(..., mode='hard')` |     Punitive steady state     |   

 `leaky_bucket(..., mode='soft')` is the most flexible. Under continuous load, it will rate limit at steady state with a uniform distribution, and will allow transients of a maximum size of $2\times \text{limit} - 1$.

## Can I install this with PyPI? (No.)

Consider this more a collection of function snippets rather than a package. Currently, you **must** adjust the rate limiters internally for custom use, so it doesn't make sense to package it. I may grow this into a proper package in the future.

For now, this is a small amount of code; just copy-paste it :-).

## Plots

[~Plots will go here~]

- Uniform times
- Random times
- Cross-window times

## License

MIT License. Attribution appreciated but not required.

You may want to maintain reference to this repo / blog post since there's no npm or pip package to track.
