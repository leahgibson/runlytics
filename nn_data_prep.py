"""
Combine running data for race prediction NN
"""

import numpy as np
import pandas as pd

from data_handling import load_runs


start_date = "20250803"
end_date = "20250914"

run_types = ["base", "trail"]
surface_lookup = {"base": "road", "trail": "trail"}

all_runs = {}
for run_type in run_types:
    runs = load_runs(start_date=start_date, end_date=end_date, type=run_type)
    # add classification to each run
    for run_df in runs.values():
        run_df["surface"] = surface_lookup[run_type]
    all_runs.update(runs)


rows = []
for run_date, df in all_runs.items():
    df["mile_group"] = np.floor(df["distance"]).astype(int)
    total_miles = df["mile_group"].max() + 1
    surface = df["surface"][0]
    grouper = df.groupby("mile_group")

    for group, mile_df in grouper:
        if len(mile_df) < 30:  # incomplete mile
            continue
        avg_pace = mile_df["pace"].mean()
        avg_hr = mile_df["hr"].mean()
        avg_elevation = mile_df["elevation"].mean()
        elevation_diff = mile_df["elevation"].diff()
        elevation_gain = elevation_diff[elevation_diff > 0].sum()
        elevation_loss = -elevation_diff[elevation_diff < 0].sum()
        net_elevation = elevation_gain - elevation_loss
        mile = group + 1

        rows.append(
            {
                "pace": round(avg_pace, 3),
                "hr": round(avg_hr),
                "altitude": round(avg_elevation),
                # "elevation_gain": elevation_gain,
                # "elevation_loss": elevation_loss,
                "net_elevation": round(net_elevation),
                "mile": mile,
                "total_miles": total_miles,
                "surface": surface,
            }
        )

final_df = pd.DataFrame(rows)
final_df.to_csv("./model_data/mile_data.csv", index=False)
