import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

# Set seaborn style
sns.set_style('whitegrid')

# Define base directory (adjust this path as needed)
base_dir = 'Data/NewData/Linux/StressNGData'

# Define directories for each thread count
directories = {
    'All Threads': os.path.join(base_dir, 'Static', 'AllThreads'),
    '2 Threads': os.path.join(base_dir, 'Static', 'TwoThreads'),
    '4 Threads': os.path.join(base_dir, 'Static', 'FourThreads'),
    '6 Threads': os.path.join(base_dir, 'Static', 'SixThreads')
}

# Define load percentages
all_loads = list(range(0, 100, 10))  # 0% to 90% in increments of 10%
partial_loads = list(range(0, 100, 10))  # Expanded to 0% to 90% in increments of 10%

# Function to create file paths
def create_file_paths(directory, loads, suffix):
    return [os.path.join(directory, f'Linux{load}{suffix}.csv') for load in loads]

# Function to load data and extract metadata
def load_data(files, num_threads_label):
    data_frames = []
    for file_path in files:
        if os.path.exists(file_path):
            print(f"Loading file: {file_path}")
            # Read CSV, skipping the first line (#datatype)
            df = pd.read_csv(file_path, skiprows=1, header=0)
            # Convert 'DateTime' column
            df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')
            df.dropna(subset=['DateTime'], inplace=True)

            # Extract load percentage from filename
            filename = os.path.basename(file_path)
            load_match = re.search(r'Linux(\d+)', filename)
            load_percent = int(load_match.group(1)) if load_match else None

            # Add metadata columns
            df['LoadPercent'] = load_percent
            df['NumThreadsLabel'] = num_threads_label
            df['SourceFile'] = filename  # Include the source file name

            data_frames.append(df)
        else:
            print(f"File not found: {file_path}")
    return data_frames

# Initialize data frames list
data_frames = []

# Iterate over each directory and load data
for num_threads_label, dir_path in directories.items():
    if 'All' in num_threads_label:
        files = create_file_paths(dir_path, all_loads, 'Static')
    else:
        # Extract number of threads from label
        threads_num = int(num_threads_label.split()[0])
        files = create_file_paths(dir_path, partial_loads, f'Static{threads_num}threads')
    data_frames.extend(load_data(files, num_threads_label))

# Combine all data
all_data = pd.concat(data_frames, ignore_index=True)

# Print unique NumThreadsLabel values
print("Unique NumThreadsLabel values in all_data:")
print(all_data['NumThreadsLabel'].unique())

# Print columns in all_data
print("Columns in all_data:")
print(all_data.columns.tolist())

# Define columns of interest
columnsOfInterest = [
    'DateTime', 'LoadPercent', 'NumThreadsLabel', 'SourceFile',
    'Proc Energy (Joules)', 'FREQ', 'AFREQ', 'Temperature', 'C0res%', 'C1res%', 'C3res%',
    'C6res%', 'C7res%', 'READ', 'WRITE'
]

# Function to get matching columns
def getMatchingColumns(columnsList, dataColumns):
    matchingColumns = {}
    for col in columnsList:
        matches = [c for c in dataColumns if c.startswith(col)]
        if matches:
            # For 'TEMP', pick the exact match or the first match
            if col == 'Temperature':
                temp_matches = [c for c in matches if c == 'Temperature']
                matchingColumns[col] = temp_matches[0] if temp_matches else matches[0]
            else:
                matchingColumns[col] = matches[0]
        else:
            print(f"Column '{col}' not found in data.")
    return matchingColumns

# Get matching columns
matchingColumns = getMatchingColumns(columnsOfInterest, all_data.columns)

# Print matching columns
print("Matching Columns:")
print(matchingColumns)

# Filter and rename columns
all_data_filtered = all_data[list(matchingColumns.values())].copy()
all_data_filtered.columns = list(matchingColumns.keys())

# Data cleaning
# Replace zero temperatures with NaN
all_data_filtered.loc[:, 'Temperature'] = all_data_filtered['Temperature'].replace(0, np.nan)
all_data_filtered['Temperature'] = pd.to_numeric(all_data_filtered['Temperature'], errors='coerce')

# Interpolate missing temperature values if appropriate
all_data_filtered.loc[:, 'Temperature'] = all_data_filtered['Temperature'].interpolate(method='linear')

# Drop rows with remaining missing values
all_data_filtered.dropna(subset=['Temperature'], inplace=True)

# Convert 'LoadPercent' to numeric
all_data_filtered['LoadPercent'] = pd.to_numeric(all_data_filtered['LoadPercent'], errors='coerce')
all_data_filtered.loc[:, 'LoadPercent'] = all_data_filtered['LoadPercent'].fillna(0)

# Map 'NumThreadsLabel' to number of threads
num_threads_mapping = {
    'All Threads': 8,  # Adjust to match the system's max threads
    '2 Threads': 2,
    '4 Threads': 4,
    '6 Threads': 6
}
all_data_filtered['NumThreads'] = all_data_filtered['NumThreadsLabel'].map(num_threads_mapping)

# Rename 'C0res%' to 'CPU Utilization' directly
if 'C0res%' in all_data_filtered.columns:
    all_data_filtered.rename(columns={'C0res%': 'CPU Utilization'}, inplace=True)
    print("Renamed 'C0res%' to 'CPU Utilization'")
else:
    print("'C0res%' column is missing from the data.")

# Print first few rows of all_data_filtered
print("First few rows of all_data_filtered:")
print(all_data_filtered.head())

# --- Proceed with Analysis ---

# Filter data for 'All Threads' only
all_threads_data = all_data_filtered[all_data_filtered['NumThreadsLabel'] == 'All Threads'].copy()

# Check if 'all_threads_data' is not empty
if all_threads_data.empty:
    print("No data found for 'All Threads'")
else:
    # Compute average processor energy consumption for 'All Threads'
    avg_energy_all_threads = all_threads_data.groupby('LoadPercent')['Proc Energy (Joules)'].mean().reset_index()

    # Plotting average energy consumption for 'All Threads' including baseline
    plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=avg_energy_all_threads,
        x='LoadPercent',
        y='Proc Energy (Joules)',
        marker='o'
    )
    plt.title('Average Processor Energy Consumption (All Threads)')
    plt.xlabel('Load Percentage (%)')
    plt.ylabel('Average Energy (Joules)')
    plt.grid(True)
    plt.show()

    # Print the average energy values
    print("Average Energy Consumption for All Threads:")
    print(avg_energy_all_threads)

    # --- Investigate Anomalies ---

    # Plot additional metrics to check for anomalies
    metrics_to_plot = ['FREQ', 'Temperature', 'CPU Utilization']

    for metric in metrics_to_plot:
        plt.figure(figsize=(10, 6))
        sns.lineplot(
            data=all_threads_data,
            x='LoadPercent',
            y=metric,
            estimator='mean',
            errorbar=None,
            marker='o'
        )
        plt.title(f'Average {metric} (All Threads)')
        plt.xlabel('Load Percentage (%)')
        plt.ylabel(f'Average {metric}')
        plt.grid(True)
        plt.show()

    # Check for thermal throttling by plotting CPU frequency and temperature
    plt.figure(figsize=(10, 6))
    sc = plt.scatter(
        x=all_threads_data['Temperature'],
        y=all_threads_data['FREQ'],
        c=all_threads_data['LoadPercent'],
        cmap='viridis'
    )
    plt.title('CPU Frequency vs. Temperature (All Threads)')
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Frequency (GHz)')
    plt.colorbar(sc, label='Load Percentage (%)')
    plt.grid(True)
    plt.show()

    # --- Data Diagnostics ---

    # Identify potential data issues at higher loads
    high_load_data = all_threads_data[all_threads_data['LoadPercent'] >= 70]

    # Check for unusual values in temperature
    print("Temperature Data at High Loads (All Threads):")
    print(high_load_data[['LoadPercent', 'Temperature']].describe())

    # --- Update Regression Analysis ---

    # Prepare data for regression
    regression_data = all_data_filtered[['Proc Energy (Joules)', 'LoadPercent', 'NumThreads', 'FREQ', 'Temperature', 'CPU Utilization']].dropna()

    # Define features and target variable
    X = regression_data[['LoadPercent', 'NumThreads', 'FREQ', 'Temperature', 'CPU Utilization']]
    y = regression_data['Proc Energy (Joules)']

    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Fit polynomial regression model
    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_poly = poly.fit_transform(X_scaled)

    model = LinearRegression()
    model.fit(X_poly, y)

    # Make predictions
    y_pred = model.predict(X_poly)

    # Calculate performance metrics
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y, y_pred)

    print(f"Polynomial Regression - RMSE: {rmse:.4f}")
    print(f"Polynomial Regression - R-squared: {r2:.4f}")

    # Print model coefficients
    feature_names = poly.get_feature_names_out(X.columns)
    coefficients = pd.DataFrame({
        'Feature': feature_names,
        'Coefficient': model.coef_
    })
    print("\nModel Coefficients:")
    print(f"Intercept: {model.intercept_}")
    print(coefficients)

    # Plot Actual vs Predicted Energy Consumption
    plt.figure(figsize=(10, 6))
    plt.scatter(y, y_pred, alpha=0.5)
    plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
    plt.xlabel('Actual Energy Consumption (Joules)')
    plt.ylabel('Predicted Energy Consumption (Joules)')
    plt.title('Actual vs Predicted Energy Consumption')
    plt.grid(True)
    plt.show()

    # Residual Plot
    residuals = y - y_pred
    plt.figure(figsize=(10, 6))
    plt.scatter(y_pred, residuals, alpha=0.5)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('Predicted Energy Consumption (Joules)')
    plt.ylabel('Residuals')
    plt.title('Residual Plot')
    plt.grid(True)
    plt.show()

    # --- Additional Visualizations ---

    # Plot energy consumption vs. CPU Utilization
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=all_data_filtered,
        x='CPU Utilization',
        y='Proc Energy (Joules)',
        hue='LoadPercent',
        palette='viridis'
    )
    plt.title('Processor Energy Consumption vs. CPU Utilization')
    plt.xlabel('CPU Utilization (%)')
    plt.ylabel('Energy Consumption (Joules)')
    plt.grid(True)
    plt.show()

    # Plot energy consumption vs. Frequency
    plt.figure(figsize=(10, 6))
    sns.scatterplot(
        data=all_data_filtered,
        x='FREQ',
        y='Proc Energy (Joules)',
        hue='LoadPercent',
        palette='viridis'
    )
    plt.title('Processor Energy Consumption vs. Frequency')
    plt.xlabel('Frequency (GHz)')
    plt.ylabel('Energy Consumption (Joules)')
    plt.grid(True)
    plt.show()

    # --- Conclusion ---

    print("Analysis complete. Please review the plots and outputs for insights into the energy usage behavior with the temperature data.")
