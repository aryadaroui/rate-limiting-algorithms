import sys
import json
import pandas as pd
import rich.traceback
from rich.pretty import pprint
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from main import DURATION, LIMIT

rich.traceback.install()  # prettier traceback

def plot_discrete_window(data: dict, title_append=''):
	"""Plot the discrete window data"""


	df = pd.DataFrame(data['plot'])
	fig = go.Figure()

	df['time'] = df['time_ms'] / 1000  # convert to seconds
	# pprint(df)

	# the saturation cycles
	# create a boolean mask for the edge of a window, where the status changes from DENIED to OK.
	mask = (df['status'] == 'OK') & (df['status'].shift() == 'DENIED')
	df['window_num'] = mask.cumsum() # use cumsum to create a cycle number for each window


	# 	# create new dataframe with incremented saturation
	# df_duplicated = df_filtered.assign(saturation=df_filtered['saturatio5an'] - 1)

	# # concatenate original dataframe with new dataframe
	# df_result = pd.concat([window_df, df_duplicated], ignore_index=True).sort_values(['time', 'saturation'], ascending=[True, True])

	# iterate over the unique values in window
	for window in df['window_num'].unique():
		fig.add_trace(
			go.Scatter(
				x = df[df['window_num'] == window]['time'],
				y = df[df['window_num'] == window]['saturation'],
				name = f"saturation, window {window}",
				mode = "lines",
				line_color = "slateblue",
				opacity = 0.7
			)
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

	# the threshold
	fig.add_hline(
	    y = data['experiment']['threshold'],
	    line_width = 1,
	    line_color = "tomato",
	    line_dash = "solid",
	    opacity = 1,
	)

	fig.add_annotation(
	    x = 0,
	    y = data['experiment']['threshold'],
	    text = "limit",
	    showarrow = False,
	    textangle = 270,
	    xshift = -30,
	    xref = 'paper',
	    yref = 'y',
	    font = dict(color = "tomato",)
	)

	fig.add_hline(
	    y = data['experiment']['threshold'] - 1,
	    line_width = 1,
	    line_color = "tomato",
	    line_dash = "dash",
	    opacity = 1,
	)

	fig.add_annotation(
	    x = 0,
	    y = data['experiment']['threshold'] - 1,
	    text = "threshold",
	    showarrow = False,
	    textangle = 270,
	    xshift = -30,
	    xref = 'paper',
	    yref = 'y',
	    font = dict(color = "tomato",)
	)

	# the windows
	first_ok_times = df[df['status'] == 'OK'].groupby((df['status'] != df['status'].shift()).cumsum()).first()['time'].tolist()
	for first_ok_time in first_ok_times:
		fig.add_vrect(
		    x0 = first_ok_time,
		    x1 = first_ok_time + data['experiment']['window_length_ms'] / 1000,
		    fillcolor = "gray",
		    opacity = 0.05,
		    layer = "below",
		    line_width = 0,
		)

		fig.add_vline(
			x = first_ok_time, 
			line_width = 2, 
			line_color = "darkgreen", 
			layer = "below", 
			opacity = 0.5, 
			line_dash = "solid"
		)

		fig.add_vline(
		    x = first_ok_time + data['experiment']['window_length_ms'] / 1000,
		    line_width = 2,
		    line_color = "darkred",
		    layer = "below",
		    opacity = 0.5,
		    line_dash = "solid",
		)



	fig.update_layout(
	    title_text = "discrete_window() " + title_append,
	    xaxis_title_text = "time [s]",
	    yaxis_title_text = "saturation",
	    template = "plotly_dark",
	)

	# fig.show()
	return fig

def plot_exclusion_window(data: dict, title_append=''):
	"""Plot the exclusion window data"""

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

	exclusion_window = 1 / data['experiment']['rps_threshold']

	first_ok_times = df[df['status'] == 'OK'].groupby((df['status'] != df['status'].shift()).cumsum()).first()['time'].tolist()
	for first_ok_time in first_ok_times:
		fig.add_vrect(
		    x0 = first_ok_time,
		    x1 = first_ok_time + exclusion_window,
		    fillcolor = "gray",
		    opacity = 0.05,
		    layer = "below",
		    line_width = 0,
		)

		fig.add_vline(
			x = first_ok_time,
			line_width = 2,
			line_color = "darkgreen",
			layer = "below",
			opacity = 0.5,
			line_dash = "solid"
		)

		fig.add_vline(
		    x = first_ok_time + exclusion_window,
		    line_width = 2,
		    line_color = "darkred",
		    layer = "below",
		    opacity = 0.5,
		    line_dash = "solid",
		)



	fig.update_layout(
	    title_text = "discrete_window " + title_append,
	    xaxis_title_text = "time [s]",
	    yaxis_title_text = "saturation",
	    template = "plotly_dark",
	)

	fig.update_layout(
	    title_text = "exclusion_window() " + title_append,
	    xaxis_title_text = "time [s]",
	    # yaxis_title_text = "",
	    template = "plotly_dark",
	)

	# fig.show()
	return fig

def plot_extrapolating_window(data: dict, title_append=''):
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

	

	# the limit & threshold
	fig.add_hline(
	    y = data['experiment']['threshold'],
	    line_width = 1,
	    line_color = "tomato",
	    line_dash = "solid",
	    opacity = 1,
	)

	fig.add_annotation(
	    x = 0,
	    y = data['experiment']['threshold'],
	    text = "limit",
	    showarrow = False,
	    textangle = 270,
	    xshift = -30,
	    xref = 'paper',
	    yref = 'y',
	    font = dict(color = "tomato",)
	)

	fig.add_hline(
	    y = data['experiment']['threshold'] - 1,
	    line_width = 1,
	    line_color = "tomato",
	    line_dash = "dash",
	    opacity = 1,
	)

	fig.add_annotation(
	    x = 0,
	    y = data['experiment']['threshold'] -1,
	    text = "threshold",
	    showarrow = False,
	    textangle = 270,
	    xshift = -30,
	    xref = 'paper',
	    yref = 'y',
	    font = dict(color = "tomato",)
	)

	window_starts =  df.loc[df['new'] == True, 'time'].tolist()
	window_ends = df.groupby('new').apply(lambda group: group[group['status'] == 'OK'].tail(1))

	if data['experiment']['mode'] == 'soft':
		window_ends = window_ends['time'] + (window_ends['saturation'] / data['experiment']['threshold']) * data['experiment']['window_length_ms'] / 1000
	else:
		window_ends = window_ends['time'] + (window_ends['saturation']) * data['experiment']['window_length_ms'] / 1000

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

	# saturation
	for i in range(len(window_starts)):
		start = window_starts[i]
		end = window_ends[i]
		window_df = df[(df['time'] >= start) & (df['time'] <= end)]

		df_filtered = window_df.loc[df['status'] == 'OK']

		# create new dataframe with incremented saturation
		df_duplicated = df_filtered.assign(saturation=df_filtered['saturation'] - 1)

		# concatenate original dataframe with new dataframe
		df_result = pd.concat([window_df, df_duplicated], ignore_index=True).sort_values(['time', 'saturation'], ascending=[True, True])

		fig.add_trace(
			go.Scatter(
				x=df_result['time'],
				y=df_result['saturation'],
				name=f"lifetime {i+1}",
				mode = "lines",
				line_color = "slateblue",
				opacity = 0.7
			)
		)

		ez_df = window_df[['time', 'status']]
		num_oks = []

		for end_time in ez_df['time']:
			start_time =  max(end_time - data['experiment']['window_length_ms'] / 1000, 0)

			mask = (ez_df['time'] >= start_time) & (ez_df['time'] < end_time)

			# Filter the rows based on the mask
			filtered_df = ez_df.loc[mask]

			# count the number of OKs
			num_oks.append(len(filtered_df[filtered_df['status'] == 'OK']))

			# pprint(filtered_df)


		fig.add_trace(
			go.Scatter(
				x = ez_df['time'],
				y = num_oks,
				name = "num OKs",
				mode = "lines+markers",
				line_color = "darkorange",
				opacity = 0.7
			)
		)

	fig.update_layout(
	    title_text = "sliding_window() " + title_append,
	    xaxis_title_text = "time [s]",
	    yaxis_title_text = "saturation",
	    template = "plotly_dark",
	    
		xaxis_range = [0, data['experiment']['duration'] + 1],
		yaxis_range = [-1, 10],
	)

	# fig.show()
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

	

	# the limit & threshold
	fig.add_hline(
	    y = data['experiment']['threshold'],
	    line_width = 1,
	    line_color = "tomato",
	    line_dash = "solid",
	    opacity = 1,
	)

	fig.add_annotation(
	    x = 0,
	    y = data['experiment']['threshold'],
	    text = "limit",
	    showarrow = False,
	    textangle = 270,
	    xshift = -30,
	    xref = 'paper',
	    yref = 'y',
	    font = dict(color = "tomato",)
	)

	fig.add_hline(
	    y = data['experiment']['threshold'] - 1,
	    line_width = 1,
	    line_color = "tomato",
	    line_dash = "dash",
	    opacity = 1,
	)

	fig.add_annotation(
	    x = 0,
	    y = data['experiment']['threshold'] -1,
	    text = "threshold",
	    showarrow = False,
	    textangle = 270,
	    xshift = -30,
	    xref = 'paper',
	    yref = 'y',
	    font = dict(color = "tomato",)
	)

	window_starts =  df.loc[df['new'] == True, 'time'].tolist()
	window_ends = df.groupby('new').apply(lambda group: group[group['status'] == 'OK'].tail(1))
	window_ends = window_ends['time'] + data['experiment']['window_length_ms'] / 1000
	# window_ends = window_ends['time'] + (window_ends['saturation']) * data['experiment']['window_length_ms'] / 1000

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



	
	# saturation
	for i in range(len(window_starts)):
		start = window_starts[i]
		end = window_ends[i]
		window_df = df[(df['time'] >= start) & (df['time'] <= end)]

		df_filtered = window_df.loc[df['status'] == 'OK']

		# create new dataframe with incremented saturation
		df_duplicated = df_filtered.assign(saturation=df_filtered['saturation'] - 1)

		# concatenate original dataframe with new dataframe
		df_result = pd.concat([window_df, df_duplicated], ignore_index=True).sort_values(['time', 'saturation'], ascending=[True, True])

		fig.add_trace(
			go.Scatter(
				x=df_result['time'],
				y=df_result['saturation'],
				name=f"lifetime {i+1}",
				mode = "lines",
				line_color = "slateblue",
				opacity = 0.7
			)
		)


		ez_df = window_df[['time', 'status']]
		num_oks = []

		for end_time in ez_df['time']:
			start_time =  max(end_time - data['experiment']['window_length_ms'] / 1000, 0)

			mask = (ez_df['time'] >= start_time) & (ez_df['time'] < end_time)

			# Filter the rows based on the mask
			filtered_df = ez_df.loc[mask]

			# count the number of OKs
			num_oks.append(len(filtered_df[filtered_df['status'] == 'OK']))

			# pprint(filtered_df)


		fig.add_trace(
			go.Scatter(
				x = ez_df['time'],
				y = num_oks,
				name = "num OKs",
				mode = "lines+markers",
				line_color = "darkorange",
				opacity = 0.7
			)
		)

	fig.update_layout(
	    title_text = "sliding_window() " + title_append,
	    xaxis_title_text = "time [s]",
	    yaxis_title_text = "saturation",
	    template = "plotly_dark",
	    
		xaxis_range = [0, data['experiment']['duration'] + 1],
		yaxis_range = [-1, 10],
	)

	return fig

def figs_to_subplot(figs: list[go.Figure], **kwargs):
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
		for annotation in fig.layout.annotations:
			subplot.add_annotation(annotation, row=i+1, col=1)

	subplot.update_layout(
	    template = "plotly_dark",
	    xaxis_range = [0, DURATION + 1],
	    # yaxis_range = [-1, LIMIT * 2],
	    legend=dict(groupclick="toggleitem")
	)

	subplot.update_xaxes(title_text="time [s]", row=len(figs), col=1)

	return subplot



def debugger_is_active() -> bool:
	"""Return if the debugger is currently active"""
	return hasattr(sys, 'gettrace') and sys.gettrace() is not None

if __name__ == "__main__":

	if debugger_is_active():
		file_path = "./data/discrete_window.json"
	else:
		if len(sys.argv) < 2:
			print("Please provide the name of the JSON file as a command line argument.")
			sys.exit(1)
		file_path = sys.argv[1]

	with open(file_path) as f:
		data: dict = json.load(f)

	filename = file_path.split("/")[-1].split(".")[0]

	match filename:
		case "discrete_window":
			plot_discrete_window(data)
		case _:
			raise ValueError(f"No matching plot function for filename: {filename}")
