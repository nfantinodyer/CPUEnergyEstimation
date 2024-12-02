import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

base_dir = 'Data/NewData/Linux/StressNGData/CPUEnergyEstimation/Data/Linux/StressNGData/Static'

# Define directories for each thread count
directories = {
    'All Threads': os.path.join(base_dir, 'All Threads'),
    'Two Threads': os.path.join(base_dir, 'TwoThreads'),
    'Four Threads': os.path.join(base_dir, 'FourThreads'),
    'Six Threads': os.path.join(base_dir, 'SixThreads')
}

# Mapping from word to integer for thread counts
word_to_num = {
    'Two': 2,
    'Four': 4,
    'Six': 6
}

# Define load percentages including the new 0% load
all_loads = [0] + list(range(10, 100, 10))  # 0% to 90% in increments of 10%
partial_loads = [0, 30, 60, 90]  # For 2, 4, 6 threads including 0%

# Function to create file paths
def create_file_paths(directory, loads, suffix):
    return [os.path.join(directory, f'Linux{load}{suffix}.csv') for load in loads]

# Function to load data and extract metadata
def load_data(files, num_threads):
    data_frames = []
    for file_path in files:
        if os.path.exists(file_path):
            # Read CSV, skipping the first line (#datatype)
            df = pd.read_csv(file_path, skiprows=1)
            # Convert 'DateTime' column
            df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')
            df.dropna(subset=['DateTime'], inplace=True)
            
            # Extract load percentage from filename
            filename = os.path.basename(file_path)
            load_match = re.search(r'(\d+)', filename)
            load_percent = int(load_match.group(1)) if load_match else None
            
            # Add metadata columns
            df['LoadPercent'] = load_percent
            df['NumThreads'] = num_threads
            
            data_frames.append(df)
        else:
            print(f"File not found: {file_path}")
    return data_frames

# Initialize data frames list
data_frames = []

# Iterate over each directory and load data
for label, dir_path in directories.items():
    if 'All' in label:
        files = create_file_paths(dir_path, all_loads, 'Static')
        num_threads = 'All'
    else:
        thread_word = label.split()[0]  # e.g., 'Two', 'Four', 'Six'
        threads_num = word_to_num.get(thread_word, None)
        if threads_num is None:
            print(f"Unknown thread count: {thread_word}")
            continue
        files = create_file_paths(dir_path, partial_loads, f'Static{threads_num}threads')
        num_threads = threads_num
    data_frames.extend(load_data(files, num_threads))

# Combine all data
all_data = pd.concat(data_frames, ignore_index=True)

# Print columns in all_data
print("Columns in all_data:")
print(all_data.columns.tolist())

# Define columns of interest
columnsOfInterest = [
    'DateTime', 'LoadPercent', 'NumThreads',
    'Proc Energy (Joules)', 'CPU Utilization', 'FREQ', 'AFREQ', 'TEMP', 'C0res%', 'C1res%', 'C3res%',
    'C6res%', 'C7res%', 'READ', 'WRITE'
]

# Function to get matching columns
def getMatchingColumns(columnsList, dataColumns):
    matchingColumns = {}
    for col in columnsList:
        matches = [c for c in dataColumns if c.startswith(col)]
        if matches:
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

# Print columns in all_data_filtered
print("Columns in all_data_filtered:")
print(all_data_filtered.columns.tolist())

# Data cleaning
all_data_filtered['LoadPercent'] = pd.to_numeric(all_data_filtered['LoadPercent'], errors='coerce')

# Handle 'All' threads
all_data_filtered['NumThreads'] = all_data_filtered['NumThreads'].replace({'All': None})
all_data_filtered['NumThreads'] = pd.to_numeric(all_data_filtered['NumThreads'], errors='coerce')

# Replace 'All' with the maximum number of threads observed
if all_data_filtered['NumThreads'].isnull().any():
    # Set the maximum number of threads (adjust as per your system)
    max_threads = all_data_filtered['NumThreads'].max(skipna=True)
    if pd.isnull(max_threads):
        max_threads = 8  # Replace with your actual maximum number of threads
    all_data_filtered['NumThreads'] = all_data_filtered['NumThreads'].fillna(max_threads)
else:
    max_threads = int(all_data_filtered['NumThreads'].max())

# Map 'NumThreads' to labels
num_threads_labels = {
    max_threads: 'All Threads',
    2: '2 Threads',
    4: '4 Threads',
    6: '6 Threads'
}
all_data_filtered['NumThreadsLabel'] = all_data_filtered['NumThreads'].map(num_threads_labels)

# Check for 'CPU Utilization'
if 'CPU Utilization' not in all_data_filtered.columns and 'C0res%' in all_data_filtered.columns:
    all_data_filtered['CPU Utilization'] = all_data_filtered['C0res%']
    print("Created 'CPU Utilization' from 'C0res%'")
else:
    print("'CPU Utilization' is present in data.")

# Print first few rows of all_data_filtered
print("First few rows of all_data_filtered:")
print(all_data_filtered.head())

# --- Update Analysis with Baseline Data ---

# Filter data for 'All Threads' only
all_threads_data = all_data_filtered[all_data_filtered['NumThreadsLabel'] == 'All Threads'].copy()

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
metrics_to_plot = ['FREQ', 'TEMP', 'CPU Utilization']

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
    x=all_threads_data['TEMP'],
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
high_load_data = all_threads_data[all_threads_data['LoadPercent'] >= 50]

# Check for unusual values in energy consumption
print("Energy Consumption at High Loads (All Threads):")
print(high_load_data[['LoadPercent', 'Proc Energy (Joules)']].describe())

# Check for negative or zero energy values
negative_energy = all_data_filtered[all_data_filtered['Proc Energy (Joules)'] <= 0]
if not negative_energy.empty:
    print("Found negative or zero energy values:")
    print(negative_energy[['DateTime', 'LoadPercent', 'Proc Energy (Joules)']])

# --- Data Cleaning ---

# Remove negative or zero energy values
all_data_filtered = all_data_filtered[all_data_filtered['Proc Energy (Joules)'] > 0]

# Recompute average energy consumption after cleaning
avg_energy_all_threads = all_data_filtered[all_data_filtered['NumThreadsLabel'] == 'All Threads'].groupby('LoadPercent')['Proc Energy (Joules)'].mean().reset_index()

# Re-plot average energy consumption after cleaning
plt.figure(figsize=(10, 6))
sns.lineplot(
    data=avg_energy_all_threads,
    x='LoadPercent',
    y='Proc Energy (Joules)',
    marker='o'
)
plt.title('Average Processor Energy Consumption after Cleaning (All Threads)')
plt.xlabel('Load Percentage (%)')
plt.ylabel('Average Energy (Joules)')
plt.grid(True)
plt.show()

# --- Update Regression Analysis ---

# Prepare data for regression
regression_data = all_data_filtered[['Proc Energy (Joules)', 'LoadPercent', 'NumThreads', 'FREQ', 'TEMP', 'CPU Utilization']].dropna()

# Define features and target variable
X = regression_data[['LoadPercent', 'NumThreads', 'FREQ', 'TEMP', 'CPU Utilization']]
y = regression_data['Proc Energy (Joules)']

# Fit linear regression model
model = LinearRegression()
model.fit(X, y)

# Make predictions
y_pred = model.predict(X)

# Calculate performance metrics
mse = mean_squared_error(y, y_pred)
r2 = r2_score(y, y_pred)

print(f"Mean Squared Error: {mse}")
print(f"R-squared: {r2}")

# Print model coefficients
coefficients = pd.DataFrame({'Feature': X.columns, 'Coefficient': model.coef_})
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

print("Analysis complete. Please review the plots and outputs for insights into the energy usage behavior with the new baseline data.")
