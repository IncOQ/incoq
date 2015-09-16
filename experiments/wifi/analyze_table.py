# Use pandas to grab some stats.

import pandas as pd
from io import StringIO


# wifi_opt_plot.csv
csv_data = '''
x,Unfiltered,Unfiltered opt,Filtered,Filtered opt
20.0,0.109375,0.078125,0.296875,0.21875
40.0,0.203125,0.1875,0.65625,0.40625
60.0,0.296875,0.28125,0.9375,0.609375
80.0,0.375,0.375,1.265625,0.8125
100.0,0.484375,0.484375,1.625,1.03125
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
