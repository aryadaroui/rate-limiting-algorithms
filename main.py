import rich.traceback

rich.traceback.install()

from rich.pretty import pprint
from plot import *
from typing import Callable
from rate_limiters import *
import globals


def generate_times(rps: float, duration: float, start_time: float = 0.0) -> list:
    ''' Generates a list of times in milliseconds starting from the given start time.'''
    times_ms = []
    interval = 1000 / rps
    for i in range(int(rps * duration)):
        times_ms.append(start_time + (i + 1) * interval)  # i + 1 to make it not start at 0
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

	fig = plotter(data, mode + ' Py')
	globals.cache.reset()
	return fig

RPS = 10  # requests per second for experiment input
DURATION = 3.0  # duration of experiment in seconds

LIMIT = 5  # max requests allowed
WINDOW_LENGTH_MS = 1000  # size of the time window in milliseconds

# TIMES_MS = generate_times(RPS, DURATION)
# TIMES_MS = [
# 	100,
# 	700,
# 	800,
# 	900,
# 	1000,
# 	1100,
# 	1200,
# 	1300,
# 	1400,
# 	1500,
# 	1600,
# 	1700,
# 	1800,
# 	1900,
# 	2000,
# 	2100
# ]

TIMES_MS = [
	100,
	110,
	120,
	130,
	140,
	150,
	1200,
	1210,
	1220,
	1230,
	1240,
	1250,
	2300,
	2310,
	2320,
	2330,
	2340,
	2350,
	7099
]

if __name__ == "__main__":

	figs = []

	# figs.append(
	# 	experiment(
	# 		discrete_window, {
	# 			'key': 'global',
	# 			'threshold': LIMIT,
	# 			'window_length_ms': WINDOW_LENGTH_MS
	# 		}, plot_discrete_window
	# 	)
	# )

	# figs.append(
	# 	experiment(
	# 		exclusion_window,
	# 		{
	# 			'key': 'global',
    # 			'rps_threshold': LIMIT
	# 		},
	# 		plot_exclusion_window
	# 	)
	# )

	figs.append(
	    experiment(
	        extrapolating_window, {
	            'key': 'global',
	            'threshold': LIMIT,
	            'window_length_ms': WINDOW_LENGTH_MS,
	            'mode': 'soft'
	        }, plot_extrapolating_window
	    )
	)

	figs.append(
	    experiment(
	        extrapolating_window, {
	            'key': 'global',
	            'threshold': LIMIT,
	            'window_length_ms': WINDOW_LENGTH_MS,
	            'mode': 'hard'
	        }, plot_extrapolating_window
	    )
	)

	# figs.append(
	#     experiment(
	#         sliding_window, {
	#             'key': 'global',
	#             'threshold': LIMIT,
	#             'window_length_ms': WINDOW_LENGTH_MS,
	#         }, plot_sliding_window
	#     )
	# )


	# for fig in figs:
	# 	fig.show()

	figs_to_subplot(
		figs,
		subplot_titles = [
			'Discrete window',
			'Exclusion window',
			'Extrapolating window, soft',
			'Extrapolating window, hard',
	        'Sliding window'
		],
		vertical_spacing = 0.05
	).show()
