"""
Analysis of zone 2/base runs.
"""

from data_handling import load_runs, add_elapsed_time, clean_base_runs
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


# Pre heat exposure
baseline_runs = load_runs(start_date="2025051", end_date="20250515", type="base")

baseline = []
for df in baseline_runs.values():
    df = add_elapsed_time(df)
    df = clean_base_runs(df)

    baseline.append(df)

baseline_df = pd.concat(baseline)
baseline_df = baseline_df.sort_values(by="timestamp")

# Pre injury
winter_peak_runs = load_runs(start_date="20250202", end_date="20250208", type="base")

winter_peak = []
for df in winter_peak_runs.values():
    df = add_elapsed_time(df)
    df = clean_base_runs(df)

    winter_peak.append(df)

winter_peak_df = pd.concat(winter_peak)
winter_peal_df = winter_peak_df.sort_values(by="timestamp")

# With heat exposure
base_runs = load_runs(
    start_date="20250602", end_date="20250720", type="base"
)  # end_date="20250629"

all_runs = []
for date_str, df in base_runs.items():
    df = add_elapsed_time(df)
    df = clean_base_runs(df)

    all_runs.append(df.copy())

runs_df = pd.concat(all_runs)
runs_df = runs_df.sort_values(by="timestamp")

### Aerobic Efficiency ###

# Group data by week (Monday=0)
runs_df["week"] = runs_df["timestamp"].dt.isocalendar().week
weekly_ae = []
weekly_ae.append(winter_peak_df["pace"].mean() / winter_peak_df["hr"].mean())
weekly_ae.append(baseline_df["pace"].mean() / baseline_df["hr"].mean())

colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
fig, axes = plt.subplots(ncols=7, sharey=True, figsize=(16, 4), dpi=300)

all_handles = []
all_labels = []

for i, (week, group) in enumerate(runs_df.groupby("week")):
    weekly_ae.append(group["pace"].mean() / group["hr"].mean())

    h1 = axes[i].scatter(
        winter_peak_df["hr"],
        winter_peak_df["pace"],
        label="Winter Peak (no heat)",
        color="gray",
        marker="s",
        alpha=0.7,
    )
    h2 = axes[i].scatter(
        baseline_df["hr"],
        baseline_df["pace"],
        label="Baseline (no heat)",
        color="lightgray",
        marker="^",
        alpha=0.7,
    )
    axes[i].set_title(f"Week {i + 1}")
    h3 = axes[i].scatter(
        group["hr"],
        group["pace"],
        label=f"Week {i + 1} (w/ heat)",
        color=colors[i],
        alpha=0.7,
    )

    if i == 0:
        all_handles.extend([h1, h2])
        all_labels.extend(["Winter Peak", "Baseline"])

    all_handles.append(h3)
    all_labels.append(f"Week {i + 1} (w/ heat)")

    axes[i].set_xlim(115, 175)
    axes[i].set_ylim(8, 11.5)

axes[0].set_ylabel("Pace (min/mi)")
axes[3].set_xlabel("Heart Rate (bpm)")

plt.figlegend(
    all_handles,
    all_labels,
    loc="lower center",
    ncol=len(all_labels),
    bbox_to_anchor=(0.5, 0.01),
)
plt.tight_layout()
plt.subplots_adjust(bottom=0.2)
plt.savefig("ae_scatter.png")
exit()
plt.show()

# Plot weekly avg
weeks = [
    datetime(2025, 2, 2),
    datetime(2025, 5, 11),
    datetime(2025, 6, 2),
    datetime(2025, 6, 9),
    datetime(2025, 6, 16),
    datetime(2025, 6, 23),
    datetime(2025, 6, 30),
    datetime(2025, 7, 7),
    datetime(2025, 7, 14),
]

fig, ax1 = plt.subplots(figsize=(6, 3))
ax1.scatter(
    datetime(2025, 2, 2),
    winter_peak_df["pace"].mean() / winter_peak_df["hr"].mean(),
    color="gray",
    marker="s",
    label="Winter Peak (before heat)",
)
ax1.scatter(
    datetime(2025, 5, 11),
    baseline_df["pace"].mean() / baseline_df["hr"].mean(),
    color="lightgray",
    marker="^",
    label="Baseline (before heat)",
)
ax1.scatter(weeks[2:], weekly_ae[2:], color="coral", label="Training (with heat)")
ax1.set_ylabel("AE (pace/HR)")

plt.title("Aerobic Efficiency")
plt.legend(loc="lower left")
plt.show()
