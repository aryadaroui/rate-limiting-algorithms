import rich.traceback

rich.traceback.install()

from rich.pretty import pprint
from plot import *
from typing import Callable
from rate_limiters import *
import globals


def generate_times(rps: float, duration: float) -> list:
	''' Generates a list of times in milliseconds.'''
	times_ms = []
	interval = 1000 / rps
	for i in range(int(rps * duration)):
		times_ms.append((i + 1) * interval)  # i + 1 to make it not start at 0
	return times_ms


def experiment(rate_limiter: Callable, rate_limiter_args: dict, plotter: Callable):

	data = {
	    "experiment": {
	        "rate_limiter": rate_limiter.__name__,
	        "rps": RPS,
	        "duration": DURATION,
	    },
	    "plot": []
	}

	# rate limiter specific experiment data
	data["experiment"].update(rate_limiter_args)

	for time_ms in TIMES_MS:
		globals.CURRENT_TIME = time_ms
		output = rate_limiter(**rate_limiter_args)
		output["time_ms"] = time_ms
		data["plot"].append(output)

	# pprint(data)

	# if rate_limiter_args has entry 'mode'
	if 'mode' in rate_limiter_args:
		mode = rate_limiter_args['mode']
	else:
		mode = ''

	plotter(data, mode + ' Py')
	globals.cache.reset()


RPS = 5  # requests per second for experiment input
DURATION = 4 # duration of experiment in seconds

LIMIT = 5  # max requests allowed
WINDOW_LENGTH_MS = 1000  # size of the time window in milliseconds

TIMES_MS = generate_times(RPS, DURATION) 

if __name__ == "__main__":

	# experiment(
	#     discrete_window, {
	#         'key': 'global',
	#         'threshold': LIMIT,
	#         'window_length_ms': WINDOW_LENGTH_MS
	#     }, plot_discrete_window
	# )

	# experiment(exclusion_window, {'key': 'global', 'rps_threshold': LIMIT}, plot_exclusion_window)

	# experiment(
	#     sliding_window, {
	#         'key': 'global',
	#         'threshold': LIMIT,
	#         'window_length_ms': WINDOW_LENGTH_MS,
	#         'mode': 'transient'
	#     }, plot_sliding_window
	# )

	# experiment(
	#     sliding_window, {
	#         'key': 'global',
	#         'threshold': LIMIT,
	#         'window_length_ms': WINDOW_LENGTH_MS,
	#         'mode': 'steady_state'
	#     }, plot_sliding_window
	# )

	# experiment(
	#     simple_sliding_window, {
	#         'key': 'global',
	#         'threshold': LIMIT,
	#         'window_length_ms': WINDOW_LENGTH_MS,
	#     }, plot_sliding_window
	# )

	experiment(
	    extrapolated_sliding_window, {
	        'key': 'global',
	        'threshold': LIMIT,
	        'window_length_ms': WINDOW_LENGTH_MS,
			'mode'	: 'transient'
	    }, plot_sliding_window
	)

	# experiment(
	# 	leaky_bucket, {
	# 		'key': 'global',
	# 		'threshold': LIMIT,
	# 		'window_length_ms': WINDOW_LENGTH_MS,
	# 		'mode': 'fast'
	# 	}, plot_sliding_window
	# )