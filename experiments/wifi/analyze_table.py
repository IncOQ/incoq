# Use pandas to grab some stats.

import pandas as pd
from io import StringIO


# wifi_opt_plot.csv
csv_data = '''
x,Unfiltered,Unfiltered opt,Filtered,Filtered opt
10.0,0.045454545454545456,0.0478125,0.15,0.09375
20.0,0.09375,0.09375,0.3078125,0.190625
30.0,0.140625,0.140625,0.4625,0.296875
40.0,0.1890625,0.184375,0.6125,0.3953125
50.0,0.2375,0.2359375,0.784375,0.5
60.0,0.2828125,0.2859375,0.9359375,0.603125
70.0,0.328125,0.3296875,1.0859375,0.703125
80.0,0.375,0.375,1.25,0.8046875
90.0,0.425,0.4265625,1.43125,0.91875
100.0,0.4734375,0.4734375,1.5828125,1.0171875
'''

df = pd.DataFrame.from_csv(StringIO(csv_data))

df['Unfiltered % improvement'] = \
    (df['Unfiltered'] - df['Unfiltered opt']) / df['Unfiltered'] * 100

df['Filtered % improvement'] = \
    (df['Filtered'] - df['Filtered opt']) / df['Filtered'] * 100

df['Filtering unopt overhead'] = \
    (df['Filtered'] / df['Unfiltered'])

df['Filtering + opt overhead'] = \
    (df['Filtered opt'] / df['Unfiltered'])

df = df.apply(lambda x: x.apply(lambda y: round(y, 3)))

print(df)
print()
print(df.mean())
