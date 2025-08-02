from fitparse import FitFile
import pandas as pd

fitfile = FitFile("Strava/Brugai_Monte_Parè.fit")

data = []

for record in fitfile.get_messages('record'):
    record_data = {}
    for field in record:
        record_data[field.name] = field.value
    data.append(record_data)

df_fit = pd.DataFrame(data)
print(df_fit.head())
