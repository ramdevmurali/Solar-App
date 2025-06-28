import pandas as pd
import xgboost as xgb
import joblib # For saving the model
import os
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

print("--- Starting Model Training Script ---")

# --- 1. LOAD DATA ---
# Fix paths to work from backend/scripts directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))  # Go up to solar-forecast-app
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed', 'merged_solar_weather_data.csv')
MODEL_PATH = os.path.join(PROJECT_ROOT, 'backend', 'app', 'models')
MODEL_NAME = 'solar_forecaster.pkl'

# Check if the processed data file exists
if not os.path.exists(PROCESSED_DATA_PATH):
    print(f"ERROR: Processed data file not found at {PROCESSED_DATA_PATH}")
    print("Please run the data merging script first (01_merge_and_clean_data.py)")
    exit(1)

df = pd.read_csv(PROCESSED_DATA_PATH, index_col='timestamp', parse_dates=True)

# Create the models directory if it doesn't exist
os.makedirs(MODEL_PATH, exist_ok=True)

print(f"  - Loaded data with shape: {df.shape}")
print(f"  - Data time range: {df.index.min()} to {df.index.max()}")


# --- 2. FEATURE ENGINEERING ---
# The model needs numerical features that capture the time of day, year, etc.
print("Step 2: Engineering features...")
df['hour'] = df.index.hour
df['day_of_week'] = df.index.dayofweek
df['month'] = df.index.month
df['year'] = df.index.year
df['day_of_year'] = df.index.dayofyear

print("  - Features created: hour, day_of_week, month, year, day_of_year")


# --- 3. DEFINE FEATURES (X) AND TARGET (y) ---
# The target is what we want to predict.
TARGET = 'solar_generation_mw'

# The features are all the columns we'll use to make the prediction.
# Updated to match the actual column names from the processed data
FEATURES = [
    'temperature_2m', 'precipitation', 'weather_code',
    'cloudcover_low', 'cloudcover_mid', 'cloudcover_high',
    'wind_speed_10m', 'hour', 'day_of_week', 'month', 'year'
]

# Ensure all feature columns exist in the DataFrame
available_features = [f for f in FEATURES if f in df.columns]
missing_features = [f for f in FEATURES if f not in df.columns]

if missing_features:
    print(f"  - WARNING: Missing features: {missing_features}")
    print(f"  - Using available features: {available_features}")

FEATURES = available_features

# Check if we have enough features
if len(FEATURES) < 3:
    print("ERROR: Not enough features available for training")
    exit(1)

X = df[FEATURES]
y = df[TARGET]

print(f"  - Using {len(FEATURES)} features: {FEATURES}")

# Check for missing values
print(f"  - Missing values in features: {X.isnull().sum().sum()}")
print(f"  - Missing values in target: {y.isnull().sum()}")

# Handle any remaining missing values
X = X.ffill().bfill().fillna(0)
y = y.fillna(0)

# --- 4. SPLIT DATA (TIME-SERIES SPLIT) ---
# For time-series, we MUST NOT shuffle. We train on the past and test on the future.
print("Step 4: Splitting data into training and testing sets...")

# Use 80% of data for training, 20% for testing
split_idx = int(len(df) * 0.8)
split_date = df.index[split_idx]

X_train = X.loc[X.index < split_date]
y_train = y.loc[y.index < split_date]
X_test = X.loc[X.index >= split_date]
y_test = y.loc[y.index >= split_date]

print(f"  - Training data from {X_train.index.min()} to {X_train.index.max()} ({len(X_train)} samples)")
print(f"  - Testing data from {X_test.index.min()} to {X_test.index.max()} ({len(X_test)} samples)")

# Check if we have enough data
if len(X_train) < 100 or len(X_test) < 20:
    print("ERROR: Not enough data for training/testing")
    exit(1)


# --- 5. TRAIN THE XGBOOST MODEL ---
# XGBoost is a powerful gradient boosting algorithm. It's a great choice for this.
print("Step 5: Training XGBoost Regressor model...")
reg = xgb.XGBRegressor(
    n_estimators=500,       # Reduced from 1000 for faster training
    learning_rate=0.1,      # Increased from 0.05 for faster convergence
    max_depth=6,            # Slightly increased
    subsample=0.8,
    colsample_bytree=0.8,
    objective='reg:squarederror',
    n_jobs=-1,              # Use all available CPU cores
    early_stopping_rounds=50, # Stop training if performance doesn't improve
    random_state=42         # For reproducibility
)

# The `eval_set` allows us to monitor performance on the test set and use early stopping.
reg.fit(X_train, y_train,
        eval_set=[(X_train, y_train), (X_test, y_test)],
        verbose=50) # Print progress every 50 trees

print("  - Model training complete.")


# --- 6. EVALUATE THE MODEL ---
print("Step 6: Evaluating model performance...")

# Make predictions
y_train_pred = reg.predict(X_train)
y_test_pred = reg.predict(X_test)

# Calculate metrics
train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
train_mae = mean_absolute_error(y_train, y_train_pred)
test_mae = mean_absolute_error(y_test, y_test_pred)
train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)

print(f"  - Training RMSE: {train_rmse:.2f}")
print(f"  - Testing RMSE: {test_rmse:.2f}")
print(f"  - Training MAE: {train_mae:.2f}")
print(f"  - Testing MAE: {test_mae:.2f}")
print(f"  - Training R²: {train_r2:.3f}")
print(f"  - Testing R²: {test_r2:.3f}")


# --- 7. SAVE THE MODEL ---
# We save the trained model so our API can load and use it for predictions.
print("Step 7: Saving model...")
model_filepath = os.path.join(MODEL_PATH, MODEL_NAME)
joblib.dump(reg, model_filepath)

print(f"--- Model saved successfully to: {model_filepath} ---")

# --- 8. FEATURE IMPORTANCE ---
# Let's see what the model thought was most important.
print("\n--- Feature Importance ---")
importance = pd.DataFrame(data=reg.feature_importances_,
                          index=reg.feature_names_in_,
                          columns=['importance'])
importance_sorted = importance.sort_values('importance', ascending=False)
print(importance_sorted)

# Save feature importance to a file for reference
importance_filepath = os.path.join(MODEL_PATH, 'feature_importance.csv')
importance_sorted.to_csv(importance_filepath)
print(f"  - Feature importance saved to: {importance_filepath}")

print("\n--- Model Training Complete ---")