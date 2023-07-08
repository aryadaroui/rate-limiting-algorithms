'''Plotting functions used for https://aryadee.dev/blog/rate-limiting-algorithms
'''

import sys
import json
import pandas as pd
import rich.traceback
from rich.pretty import pprint
from plotly import graph_objects as go
from plotly.subplots import make_subplots

rich.traceback.install()  # prettier traceback

MARGIN = dict(
			t = 40,
			b = 20,
			l = 35,
			r = 20
		)

def plot_fixed_window(data: dict, title_append=''):
	"""Plot the fixed window data"""


	df = pd.DataFrame(data['plot'])
	fig = go.Figure()

	df['time'] = df['time_ms'] / 1000  # convert to seconds

	window_starts =  list(df[df['counter'] == 1]['time'])
	window_ends = list(map(lambda x: x + data['window_length_ms'] / 1000, window_starts))

	for idx, (window_start, window_end) in enumerate(zip(window_starts, window_ends)):
		fig.add_vrect(
		    x0 = window_start,
		    x1 = window_end,
		    fillcolor = "gray",
		    opacity = 0.05,
		    layer = "below",
		    line_width = 0,
		)

		fig.add_vline(
			x = window_start, 
			line_width = 3, 
			line_color = "darkgreen", 
			layer = "below", 
			opacity = 0.5, 
			line_dash = "solid"
		)

		fig.add_vline(
		    x = window_end,
		    line_width = 3,
		    line_color = "darkred",
		    layer = "below",
		    opacity = 0.7,
		    line_dash = "solid",
		)

		window_df = df[(df['time'] >= window_start) & (df['time'] < window_end) ]
		# df_duplicated = window_df.assign(counter=window_df['counter'] - 1)
		df_duplicated = window_df.copy()
		df_duplicated.loc[df_duplicated['status'] == 'OK', 'counter'] -= 1
		df_result = pd.concat([window_df, df_duplicated], ignore_index=True).sort_values(['time', 'counter'], ascending=[True, True])

		fig.add_trace(
		go.Scatter(
			x=df_result['time'],
			y=df_result['counter'],
			name=f"counter #{idx}",
			mode = "lines",
			line_color = "gainsboro",
			opacity = 0.7
		)
	)
		
	# the limit line
	fig.add_hline(
	    y = data['limit'],
	    line_width = 1,
	    line_color = "deeppink",
	    line_dash = "dash",
	    opacity = 1,
	)
	fig.add_annotation(
	    x = 0,
	    y = data['limit'],
	    text = "limit",
	    showarrow = False,
	    textangle = 270,
	    xshift = -30,
	    xref = 'paper',
	    yref = 'y',
	    font = dict(color = "deeppink",)
	)

	# the OKs
	fig.add_trace(
	    go.Scatter(
	        x = df[df['status'] == "OK"]['time'],
	        # choose y to be 0 for all OKs
	        y = [0] * len(df[df['status'] == "OK"]['time']),
	        name = "OK",
	        mode = "markers",
	        marker = dict(
	            color = "darkturquoise",
	            size = 10,
	        ),
	    )
	)

	# the DENIEDs
	fig.add_trace(
	    go.Scatter(
	        x = df[df['status'] == "DENIED"]['time'],
	        # choose y to be 0 for all OKs
	        y = [0] * len(df[df['status'] == "DENIED"]['time']),
	        name = "DENIED",
	        mode = "markers",
	        marker = dict(
	            color = "crimson",
	            symbol = "x",
	            size = 10,
	        ),
	    )
	)

	get_num_oks(df, data['window_length_ms'], fig )

	fig.update_layout(
	    title_text = "fixed_window() " + title_append,
	    xaxis_title_text = "time [s]",
	    template = "plotly_dark",
		margin = MARGIN
	)
	return fig

def plot_enforced_avg(data: dict, title_append=''):
	"""Plot the enforced average data"""

	df = pd.DataFrame(data['plot'])
	fig = go.Figure()

	df['time'] = df['time_ms'] / 1000  # convert to seconds
	# pprint(df)

	# the OKs
	fig.add_trace(
	    go.Scatter(
	        x = df[df['status'] == "OK"]['time'],
	        # choose y to be 0 for all OKs
	        y = [0] * len(df[df['status'] == "OK"]['time']),
	        name = "OK",
	        mode = "markers",
	        marker = dict(
	            color = "darkturquoise",
	            size = 10,
	        ),
	    )
	)

	# the DENIEDs
	fig.add_trace(
	    go.Scatter(
	        x = df[df['status'] == "DENIED"]['time'],
	        # choose y to be 0 for all OKs
	        y = [0] * len(df[df['status'] == "DENIED"]['time']),
	        name = "DENIED",
	        mode = "markers",
	        marker = dict(
	            color = "crimson",
	            symbol = "x",
	            size = 10,
	        ),
	    )
	)

	# the windows
	exclusion_window = 1 / data['limit_rps']
	window_starts =  list(df[df['status'] == 'OK']['time'])
	window_ends = list(map(lambda x: x + exclusion_window, window_starts))

	for window_start, window_end in zip(window_starts, window_ends):
		fig.add_vrect(
		    x0 = window_start,
		    x1 = window_end,
		    fillcolor = "gray",
		    opacity = 0.05,
		    layer = "below",
		    line_width = 0,
		)

		fig.add_vline(
			x = window_start, 
			line_width = 3, 
			line_color = "darkgreen", 
			layer = "below", 
			opacity = 0.5, 
			line_dash = "solid"
		)

		fig.add_vline(
		    x = window_end,
		    line_width = 3,
		    line_color = "darkred",
		    layer = "below",
		    opacity = 0.7,
		    line_dash = "solid",
		)




	fig.add_hline(
	    y = data['limit_rps'],
	    line_width = 1,
	    line_color = "deeppink",
	    line_dash = "dash",
	    opacity = 1,
	)

	fig.add_annotation(
	    x = 0,
	    y = data['limit_rps'],
	    text = "limit",
	    showarrow = False,
	    textangle = 270,
	    xshift = -30,
	    xref = 'paper',
	    yref = 'y',
	    font = dict(color = "deeppink",)
	)

	fig.update_layout(
	    title_text = "exclusion_window() " + title_append,
	    xaxis_title_text = "time [s]",
	    # yaxis_title_text = "",
	    template = "plotly_dark",
	    margin = MARGIN
	)

	get_num_oks(df, 1000, fig )

	return fig

def plot_sliding_window(data: dict, title_append: str = ""):
	"""Plot the sliding window data."""
	df = pd.DataFrame(data['plot'])
	fig = go.Figure()

	df['time'] = df['time_ms'] / 1000  # convert to seconds
	# pprint(df)


	# the OKs
	fig.add_trace(
	    go.Scatter(
	        x = df[df['status'] == "OK"]['time'],
	        # choose y to be 0 for all OKs
	        y = [0] * len(df[df['status'] == "OK"]['time']),
	        name = "OK",
	        mode = "markers",
	        marker = dict(
	            color = "darkturquoise",
	            size = 10,
	        ),
	    )
	)

	# the DENIEDs
	fig.add_trace(
	    go.Scatter(
	        x = df[df['status'] == "DENIED"]['time'],
	        # choose y to be 0 for all OKs
	        y = [0] * len(df[df['status'] == "DENIED"]['time']),
	        name = "DENIED",
	        mode = "markers",
	        marker = dict(
	            color = "crimson",
	            symbol = "x",
	            size = 10,
	        ),
	    )
	)

	

	# the limit
	fig.add_hline(
	    y = data['limit'],
	    line_width = 1,
	    line_color = "deeppink",
	    line_dash = "dash",
	    opacity = 1,
	)

	fig.add_annotation(
	    x = 0,
	    y = data['limit'],
	    text = "limit",
	    showarrow = False,
	    textangle = 270,
	    xshift = -30,
	    xref = 'paper',
	    yref = 'y',
	    font = dict(color = "deeppink",)
	)

	window_starts =  df.loc[df['new'] == True, 'time'].tolist()
	window_starts_inf = window_starts + [float('inf')] # dupe widnow_starts w/ inf at the end so we can iterate over pairs

	for idx, window_start in enumerate(window_starts):
		window_df = df[(df['time'] >= window_starts_inf[idx]) & (df['time'] < window_starts_inf[idx + 1])]
		last_ok = window_df[window_df['status'] == 'OK'].tail(1)['time'].values[0]
		window_end = last_ok + data['window_length_ms'] / 1000

		fig.add_vrect(
		    x0 = window_start,
		    x1 = window_end,
		    fillcolor = "gray",
		    opacity = 0.05,
		    layer = "below",
		    line_width = 0,
		)

		fig.add_vline(
			x = window_start, 
			line_width = 2,
			line_color = "darkgreen",
			layer = "below",
			opacity = 0.5,
			line_dash = "solid"
		)

		fig.add_vline(
		    x = window_end,
		    line_width = 2,
		    line_color = "darkred",
		    layer = "below",
		    opacity = 0.5,
		    line_dash = "solid",
		)

		df_filtered = window_df.loc[df['status'] == 'OK']

		# create new dataframe with incremented counter
		df_duplicated = df_filtered.assign(counter=df_filtered['counter'] - 1)

		# concatenate original dataframe with new dataframe
		df_result = pd.concat([window_df, df_duplicated], ignore_index=True).sort_values(['time', 'counter'], ascending=[True, True])

		fig.add_trace(
			go.Scatter(
				x=df_result['time'],
				y=df_result['counter'],
				name=f"counter #{idx}",
				mode = "lines",
				line_color = "gainsboro",
				opacity = 0.7
			)
		)


	fig.update_layout(
	    title_text = "sliding_window() " + title_append,
	    xaxis_title_text = "time [s]",
	    # yaxis_title_text = "counter",
	    template = "plotly_dark",
	    
		xaxis_range = [0, data['duration'] + 1],
		yaxis_range = [-1, 10],
		margin = MARGIN
	)

	get_num_oks(df, data['window_length_ms'], fig )

	return fig	

def plot_leaky_bucket(data: dict, title_append=''):
	"""Plot the leaky bucket data."""
	df = pd.DataFrame(data['plot'])
	fig = go.Figure()

	df['time'] = df['time_ms'] / 1000  # convert to seconds

	# the OKs
	fig.add_trace(
	    go.Scatter(
	        x = df[df['status'] == "OK"]['time'],
	        # choose y to be 0 for all OKs
	        y = [0] * len(df[df['status'] == "OK"]['time']),
	        name = "OK",
	        mode = "markers",
	        marker = dict(
	            color = "darkturquoise",
	            size = 10,
	        ),
	    )
	)

	# the DENIEDs
	fig.add_trace(
	    go.Scatter(
	        x = df[df['status'] == "DENIED"]['time'],
	        # choose y to be 0 for all OKs
	        y = [0] * len(df[df['status'] == "DENIED"]['time']),
	        name = "DENIED",
	        mode = "markers",
	        marker = dict(
	            color = "crimson",
	            symbol = "x",
	            size = 10,
	        ),
	    )
	)

	# the limit
	fig.add_hline(
	    y = data['limit'],
	    line_width = 1,
	    line_color = "deeppink",
	    line_dash = "dash",
	    opacity = 1,
	)

	fig.add_annotation(
	    x = 0,
	    y = data['limit'],
	    text = "limit",
	    showarrow = False,
	    textangle = 270,
	    xshift = -30,
	    xref = 'paper',
	    yref = 'y',
	    font = dict(color = "deeppink",)
	)

	window_starts =  df.loc[df['new'] == True, 'time'].tolist()
	window_starts_inf = window_starts + [float('inf')] # dupe widnow_starts w/ inf at the end so we can iterate over pairs

	for idx, window_start in enumerate(window_starts):
		window_df = df[(df['time'] >= window_starts_inf[idx]) & (df['time'] < window_starts_inf[idx + 1])]
		last_ok = window_df[window_df['status'] == 'OK'].tail(1)['time'].values[0]

		if data['mode'] == 'soft':
			window_end = last_ok + (window_df[window_df['time'] == last_ok]['counter'].values[0] / data['limit']) * data['window_length_ms'] / 1000
		else:
			window_end = last_ok + (window_df[window_df['time'] == last_ok]['counter'].values[0]) * data['window_length_ms'] / 1000

		fig.add_vrect(
		    x0 = window_start,
		    x1 = window_end,
		    fillcolor = "gray",
		    opacity = 0.05,
		    layer = "below",
		    line_width = 0,
		)

		fig.add_vline(
			x = window_start, 
			line_width = 2,
			line_color = "darkgreen",
			layer = "below",
			opacity = 0.5,
			line_dash = "solid"
		)

		fig.add_vline(
		    x = window_end,
		    line_width = 2,
		    line_color = "darkred",
		    layer = "below",
		    opacity = 0.5,
		    line_dash = "solid",
		)

		df_filtered = window_df.loc[df['status'] == 'OK']

		# create new dataframe with incremented counter
		df_duplicated = df_filtered.assign(counter=df_filtered['counter'] - 1)

		# concatenate original dataframe with new dataframe
		df_result = pd.concat([window_df, df_duplicated], ignore_index=True).sort_values(['time', 'counter'], ascending=[True, True])

		fig.add_trace(
			go.Scatter(
				x=df_result['time'],
				y=df_result['counter'],
				name=f"counter #{idx}",
				mode = "lines",
				line_color = "gainsboro",
				opacity = 0.7
			)
		)

	fig.update_layout(
	    title_text = "leaky_bucket() " + title_append,
	    xaxis_title_text = "time [s]",
	    # yaxis_title_text = "counter",
	    template = "plotly_dark",
	    
		xaxis_range = [0, data['duration'] + 1],
		yaxis_range = [-1, 10],
		margin = MARGIN
	)

	get_num_oks(df, data['window_length_ms'], fig)

	return fig

def get_num_oks(df, window_len_ms: float, fig):
	''' gets the number OKs in the last window_len_ms and adds it to the figure.

	note: handles everything input in ms, but plots in s.
	'''

	df = df[['time_ms', 'status']]

	# create new df with new rows for when the window ends
	new_rows = df[df['status'] == 'OK'].copy()
	new_rows['time_ms'] = new_rows['time_ms'] + window_len_ms
	new_rows['status'] = ''

	df = pd.concat([df, new_rows], ignore_index=True).drop_duplicates(subset=['time_ms']).sort_values(['time_ms', 'status'], ascending=[True, True])


	num_oks = []
	for end_time in df['time_ms']:
		start_time =  max(end_time - window_len_ms, 0)

		mask = (df['time_ms'] > start_time) & (df['time_ms'] < end_time) | (df['time_ms'] == end_time) # all the times within the window

		# get the number of OKs within the window
		num_oks.append(df.loc[mask, 'status'].eq('OK').sum())

	df['num_oks'] = num_oks

	fig.add_trace(
		go.Scatter(
			x = df['time_ms'] / 1000,
			y = df['num_oks'],
			name = "num OKs",
			line=dict(shape='hv', color='yellow'),
			mode = "lines",
			line_color = "yellow",
			opacity = 0.7
		)
	)

def figs_to_subplot(figs: list[go.Figure], title: str, duration:float, **kwargs):
	''' takes a list of figures and returns a subplot with them all in it.
	'''
	subplot = make_subplots(
		rows=len(figs),
		cols=1,
		shared_xaxes=True,
		**kwargs
	)

	for i, fig in enumerate(figs):

		for trace in fig.data:
			if 'subplot_titles' in kwargs:
				trace.legendgroup = kwargs['subplot_titles'][i]
				trace.legendgrouptitle.text = kwargs['subplot_titles'][i]
			subplot.add_trace(trace, row=i+1, col=1)
		for shape in fig.layout.shapes:
			subplot.add_shape(shape, row=i+1, col=1)
		# for annotation in fig.layout.annotations:
		# 	subplot.add_annotation(annotation, row=i+1, col=1)

	subplot.update_layout(
	    template = "plotly_dark",
	    xaxis_range = [0, duration + 1],
	    # yaxis_range = [-1, LIMIT * 2],
	    legend=dict(groupclick="toggleitem"),
	    title_text = title,
	    margin = MARGIN
	)

	subplot.update_xaxes(title_text="time [s]", row=len(figs), col=1)

	return subplot

def debugger_is_active() -> bool:
	"""Return true if the debugger is currently active"""
	return hasattr(sys, 'gettrace') and sys.gettrace() is not None

if __name__ == "__main__":

	if debugger_is_active():
		file_path = "./data/fixed_window.json"
	else:
		if len(sys.argv) < 2:
			print("Please provide the name of the JSON file as a command line argument.")
			sys.exit(1)
		file_path = sys.argv[1]

	with open(file_path) as f:
		data: dict = json.load(f)

	filename = file_path.split("/")[-1].split(".")[0]

	match filename:
		case "fixed_window":
			plot_fixed_window(data).show()
		case _:
			raise ValueError(f"No matching plot function for filename: {filename}")
