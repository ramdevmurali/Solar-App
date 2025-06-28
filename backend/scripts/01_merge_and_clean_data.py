import pandas as pd
import os

print("--- Starting Data Merging and Cleaning Script ---")

# --- 1. DEFINE FILE PATHS ---
# This makes the script reusable and easy to understand.
# It assumes you are running the script from the `solar-forecast-app/backend/` directory.
RAW_DATA_PATH = '../data/raw/'
PROCESSED_DATA_PATH = '../data/processed/'
SOLAR_FILES = [
    'PV Live Historical Results _23.csv', 
    'PV Live Historical Results _24.csv',
    'PV Live Historical Results_25.csv'
]
WEATHER_FILE = 'Historical Weather Data 52.48N 1.67E.csv'
OUTPUT_FILE = 'merged_solar_weather_data.csv'

# Create the processed data directory if it doesn't exist
os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)


# --- 2. LOAD AND COMBINE SOLAR DATA ---
print("Step 2: Loading and combining solar generation data...")

solar_df_list = []
for file in SOLAR_FILES:
    try:
        # Solar data has clean structure, no need to skip rows
        df = pd.read_csv(os.path.join(RAW_DATA_PATH, file))
        solar_df_list.append(df)
        print(f"  - Successfully loaded {file}")
    except FileNotFoundError:
        print(f"  - ERROR: {file} not found in {RAW_DATA_PATH}. Skipping.")
        continue

# Concatenate all solar dataframes into a single one
solar_df = pd.concat(solar_df_list, ignore_index=True)

# --- 3. CLEAN AND PREPROCESS SOLAR DATA ---
print("\nStep 3: Cleaning solar data...")

# Rename columns for clarity. Using actual column names from the data.
solar_df.rename(columns={'datetime_gmt': 'timestamp', 'generation_mw': 'solar_generation_mw'}, inplace=True)

# Convert the timestamp column to datetime objects
solar_df['timestamp'] = pd.to_datetime(solar_df['timestamp'], utc=True)

# Set the timestamp as the index. This is CRUCIAL for time-series analysis.
solar_df.set_index('timestamp', inplace=True)

# Drop unnecessary columns (keep only solar generation)
solar_df = solar_df[['solar_generation_mw']]

# Handle duplicates that might arise from overlapping files
solar_df = solar_df[~solar_df.index.duplicated(keep='first')]

# Sort by the index to ensure chronological order
solar_df.sort_index(inplace=True)

print("  - Solar data cleaned. Shape:", solar_df.shape)
print("  - Solar data time range:", solar_df.index.min(), "to", solar_df.index.max())


# --- 4. LOAD AND PREPROCESS WEATHER DATA ---
print("\nStep 4: Loading and cleaning weather data...")

try:
    # Weather data has metadata at the top (2 lines), so we need to skip them
    weather_df = pd.read_csv(os.path.join(RAW_DATA_PATH, WEATHER_FILE), skiprows=2)

    # Rename columns to match the actual data structure
    weather_df.rename(columns={'time': 'timestamp'}, inplace=True)

    # Convert timestamp to datetime objects. Weather data doesn't have timezone info, so we'll assume UTC
    weather_df['timestamp'] = pd.to_datetime(weather_df['timestamp'], utc=True)

    # Set timestamp as the index
    weather_df.set_index('timestamp', inplace=True)
    
    # Sort by the index
    weather_df.sort_index(inplace=True)

    print("  - Weather data cleaned. Shape:", weather_df.shape)
    print("  - Weather data time range:", weather_df.index.min(), "to", weather_df.index.max())

except FileNotFoundError:
    print(f"  - ERROR: {WEATHER_FILE} not found. Cannot proceed with merge.")
    exit() # Exit the script if weather data is missing


# --- 5. MERGE THE DATASETS ---
print("\nStep 5: Merging solar and weather data...")

# We'll use an 'inner' merge. This keeps only the timestamps that exist in BOTH dataframes.
# This is usually what you want to avoid having missing values for your features or target.
merged_df = pd.merge(solar_df, weather_df, left_index=True, right_index=True, how='inner')

print("  - Merging complete. Final dataset shape:", merged_df.shape)


# --- 6. HANDLE MISSING VALUES ---
# After merging, you might still have missing values in some columns.
# A simple strategy is forward-fill (ffill) or interpolation.
print("\nStep 6: Handling missing values...")
print("  - Missing values before handling:\n", merged_df.isnull().sum())

# We can interpolate for weather data, as it changes gradually.
weather_columns = [col for col in weather_df.columns if col in merged_df.columns]
merged_df[weather_columns] = merged_df[weather_columns].interpolate(method='time')

# For solar generation, 0 is a valid value (e.g., at night). 
# Filling with 0 might be a safe bet if there are still NaNs.
merged_df = merged_df.fillna({'solar_generation_mw': 0})

print("\n  - Missing values after handling:\n", merged_df.isnull().sum())


# --- 7. SAVE THE PROCESSED DATA ---
print("\nStep 7: Saving the final processed file...")

output_path = os.path.join(PROCESSED_DATA_PATH, OUTPUT_FILE)
merged_df.to_csv(output_path)

print(f"--- Successfully created merged dataset at: {output_path} ---")