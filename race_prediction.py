"""
Code to repdict race time
"""

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor


df = pd.read_csv("./model_data/mile_data.csv")
race_df = pd.read_csv("./model_data/race.csv")

# Plot relationships
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.5))

# First subplot - Altitude colored
vmin_alt = df["altitude"].min()
vmax_alt = df["altitude"].max()

# Plot road points on first subplot
road_mask = df["surface"] == "road"
scatter1_alt = ax1.scatter(
    df[road_mask]["net_elevation"],
    df[road_mask]["pace"],
    c=df[road_mask]["altitude"],
    cmap="terrain",
    marker="o",
    label="Road",
    alpha=0.9,
    vmin=vmin_alt,
    vmax=vmax_alt,
)

# Plot trail points on first subplot
trail_mask = df["surface"] == "trail"
scatter2_alt = ax1.scatter(
    df[trail_mask]["net_elevation"],
    df[trail_mask]["pace"],
    c=df[trail_mask]["altitude"],
    cmap="terrain",
    marker="^",
    label="Trail",
    alpha=0.9,
    vmin=vmin_alt,
    vmax=vmax_alt,
)

# First subplot formatting
plt.colorbar(scatter1_alt, ax=ax1, label="Altitude (ft)")
ax1.set_xlabel("Net Elevation Gain (ft)")
ax1.set_ylabel("Pace (min/mi)")
ax1.legend()
ax1.set_title("Pace vs Net Elevation (Colored by Altitude)")

# Second subplot - Heart Rate colored
vmin_hr = df["hr"].min()
vmax_hr = df["hr"].max()

# Plot road points on second subplot
scatter1_hr = ax2.scatter(
    df[road_mask]["net_elevation"],
    df[road_mask]["pace"],
    c=df[road_mask]["hr"],
    cmap="turbo",
    marker="o",
    label="Road",
    alpha=0.9,
    vmin=vmin_hr,
    vmax=vmax_hr,
)

# Plot trail points on second subplot
scatter2_hr = ax2.scatter(
    df[trail_mask]["net_elevation"],
    df[trail_mask]["pace"],
    c=df[trail_mask]["hr"],
    cmap="turbo",
    marker="^",
    label="Trail",
    alpha=0.9,
    vmin=vmin_hr,
    vmax=vmax_hr,
)

# Second subplot formatting
plt.colorbar(scatter1_hr, ax=ax2, label="Heart Rate (bpm)")
ax2.set_xlabel("Net Elevation Gain (ft)")
ax2.set_ylabel("Pace (min/mi)")
ax2.legend()
ax2.set_title("Pace vs Net Elevation (Colored by Heart Rate)")

plt.tight_layout()
plt.savefig("race_relationships.png", dpi=300)
plt.show()


### Predict using basic linear regression with net_elevation and altitude ###
X = df[["net_elevation", "altitude", "hr"]]
y = df["pace"]

model = LinearRegression()
model.fit(X, y)

# Use race data to predict
X_race = race_df[["net_elevation", "altitude", "hr"]]
y_pred = model.predict(X_race)

print("##### Linear Regression Model #####")
print(f"paces: {y_pred}")
print(f"Total time prediction: {sum(y_pred)} min")

### Predict using neural net ###

features = ["net_elevation", "altitude", "hr"]

X = df[features].values 
y = df["pace"].values

# scale inputs
scaler = StandardScaler()
X = scaler.fit_transform(X)

mlp = MLPRegressor(
    hidden_layer_sizes=(32, 16),
    activation="relu",
    solver="adam",
    max_iter=1000,
    random_state=42,
)

mlp.fit(X, y)

# Predict race

X_race = race_df[features].values
X_race = scaler.transform(X_race)

nn_y_pred = mlp.predict(X_race)
print("##### Neural Network #####")
print(f"paces: {nn_y_pred}")
print(f"Total time prediction: {sum(nn_y_pred)} min")

fig, ax1 = plt.subplots(figsize=(7, 4))

ax1.plot(race_df["mile"], y_pred, color="blue", label="Linear Regression")
ax1.plot(race_df["mile"], nn_y_pred, color="green", label="Neural Network")
ax1.legend()
ax1.set_xlabel("Miles")
ax1.set_ylabel("Pace (min/mi)")

ax2 = ax1.twinx()

ax2.fill_between(
    race_df["mile"],
    race_df["altitude"].min(),
    race_df["altitude"],
    alpha=0.3,
    color="gray",
    label="Altitude",
)
ax2.set_ylabel("Altitude (ft)", color="gray")
ax2.tick_params(axis="y", labelcolor="gray")

plt.tight_layout()
plt.savefig("race_predictions.png", dpi=300)
plt.show()
