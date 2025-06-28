import pandas as pd
import joblib
import os
from flask import Blueprint, request, jsonify

# --- 1. SETUP ---
# Create a Blueprint, which is a way to organize a group of related routes.
prediction_bp = Blueprint('prediction_bp', __name__)

# Define the path to the model file.
# This path is relative to the `backend` directory where you'll run the app.
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'solar_forecaster.pkl')
print(f"Attempting to load model from: {MODEL_PATH}")

# Load the model right when the app starts.
# This is way more efficient than loading it for every request.
try:
    model = joblib.load(MODEL_PATH)
    print("✅ Model loaded successfully!")
except FileNotFoundError:
    print(f"❌ Error: Model file not found at {MODEL_PATH}. Make sure you've run the training script.")
    model = None

# This MUST be the same list of features the model was trained on.
# Order matters!
FEATURES = [
    'temperature_2m', 'precipitation', 'weather_code',
    'cloudcover_low', 'cloudcover_mid', 'cloudcover_high',
    'wind_speed_10m', 'hour', 'day_of_week', 'month', 'year'
]


# --- 2. DEFINE THE API ROUTE ---
@prediction_bp.route('/predict', methods=['POST'])
def predict():
    """
    Receives weather data in a POST request, makes a prediction,
    and returns it.
    """
    if model is None:
        return jsonify({"error": "Model is not loaded. Check server logs."}), 500

    # Get the JSON data from the request
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    print("Received JSON data:", json_data)

    try:
        # --- 3. PREPARE THE DATA FOR THE MODEL ---
        # Convert the incoming JSON into a pandas DataFrame.
        # The frontend will likely send data for a single point in time.
        input_df = pd.DataFrame(json_data, index=[0])

        # Feature Engineering: Create time-based features from the timestamp
        # The model was trained with 'hour', 'month', etc. so we MUST create them here.
        # We assume the frontend sends a 'timestamp' string like '2023-10-27T14:00:00'
        timestamp = pd.to_datetime(input_df['timestamp'])
        input_df['hour'] = timestamp.dt.hour
        input_df['day_of_week'] = timestamp.dt.dayofweek
        input_df['month'] = timestamp.dt.month
        input_df['year'] = timestamp.dt.year

        # Drop the original timestamp column as the model doesn't use it directly
        input_df = input_df.drop(columns=['timestamp'])

        # Reorder columns to match the order the model was trained on. CRITICAL STEP.
        input_df = input_df[FEATURES]

        # --- 4. MAKE THE PREDICTION ---
        prediction = model.predict(input_df)

        # The model outputs a numpy array, so we get the first (and only) element.
        output = prediction[0]
        
        # Make sure the output is a native Python float (JSON serializable)
        # Also, clamp the prediction at 0, since we can't have negative generation.
        final_prediction = max(0, float(output))

        # --- 5. RETURN THE RESPONSE ---
        return jsonify({"predicted_solar_generation_mw": final_prediction})

    except (KeyError, TypeError) as e:
        print(f"Invalid input data: {e}")
        return jsonify({"error": f"Invalid input data: {e}"}), 400