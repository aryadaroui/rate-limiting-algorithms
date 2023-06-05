import sys
import json
import pandas as pd
import rich.traceback
from rich.pretty import pprint
from plotly import graph_objects as go

rich.traceback.install()  # prettier traceback

def plot_discrete_window(data: dict, title_append='') -> None:
	"""Plot the discrete window data"""

	df = pd.DataFrame(data['plot'])
	fig = go.Figure()

	df['time'] = df['time_ms'] / 1000  # convert to seconds
	pprint(df)

	# the saturation cycles
	# create a boolean mask for the edge of a window, where the status changes from DENIED to OK.
	mask = (df['status'] == 'OK') & (df['status'].shift() == 'DENIED')
	df['window_num'] = mask.cumsum() # use cumsum to create a cycle number for each window

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
	    line_dash = "dash",
	    opacity = 1,
	)

	fig.add_annotation(
	    x = 0,
	    y = data['experiment']['threshold'],
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

	fig.show()

def plot_exclusion_window(data: dict, title_append='') -> None:
	"""Plot the exclusion window data"""

	df = pd.DataFrame(data['plot'])
	fig = go.Figure()

	df['time'] = df['time_ms'] / 1000  # convert to seconds
	pprint(df)

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

	fig.show()

def plot_sliding_window(data: dict, title_append='') -> None:
	df = pd.DataFrame(data['plot'])
	fig = go.Figure()

	df['time'] = df['time_ms'] / 1000  # convert to seconds
	# pprint(df)

	# # the saturation cycles
	# # create a boolean mask for the edge of a window, where the status changes from DENIED to OK.
	# mask = (df['status'] == 'OK') & (df['status'].shift() == 'DENIED')
	# df['window_num'] = mask.cumsum() # use cumsum to create a cycle number for each window

	# # iterate over the unique values in window
	# for window in df['window_num'].unique():
	# 	fig.add_trace(
	# 		go.Scatter(
	# 			x = df[df['window_num'] == window]['time'],
	# 			y = df[df['window_num'] == window]['saturation'],
	# 			name = f"saturation, window {window}",
	# 			mode = "lines",
	# 			line_color = "slateblue",
	# 			opacity = 0.7
	# 		)
	# 	)

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
	window_ends = window_ends['time'] + (window_ends['saturation']) * data['experiment']['window_length_ms'] / 1000
	# window_ends = df.loc[df['saturation'].shift(-1) == 1, 'time'] # get times where next saturation is 0

	# for window_start in window_starts:
	# 	fig.add_vline(
	# 	    x = window_start,
	# 	    line_width = 2,
	# 	    line_color = "darkgreen",
	# 	    layer = "below",
	# 	    opacity = 0.5,
	# 	    line_dash = "solid",
	# 	)


	# # add the last time
	# last_time = pd.Series(df['time'].iloc[-1])
	# window_ends = pd.concat([window_ends, last_time])
	# window_ends = window_ends + ((data['experiment']['window_length_ms'] / 1000) * data['experiment']['threshold'])
	# window_ends = window_ends.tolist()


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

		# filter out rows with saturation of 0
		df_filtered = window_df.loc[df['status'] == 'OK']

		# create new dataframe with incremented saturation
		df_duplicated = df_filtered.assign(saturation=df_filtered['saturation'] - 1)

		# concatenate original dataframe with new dataframe
		df_result = pd.concat([window_df, df_duplicated], ignore_index=True).sort_values(['time', 'saturation'], ascending=[True, True])

		fig.add_trace(
			go.Scatter(
				x=df_result['time'],
				y=df_result['saturation'],
				name=f"window {i+1}",
				mode = "lines",
				line_color = "slateblue",
				opacity = 0.7
			)
		)


	


	# window_ends = df.loc[df['saturation'] == 0, 'time'].shift(-1).tolist()

	# the windows
	# first_ok_times = df[df['status'] == 'OK'].groupby((df['status'] != df['status'].shift()).cumsum()).first()['time'].tolist()

	# df['time'].diff() > 1.0
	# for first_ok_time in first_ok_times:
	# 	fig.add_vrect(
	# 	    x0 = first_ok_time,
	# 	    x1 = first_ok_time + data['experiment']['window_length_ms'] / 1000,
	# 	    fillcolor = "gray",
	# 	    opacity = 0.05,
	# 	    layer = "below",
	# 	    line_width = 0,
	# 	)

	# 	fig.add_vline(
	# 		x = first_ok_time, 
	# 		line_width = 2, 
	# 		line_color = "darkgreen", 
	# 		layer = "below", 
	# 		opacity = 0.5, 
	# 		line_dash = "solid"
	# 	)

	# 	fig.add_vline(
	# 	    x = first_ok_time + data['experiment']['window_length_ms'] / 1000,
	# 	    line_width = 2,
	# 	    line_color = "darkred",
	# 	    layer = "below",
	# 	    opacity = 0.5,
	# 	    line_dash = "solid",
	# 	)



	fig.update_layout(
	    title_text = "sliding_window() " + title_append,
	    xaxis_title_text = "time [s]",
	    yaxis_title_text = "saturation",
	    template = "plotly_dark",
	)

	fig.show()

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
