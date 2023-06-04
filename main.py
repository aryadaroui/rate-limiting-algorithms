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


def experiment(rate_limiter: Callable, rate_lmiter_args: dict, plotter: Callable):

	data = {
	    "experiment": {
	        "rate_limiter": rate_limiter.__name__,
	        "rps": RPS,
	        "duration": DURATION,
	    },
	    "plot": []
	}

	# rate limiter specific experiment data
	data["experiment"].update(rate_lmiter_args)

	for time_ms in TIMES_MS:
		globals.CURRENT_TIME = time_ms
		output = rate_limiter(**rate_lmiter_args)
		output["time_ms"] = time_ms
		data["plot"].append(output)

	pprint(data)
	plotter(data, 'Py')
	globals.cache.reset()


RPS = 9.5  # requests per second
RPS_THRESHOLD = 5  # max requests per second to allow
DURATION = 2  # seconds
WINDOW_LENGTH_MS = 1000  # millisecond

TIMES_MS = generate_times(RPS, DURATION)

if __name__ == "__main__":

	# experiment(
	#     discrete_window, {
	#         'key': 'global',
	#         'threshold': RPS_THRESHOLD,
	#         'window_length_ms': WINDOW_LENGTH_MS
	#     }, plot_discrete_window
	# )

	# experiment(exclusion_window, {'key': 'global', 'rps_threshold': RPS_THRESHOLD}, plot_exclusion_window)

	experiment(
	    sliding_window, {
	        'key': 'global',
	        'threshold': RPS_THRESHOLD,
	        'window_length_ms': WINDOW_LENGTH_MS
	    }, plot_sliding_window
	)
