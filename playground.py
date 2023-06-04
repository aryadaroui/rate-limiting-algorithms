from rich.pretty import pprint
import pandas as pd

# your series
s = pd.Series([0.105263, 0.210526, 0.315789, 0.421053, 0.526316, 0.631579, 0.736842, 0.842105, 0.947368, 1.052632, 1.157895, 1.263158, 1.368421, 1.473684, 1.578947, 3.684211, 3.789474, 3.894737, 4.000000], name='time')

# calculate the difference between consecutive elements
diff = s.diff()

# select the elements where the difference is greater than 1.0
mask = diff > 1.0

# get the time of the next element
result = s[mask].shift(-1)

pprint(result)
