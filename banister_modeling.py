import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

from data_handling import load_runs

run_types = ["z2", "vo2", "sprint", "threshold", "trail"]
all_runs = {}
for run_type in run_types:
    runs = load_runs(start_date="20250602", end_date="20250721", type=run_type)
    all_runs[run_type] = runs

max_hr = 196
rest_hr = 48
trimp = {}
all_dates = []

for run_type, runs_dict in all_runs.items():
    trimp[run_type] = pd.DataFrame(columns=["date", "trimp"])
    for date_str, df in runs_dict.items():
        day = datetime.strptime(date_str, "%Y%m%d")
        all_dates.append(day)
        df["time_diff"] = df["timestamp"].diff()
        df["duration"] = df["time_diff"].dt.total_seconds() / 60
        df["duration"] = df["duration"].fillna(0)
        duration_df = df.groupby("hr")["duration"].sum().reset_index()

        load = 0
        for i, row in duration_df.iterrows():
            hr_reserve = (row["hr"] - rest_hr) / (max_hr - rest_hr)
            exponent = hr_reserve * 1.67
            load += row["duration"] * hr_reserve * 0.64 * math.exp(exponent)

        trimp[run_type] = pd.concat(
            [trimp[run_type], pd.DataFrame({"date": [day], "trimp": [load]})],
            ignore_index=True,
        )

# Add in TRIMP for no run days
min_date = min(all_dates)
max_date = max(all_dates)
date_range = pd.date_range(start=min_date, end=max_date, freq="D")
no_run_dates = [date for date in date_range if date not in all_dates]
trimp["none"] = pd.DataFrame({"date": no_run_dates, "trimp": [0] * len(no_run_dates)})

# Compute performance using Banister Model
trimp_df = pd.concat(list(trimp.values()))
trimp_df = trimp_df.sort_values(by="date")


def compute_fitness_and_fatigue(fitness_tau=42, fatigue_tau=7):
    """
    Compute fitness and fatigue timeseries from TRIMP
    """
    fitness = []
    fatigue = []
    daily_trimp = trimp_df["trimp"].values.tolist()

    for t in range(len(daily_trimp)):
        fit = 0
        fat = 0
        if t > 0:
            past_trimp = daily_trimp[:t]
            for i in range(len(past_trimp)):
                fit += past_trimp[i] * math.exp(-(t - i) / fitness_tau)
                fat += past_trimp[i] * math.exp(-(t - i) / fatigue_tau)
            fitness.append(fit)
            fatigue.append(fat)

    return fitness, fatigue


def compute_performance(fitness, fatigue, initial_performance=0, k1=1.0, k2=2.0):
    fitness = np.array(fitness)
    fatigue = np.array(fatigue)
    return initial_performance + (k1 * fitness) - (k2 * fatigue)


fitness, fatigue = compute_fitness_and_fatigue()
initial_performance = 0
performance = compute_performance(fitness, fatigue)
performance = np.insert(performance, 0, initial_performance)
fitness.append(np.nan)
fatigue.append(np.nan)

fig, axes = plt.subplots(
    nrows=2, figsize=(12, 10), gridspec_kw={"height_ratios": [2, 1]}
)

ax1 = axes[0]
ax2 = ax1.twinx()

performance_line = ax1.plot(
    trimp_df["date"], performance, color="black", linewidth=2, label="Performance"
)
ax1.set_ylabel("Performance")
ax1.tick_params(axis="y", labelcolor="black")

for run_type, df in trimp.items():
    ax2.scatter(df["date"], df["trimp"], label=run_type, s=50, alpha=0.7)
ax2.set_ylabel("TRIMP", color="gray")
ax2.tick_params(axis="y", labelcolor="gray")

ax1.set_title("Performance and Training Load (TRIMP)")
ax1.grid(True, alpha=0.2)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

axes[1].plot(trimp_df["date"], fitness, color="olive", label="Fitness", linewidth=2)
axes[1].plot(trimp_df["date"], fatigue, color="gray", label="Fatigue", linewidth=2)
axes[1].set_ylabel("Fitness/Fatigue", fontsize=12)
axes[1].set_xlabel("Date", fontsize=12)
axes[1].legend()
axes[1].grid(True, alpha=0.3)
axes[1].set_title("Fitness and Fatigue Components", fontsize=14)

for ax in axes:
    ax.tick_params(axis="x", rotation=45)

plt.tight_layout()
plt.show()
