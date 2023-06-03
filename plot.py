import sys
import json
import pandas as pd
import rich.traceback
from rich.pretty import pprint
from plotly import graph_objects as go

rich.traceback.install()  # prettier traceback
# __builtins__.print = pprint # override print to pprint


def debugger_is_active() -> bool:
	"""Return if the debugger is currently active"""
	return hasattr(sys, 'gettrace') and sys.gettrace() is not None


def plot_discrete_window(data: dict) -> None:
	"""Plot the discrete window data"""

	df = pd.DataFrame(data['plot'])
	pprint(df)
	fig = go.Figure()

	# the saturation cycles
	# create a boolean mask for the edge of a window, where the status changes from DENIED to OK.
	mask = (df['status'] == 'OK') & (df['status'].shift() == 'DENIED')
	df['window'] = mask.cumsum() # use cumsum to create a cycle number for each window

	# iterate over the unique values in window
	for window in df['window'].unique():
		fig.add_trace(
			go.Scatter(
				x = df[df['window'] == window]['time'],
				y = df[df['window'] == window]['saturation'],
				name = f"saturation, window {window}",
				mode = "lines",
				line_color = "slateblue",
				opacity = 0.5
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
	    xshift = -20,
	    xref = 'paper',
	    yref = 'y',
	    font = dict(color = "tomato",)
	)

	# the windows
	first_ok_times = df[df['status'] == 'OK'].groupby((df['status'] != df['status'].shift()).cumsum()).first()['time'].tolist()
	for first_ok_time in first_ok_times:
		fig.add_vrect(
		    x0 = first_ok_time,
		    x1 = first_ok_time + data['experiment']['window_length'],
		    fillcolor = "black",
		    opacity = 0.2,
		    layer = "below",
		    line_width = 0,
		)

		fig.add_vline(x = first_ok_time, line_width = 1, line_color = "darkgreen", layer = "below", opacity = 0.5)

		fig.add_vline(
		    x = first_ok_time + data['experiment']['window_length'],
		    line_width = 1,
		    line_color = "darkred",
		    layer = "below",
		    opacity = 0.5
		)

	fig.update_layout(
	    title_text = "discrete_window",
	    template = "plotly_dark",
	)

	fig.show()


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

	plot_discrete_window(data)

	# # get OKs

	# x: list[int] = list(
	#     map(lambda d: d['time'], filter(lambda d: d['status'] == "OK", data)))
	# y: list[int] = list(
	#     map(lambda d: 0, filter(lambda d: d['status'] == "OK", data)))
	# # y: list[str] = list(map(lambda d: d['status'], data))

	# fig = go.Figure()
	# fig.add_trace(go.Scatter(x=x, y=y, mode="markers", name="OK" ))
	# fig.show()
