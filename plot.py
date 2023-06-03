import sys
import json
import rich.traceback
from rich.pretty import pprint
from plotly import graph_objects as go

rich.traceback.install()  # prettier traceback
# __builtins__.print = pprint # override print to pprint


def debugger_is_active() -> bool:
	"""Return if the debugger is currently active"""
	return hasattr(sys, 'gettrace') and sys.gettrace() is not None

def plot_discrete_window(data: list[dict]) -> None:
	"""Plot the discrete window data"""
	# get OKs
	x: list[int] = list(
	    map(lambda d: d['time'], filter(lambda d: d['status'] == "OK", data)))
	y: list[int] = list(
	    map(lambda d: 0, filter(lambda d: d['status'] == "OK", data)))
	# y: list[str] = list(map(lambda d: d['status'], data))

	fig = go.Figure()
	fig.add_trace(go.Scatter(x=x, y=y, mode="markers", name="OK" ))
	fig.show()

if __name__ == "__main__":

	if debugger_is_active():
		filename = "discrete_window.json"
	else:
		if len(sys.argv) < 2:
			print(
			    "Please provide the name of the JSON file as a command line argument."
			)
			sys.exit(1)
		filename = sys.argv[1]

	with open(filename) as f:
		data: list[dict] = json.load(f)

	# # get OKs

	# x: list[int] = list(
	#     map(lambda d: d['time'], filter(lambda d: d['status'] == "OK", data)))
	# y: list[int] = list(
	#     map(lambda d: 0, filter(lambda d: d['status'] == "OK", data)))
	# # y: list[str] = list(map(lambda d: d['status'], data))

	# fig = go.Figure()
	# fig.add_trace(go.Scatter(x=x, y=y, mode="markers", name="OK" ))
	# fig.show()
