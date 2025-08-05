from pathlib import Path
from fitparse import FitFile
import gpxpy
import pandas as pd

# === FILE PATHS ===
fit_path = Path("Strava/Brugai_Monte_Parè.fit")
gpx_path = Path("Strava/Brugai_Monte_Parè.gpx")

# === PARSE .FIT ===
fitfile = FitFile(fit_path)
fit_data = []

for record in fitfile.get_messages('record'):
    row = {}
    for field in record:
        row[field.name] = field.value
    fit_data.append(row)

df_fit = pd.DataFrame(fit_data)
df_fit = df_fit[sorted(df_fit.columns)]  # Ordina colonne
if 'timestamp' in df_fit.columns:
    df_fit['timestamp'] = pd.to_datetime(df_fit['timestamp'])

# === PARSE .GPX ===
with open(gpx_path, "r") as gpx_file:
    gpx = gpxpy.parse(gpx_file)

gpx_data = []
for track in gpx.tracks:
    for segment in track.segments:
        for point in segment.points:
            gpx_data.append({
                "time": point.time,
                "latitude": point.latitude,
                "longitude": point.longitude,
                "elevation": point.elevations
            })

df_gpx = pd.DataFrame(gpx_data)
df_gpx['time'] = pd.to_datetime(df_gpx['time'])

# === EXPORT CSV ===
fit_csv_path = "csv/strava_fit.csv"
gpx_csv_path = "csv/strava_gpx.csv"

df_fit.to_csv(fit_csv_path, index=False)
df_gpx.to_csv(gpx_csv_path, index=False)

fit_csv_path, gpx_csv_path
