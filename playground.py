from rich.pretty import pprint
##############################################
import pandas as pd
import numpy as np

# create a sample DataFrame with unevenly spaced time series
df = pd.DataFrame({
    'timestamp': [1, 2, 4, 7, 11],
    'value': [10, 20, 30, 40, 50],
    'status': ['OK', 'OK', 'DENIED', 'OK', 'OK']
})

# create a mapping of status values to numerical values
status_map = {'OK': 1, 'DENIED': 0}

# create a new DataFrame where the 'status' column is replaced with numerical values
df_numeric = df.copy()
df_numeric['status'] = df_numeric['status'].map(status_map)

window_size = 2
df_numeric['timestamp'] = pd.to_datetime(df_numeric['timestamp'], unit='s')
df_numeric = df_numeric.set_index('timestamp')

# Resample data to have consistent time intervals (1 second)
resampled_df = df_numeric.resample('1S').interpolate()

# Calculate the moving average
moving_average = resampled_df['value'].rolling(window=window_size).mean()

# Count the number of 'OK' values in each rolling window
ok_count = resampled_df['status'].rolling(window=window_size).apply(lambda x: (x == 1).sum(), raw=True)

# Print the result
pprint(moving_average)
pprint(ok_count)