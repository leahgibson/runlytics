"""
File for grouping running data into weekly metrics

(Weekly) Inputs:
- total distance (mi)
- time in Z2 (min)
- time in Z3 (min)
- time in Z4 (min)
- time in Z5 (min)
- total time (min)
- total elevation gain (ft)
- highest altitude (ft)
- time spent > 6000 ft (min)
- time spend > 10000 ft (min)
- duration of longest run (min)
- max HR (bpm)
- load

(Weekly) Output:
- Avg Z2 pace
"""

import math
import pandas as pd
from data_handling import load_runs, add_elapsed_time, clean_base_runs


def compute_time_in_zone(df, zone):
    df = df.copy()
    hr_zones = {"z2": [141, 158], "z3": [159, 168], "z4": [169, 175], "z5": [176, 196]}

    hr_range = hr_zones[zone]
    df = df[(df["hr"] >= hr_range[0]) & (df["hr"] <= hr_range[1])]

    total_time_min = round(df["time_diff"].sum() / 60, 3)

    return total_time_min


def compute_time_above_alt(df, alt):
    df = df.copy()
    df = df[df["elevation"] >= alt]

    total_time_min = round(df["time_diff"].sum() / 60, 3)

    return total_time_min


def compute_load(df):
    df = df.copy()

    max_hr = 196
    rest_hr = 48

    df["duration"] = df["time_diff"] / 60  # convert sec -> min
    df["duration"] = df["duration"].fillna(0)

    duration_df = df.groupby("hr")["duration"].sum().reset_index()

    load = 0
    for i, row in duration_df.iterrows():
        hr_reserve = (row["hr"] - rest_hr) / (max_hr - rest_hr)
        exponent = hr_reserve * 1.67
        load += row["duration"] * hr_reserve * 0.64 * math.exp(exponent)

    return load


start_date = "20250602"
end_date = "20250817"


run_types = ["z2", "vo2", "sprint", "threshold", "trail"]
all_runs = {}
for run_type in run_types:
    runs = load_runs(start_date=start_date, end_date=end_date, type=run_type)
    all_runs.update(runs)

# Pull stats from each run
daily_columns = [
    "date",
    "total_distance",
    "z2_time",
    "z3_time",
    "z4_time",
    "z5_time",
    "total_time",
    "total_elevation_gain",
    "max_altitude",
    "time_above_6000",
    "time_above_10000",
    "max_hr",
    "total_load",
]
run_stats = pd.DataFrame(columns=daily_columns)
for i, (run_date, df) in enumerate(all_runs.items()):
    stats = {}
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["time_diff"] = df["timestamp"].diff().dt.total_seconds()
    stats["date"] = df["timestamp"][0].date()
    stats["total_distance"] = df["distance"].iloc[-1]
    stats["z2_time"] = compute_time_in_zone(df, "z2")
    stats["z3_time"] = compute_time_in_zone(df, "z3")
    stats["z4_time"] = compute_time_in_zone(df, "z4")
    stats["z5_time"] = compute_time_in_zone(df, "z5")
    stats["total_time"] = round(
        (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds() / 60, 3
    )
    elev_diff = df["elevation"].diff()
    stats["total_elevation_gain"] = elev_diff[elev_diff > 0].sum()
    stats["max_altitude"] = df["elevation"].max()
    stats["time_above_6000"] = compute_time_above_alt(df, 6000)
    stats["time_above_10000"] = compute_time_above_alt(df, 10000)
    stats["max_hr"] = df["hr"].max()
    stats["total_load"] = compute_load(df)

    daily_df = pd.DataFrame(stats, index=[i])
    run_stats = pd.concat([run_stats, daily_df])

run_stats["date"] = pd.to_datetime(run_stats["date"])
run_stats["week"] = run_stats["date"].dt.isocalendar().week
run_stats.sort_values("week", inplace=True, ignore_index=True)

weekly_columns = [
    "week",
    "total_distance",
    "z2_time",
    "z3_time",
    "z4_time",
    "z5_time",
    "total_time",
    "total_elevation_gain",
    "max_altitude",
    "time_above_6000",
    "time_above_10000",
    "lr_duration",
    "max_hr",
    "total_load",
]
weekly_stats = pd.DataFrame(columns=weekly_columns)
for i, (week, group) in enumerate(run_stats.groupby("week")):
    stats = {}
    stats["week"] = week
    stats["total_distance"] = group["total_distance"].sum()
    stats["z2_time"] = group["z2_time"].sum()
    stats["z3_time"] = group["z3_time"].sum()
    stats["z4_time"] = group["z4_time"].sum()
    stats["z5_time"] = group["z5_time"].sum()
    stats["total_time"] = group["total_time"].sum()
    stats["total_elevation_gain"] = group["total_elevation_gain"].sum()
    stats["max_altitude"] = group["max_altitude"].max()
    stats["time_above_6000"] = group["time_above_6000"].sum()
    stats["time_above_10000"] = group["time_above_10000"].sum()
    stats["lr_duration"] = group["total_time"].max()
    stats["max_hr"] = group["max_hr"].max()
    stats["total_load"] = group["total_load"].sum()

    week_df = pd.DataFrame(stats, index=[i])
    weekly_stats = pd.concat([weekly_stats, week_df])

# Add in acute and chronic load from banister data
load_df = pd.read_csv("load.csv")
load_df["Date"] = pd.to_datetime(load_df["Date"])
load_df["week"] = load_df["Date"].dt.isocalendar().week

acute_weekly_load = []
chronic_weekly_load = []
for week, group in load_df.groupby("week"):
    acute_weekly_load.append(group["Acute Load"].mean())
    chronic_weekly_load.append(group["Chronic Load"].mean())

weekly_stats["acute_load"] = acute_weekly_load
weekly_stats["chronic_load"] = chronic_weekly_load


# Load filtered base runs
base_runs = load_runs(start_date=start_date, end_date=end_date, type="base")

dfs_list = []
for day, df in base_runs.items():
    df = add_elapsed_time(df)
    df = clean_base_runs(df)
    dfs_list.append(df)

base_df = pd.concat(dfs_list)
base_df.sort_values("timestamp", inplace=True)
base_df["week"] = base_df["timestamp"].dt.isocalendar().week

pace_info = {"week": [], "pace": []}
for week, group in base_df.groupby("week"):
    pace_info["week"].append(week)
    pace_info["pace"].append(group["pace"].mean())
pace_df = pd.DataFrame(pace_info)

weekly_stats = pd.merge(weekly_stats, pace_df, on="week", how="left")

# save data
weekly_stats.to_csv("weekly_stats.csv", index=False)
