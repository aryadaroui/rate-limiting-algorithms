import rich.traceback

rich.traceback.install()

import random
from rich.pretty import pprint
from plot import *
from typing import Callable
from rate_limiters import *
import globals


def generate_random_times(num: int, duration: float, start_time: float = 0.0) -> list:
    """
    Generates a list of `num` random times between `start_time` and `start_time + duration`.

    Args:
        `num` (int): The number of random times to generate.
        `duration` (float): The duration of the time range to generate random times within.
        `start_time` (float, optional): The start time of the time range to generate random times within. Defaults to 0.0.

    Returns:
        list: A list of `num` random times between `start_time` and `start_time + duration`.
    """
    return sorted([random.uniform(start_time, (start_time + duration) * 1000) for _ in range(num)])

def generate_times(rps: float, duration: float, start_time: float = 0.0) -> list:
    ''' Generates a list of times in milliseconds starting from the given start time.'''
    times_ms = []
    interval = 1000 / rps
    for i in range(int(rps * duration)):
        times_ms.append(start_time + (i + 1) * interval)  # i + 1 to make it not start at 0
    return times_ms

def experiment(rate_limiter: Callable, rate_limiter_args: dict, plotter: Callable):

	data = {
		"rate_limiter": rate_limiter.__name__,
		"rps": RPS,
		"duration": DURATION,
	    "plot": []
	}

	# rate limiter specific experiment data
	data.update(rate_limiter_args)

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

LIMIT = 5  # max # of requests allowed per window
WINDOW_LENGTH_MS = 1000  # size of the time window in milliseconds

uniform_times = generate_times(RPS, DURATION) 
random_times = generate_random_times(int(DURATION * RPS), DURATION)
cross_window_times = [x for x in uniform_times if x < 200 or x > 700]

bursts_times = [
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

def experiment_batch(title: str, limiters: list[Callable], single_plots: bool, subplots: bool, json: bool, file_append=''):
	
	figs: list = []
	subplot_titles = []

	if fixed_window in limiters:
		subplot_titles.append('Fixed window')
		figs.append(
			experiment(
				fixed_window, {
					'key': 'global',
					'limit': LIMIT,
					'window_length_ms': WINDOW_LENGTH_MS
				}, plot_fixed_window
			)
		)
	if enforced_avg in limiters:
		subplot_titles.append('Enforced average')
		figs.append(
			experiment(
				enforced_avg,
				{
					'key': 'global',
	    			'limit_rps': LIMIT
				},
				plot_enforced_avg
			)
		)
	if sliding_window in limiters:
		subplot_titles.append('Sliding window')
		figs.append(
			experiment(
				sliding_window, {
					'key': 'global',
					'limit': LIMIT,
					'window_length_ms': WINDOW_LENGTH_MS,
				}, plot_sliding_window
			)
		)
	if leaky_bucket in limiters:
		subplot_titles.append('Leaky bucket, soft')
		figs.append(
		    experiment(
		        leaky_bucket, {
		            'key': 'global',
		            'limit': LIMIT,
		            'window_length_ms': WINDOW_LENGTH_MS,
		            'mode': 'soft'
		        }, plot_leaky_bucket
		    )
		)
		subplot_titles.append('Leaky bucket, hard')
		figs.append(
		    experiment(
		        leaky_bucket, {
		            'key': 'global',
		            'limit': LIMIT,
		            'window_length_ms': WINDOW_LENGTH_MS,
		            'mode': 'hard'
		        }, plot_leaky_bucket
		    )
		)


	all_figs = figs_to_subplot(
		figs,
		title=title,
		subplot_titles = subplot_titles,
		vertical_spacing = 0.05
	)

	
	if single_plots:
		for fig in figs:
			fig.show()

	if subplots:
		all_figs.show()

	if json:
		append = '_' + file_append if file_append else ''

		for fig in figs:
			title = fig.layout.title.text

			if 'soft' in title:
				filename = f'./{title.split("(")[0]}_soft'
			elif 'hard' in title:
				filename = f'./{title.split("(")[0]}_hard'
			else:
				filename = f'./{title.split("(")[0]}'

			fig.write_json(f'./{filename}{append}.json')

		all_figs.write_json(f'./subplots{append}.json')

if __name__ == "__main__":

	TIMES_MS = uniform_times
	experiment_batch(
		f'Rate limiters -- uniform times; {RPS} rps, {DURATION} s; limit: {LIMIT} req / {WINDOW_LENGTH_MS} ms',
		[
			fixed_window,
			enforced_avg,
			sliding_window,
			leaky_bucket
		],
		single_plots = False,
		subplots = True,
		json = True
	)

	TIMES_MS = random_times
	experiment_batch(
		f'Rate limiters -- random times; ~{RPS} rps, {DURATION} s; limit: {LIMIT} req / {WINDOW_LENGTH_MS} ms',
		[
			fixed_window,
			enforced_avg,
			sliding_window,
			leaky_bucket
		],
		single_plots = False,
		subplots = False,
		json = False,
		file_append = 'random'
	)

	TIMES_MS = cross_window_times
	experiment_batch(
		f'Rate limiters -- cross-window times; {RPS} rps, {DURATION} s; limit: {LIMIT} req / {WINDOW_LENGTH_MS} ms',
		[
			fixed_window,
			enforced_avg,
			sliding_window,
			leaky_bucket
		],
		single_plots = False,
		subplots = True,
		json = True,
		file_append = 'cross_window'
	)



a = fixed_window('a', 5, 1000) 
