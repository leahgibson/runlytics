import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.model_selection import LeaveOneOut, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

df = pd.read_csv("weekly_stats.csv")

feature_names = [
    "total_distance",
    "z2_time",
    # "z3_time",
    # "z4_time",
    # "z5_time",
    "total_time",
    "total_elevation_gain",
    # "max_altitude",
    # "time_above_6000",
    # "time_above_10000",
    "lr_duration",
    # "max_hr",
    # "total_load",
    "acute_load",
    "chronic_load",
]

colors = ["red", "orange", "green", "pink", "blue", "black", "violet"]
# Visualize the input variables
fig, axes = plt.subplots(nrows=len(feature_names) + 1, sharex=True, figsize=(7, 10))
for i, feature in enumerate(feature_names):
    axes[i].plot(df[feature], marker="o", color=colors[i])
    axes[i].set_ylabel(feature, color=colors[i])
axes[i + 1].plot(df["pace"], marker="o", color="gray")
axes[i + 1].set_ylabel("z2_pace", color="gray")
axes[i + 1].set_xlabel("Training Week")
plt.tight_layout()
plt.savefig("input_ts.png", dpi=300)


# Prepare data for training
X = df[feature_names].values
y = df["pace"].values


scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
loo = LeaveOneOut()

fig, axes = plt.subplots(ncols=3, nrows=2, figsize=(7, 6))
axes = axes.flatten()

for i, alpha in enumerate([0, 0.01, 0.1, 1.0, 10, 100]):
    y_preds = []
    y_actuals = []
    shap_values = []
    test_indices = []

    for train_idx, test_idx in loo.split(X_scaled):
        X_train, X_test = X_scaled[train_idx], X_scaled[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        model = Ridge(alpha=alpha)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # print(model.coef_)

        y_preds.append(y_pred[0])
        y_actuals.append(y_test[0])
        test_indices.append(test_idx[0])

        # explainer = shap.LinearExplainer(model, X_train)
        # shap_vals = explainer.shap_values(X_test)
        # shap_values.append(shap_vals[0])

    mse = mean_squared_error(y_actuals, y_preds)
    r2 = r2_score(y_actuals, y_preds)

    ax = axes[i]

    # Plot predicted vs actual
    ax.scatter(y_actuals, y_preds)
    ax.plot([min(y_actuals), max(y_actuals)], [min(y_actuals), max(y_actuals)], "r--")
    ax.set_xlabel("Actual pace")
    ax.set_ylabel("Predicted pace")
    ax.set_title(f"$\lambda$ = {alpha}, R$^2$ = {r2:.2f}")

plt.tight_layout()
plt.savefig("lambda_test.png", dpi=300)


# Find the best alpha
ridge = Ridge()
param_grid = {"alpha": np.logspace(-2, 2, 50)}
grid = GridSearchCV(ridge, param_grid, cv=loo, scoring="neg_mean_squared_error")
grid.fit(X_scaled, y)

best_alpha = grid.best_params_["alpha"]

print("Best alpha:", best_alpha)

# Train model with best alpha on all data
final_model = Ridge(alpha=best_alpha)
final_model.fit(X_scaled, y)

y_pred = final_model.predict(X_scaled)

print("Intercept:", final_model.intercept_)
print("Coefficients:", final_model.coef_)


### Predict future week ###
future_week = pd.DataFrame(
    [
        {
            "total_distance": 39,
            "z2_time": 300,
            "total_time": 470,
            "total_elevation_gain": 5000,
            "lr_duration": 265,
            "acute_load": 520,
            "chronic_load": 2600,
        }
    ]
)

future_week_scaled = scaler.transform(future_week[feature_names])
future_pred = final_model.predict(future_week_scaled)
y_pred = np.append(y_pred, future_pred[0])

plt.figure(figsize=(7, 3))
plt.plot(y, label="Actual Z2 Pace")
plt.plot(y_pred, label="Predicted Z2 Pace")
plt.xlabel("Training Week")
plt.ylabel("Pace (min/mi)")
plt.legend()
plt.tight_layout()
plt.savefig("z2_prediction.png", dpi=300)
