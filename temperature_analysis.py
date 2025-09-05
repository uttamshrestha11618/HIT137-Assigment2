import pandas as pd, os, glob, numpy as np

BASE = "temperatures"  # folder with CSVs
OUT = "."

# Load & combine all year files
files = sorted(glob.glob(os.path.join(BASE, "*.csv")))
dfs = []
for fp in files:
    year = os.path.basename(fp).split("_")[-1].split(".")[0]
    df = pd.read_csv(fp)
    df["YEAR"] = int(year)
    dfs.append(df)
all_df = pd.concat(dfs, ignore_index=True)

# Long format
months = ["January","February","March","April","May","June","July","August","September","October","November","December"]
long_df = all_df.melt(
    id_vars=["STATION_NAME","STN_ID","LAT","LON","YEAR"],
    value_vars=months,
    var_name="MONTH",
    value_name="TEMP"
)

# Australian seasons
season_map = {
    "December":"Summer","January":"Summer","February":"Summer",
    "March":"Autumn","April":"Autumn","May":"Autumn",
    "June":"Winter","July":"Winter","August":"Winter",
    "September":"Spring","October":"Spring","November":"Spring"
}
long_df["SEASON"] = long_df["MONTH"].map(season_map)

# 1) Seasonal average (ignore NaN)
seasonal = long_df.groupby("SEASON", as_index=False)["TEMP"].mean(numeric_only=True)
seasonal["TEMP"] = seasonal["TEMP"].round(1)
order = pd.Categorical(seasonal["SEASON"], ["Summer","Autumn","Winter","Spring"])
seasonal = seasonal.assign(SEASON=order).sort_values("SEASON")
with open(os.path.join(OUT, "average_temp.txt"), "w") as f:
    for _, r in seasonal.iterrows():
        f.write(f"{r.SEASON}: {r.TEMP:.1f}°C\n")

# 2) Largest temperature range per station (max - min)
stats = long_df.groupby("STATION_NAME", as_index=False)["TEMP"].agg(["min","max"]).reset_index()
stats["range"] = stats["max"] - stats["min"]
stats = stats.dropna(subset=["range"])
max_range = stats["range"].max()
winners = stats[np.isclose(stats["range"], max_range, atol=1e-9)].sort_values("STATION_NAME")
with open(os.path.join(OUT, "largest_temp_range_station.txt"), "w") as f:
    for _, r in winners.iterrows():
        f.write(f"{r['STATION_NAME']}: Range {r['range']:.1f}°C (Max: {r['max']:.1f}°C, Min: {r['min']:.1f}°C)\n")

# 3) Temperature stability (std dev)
stds = long_df.groupby("STATION_NAME", as_index=False)["TEMP"].std(ddof=1).rename(columns={"TEMP":"STD"}).dropna()
min_std, max_std = stds["STD"].min(), stds["STD"].max()
stable = stds[np.isclose(stds["STD"], min_std, atol=1e-12)].sort_values("STATION_NAME")
variable = stds[np.isclose(stds["STD"], max_std, atol=1e-12)].sort_values("STATION_NAME")

def join_entries(df):
    return "; ".join([f"{row.STATION_NAME} ({row.STD:.1f}°C)" for _, row in df.iterrows()])

with open(os.path.join(OUT, "temperature_stability_stations.txt"), "w") as f:
    f.write(f"Most Stable: {join_entries(stable)}\n")
    f.write(f"Most Variable: {join_entries(variable)}\n")
