import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
from scipy.stats import ttest_ind

# Set seaborn style
sns.set_style('whitegrid')

# Define base directories for different CPUs
base_dirs = {
    'i77700K': 'Data/NewData/Linux/StressNGData',
    'i713700K': 'Data/NewData/Linux/StressNGData/i713700K'
}

# Define directories for each thread count
directories = {
    'i77700K': {
        'All Threads': os.path.join(base_dirs['i77700K'], 'Static', 'AllThreads'),
        '2 Threads': os.path.join(base_dirs['i77700K'], 'Static', 'TwoThreads'),
        '4 Threads': os.path.join(base_dirs['i77700K'], 'Static', 'FourThreads'),
        '6 Threads': os.path.join(base_dirs['i77700K'], 'Static', 'SixThreads'),
    },
    'i713700K': {
        'All Threads': os.path.join(base_dirs['i713700K'], 'Static', 'AllThreads'),
        '2 Threads': os.path.join(base_dirs['i713700K'], 'Static', 'TwoThreads'),
        '4 Threads': os.path.join(base_dirs['i713700K'], 'Static', 'FourThreads'),
        '6 Threads': os.path.join(base_dirs['i713700K'], 'Static', 'SixThreads'),
    }
}

# Define load percentages
all_loads = list(range(0, 100, 10))  # 0% to 90% in increments of 10%
partial_loads = list(range(0, 100, 10))  # Expanded to 0% to 90% in increments of 10%

# Function to create file paths
def create_file_paths(directory, loads, suffix):
    return [os.path.join(directory, f'Linux{load}{suffix}.csv') for load in loads]

# Function to load data and extract metadata
def load_data(files, num_threads_label, cpu_label):
    data_frames = []
    for file_path in files:
        if os.path.exists(file_path):
            print(f"Loading file: {file_path}")
            df = pd.read_csv(file_path, skiprows=1, header=0)
            df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')
            df.dropna(subset=['DateTime'], inplace=True)

            # Extract load percentage from filename
            filename = os.path.basename(file_path)
            load_match = re.search(r'(\d+)', filename)
            load_percent = int(load_match.group(1)) if load_match else None

            # Add metadata columns
            df['LoadPercent'] = load_percent
            df['NumThreadsLabel'] = num_threads_label
            df['CPU'] = cpu_label  # Add label for the dataset (CPU type)
            df['SourceFile'] = filename

            data_frames.append(df)
        else:
            print(f"File not found: {file_path}")
    return data_frames

# Initialize data frames list
data_frames = []

# Iterate over each directory and load data
for cpu_label, cpu_dirs in directories.items():
    for num_threads_label, dir_path in cpu_dirs.items():
        if 'All' in num_threads_label:
            files = create_file_paths(dir_path, all_loads, 'Static')
        else:
            threads_num = int(num_threads_label.split()[0])
            files = create_file_paths(dir_path, partial_loads, f'Static{threads_num}threads')
        data_frames.extend(load_data(files, num_threads_label, cpu_label))

# Combine all data
all_data = pd.concat(data_frames, ignore_index=True)

# Define columns of interest
columnsOfInterest = [
    'DateTime', 'CPU', 'LoadPercent', 'NumThreadsLabel', 'SourceFile',
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

# Filter and rename columns
all_data_filtered = all_data[list(matchingColumns.values())].copy()
all_data_filtered.columns = list(matchingColumns.keys())

# Data cleaning
# Replace zero temperatures with NaN
all_data_filtered['Temperature'] = all_data_filtered['Temperature'].replace(0, np.nan)
all_data_filtered['Temperature'] = pd.to_numeric(all_data_filtered['Temperature'], errors='coerce')
all_data_filtered['Temperature'] = all_data_filtered['Temperature'].interpolate(method='linear')
all_data_filtered.dropna(subset=['Temperature'], inplace=True)

# Map 'NumThreadsLabel' to number of threads
num_threads_mapping = {
    'All Threads': 8,
    '2 Threads': 2,
    '4 Threads': 4,
    '6 Threads': 6
}
all_data_filtered['NumThreads'] = all_data_filtered['NumThreadsLabel'].map(num_threads_mapping)

# Rename 'C0res%' to 'CPU Utilization'
if 'C0res%' in all_data_filtered.columns:
    all_data_filtered.rename(columns={'C0res%': 'CPU Utilization'}, inplace=True)

# Group data by CPU and LoadPercent
cpu_comparison = all_data_filtered.groupby(['CPU', 'LoadPercent']).agg(
    AvgEnergy=('Proc Energy (Joules)', 'mean'),
    StdEnergy=('Proc Energy (Joules)', 'std'),
    AvgUtilization=('CPU Utilization', 'mean'),
    AvgTemperature=('Temperature', 'mean')
).reset_index()

# Visualization: Energy Consumption by CPU
plt.figure(figsize=(10, 6))
sns.lineplot(data=cpu_comparison, x='LoadPercent', y='AvgEnergy', hue='CPU', marker='o')
plt.title('Energy Consumption Comparison')
plt.xlabel('Load Percentage (%)')
plt.ylabel('Average Energy (Joules)')
plt.legend(title='CPU')
plt.grid(True)
plt.show()

# Visualization: Temperature by CPU
plt.figure(figsize=(10, 6))
sns.lineplot(data=cpu_comparison, x='LoadPercent', y='AvgTemperature', hue='CPU', marker='o')
plt.title('Temperature Comparison')
plt.xlabel('Load Percentage (%)')
plt.ylabel('Average Temperature (°C)')
plt.legend(title='CPU')
plt.grid(True)
plt.show()

# Regression Analysis
regression_data = all_data_filtered[['Proc Energy (Joules)', 'LoadPercent', 'NumThreads', 'FREQ', 'Temperature', 'CPU Utilization', 'CPU']].dropna()

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

# Predictions and metrics
y_pred = model.predict(X_poly)
mse = mean_squared_error(y, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y, y_pred)
print(f"Polynomial Regression - RMSE: {rmse:.4f}")
print(f"Polynomial Regression - R-squared: {r2:.4f}")

# Actual vs Predicted
plt.scatter(y, y_pred, alpha=0.5)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
plt.title('Actual vs Predicted Energy Consumption')
plt.show()

# Residual Plot
residuals = y - y_pred
plt.scatter(y_pred, residuals, alpha=0.5)
plt.axhline(0, color='red', linestyle='--')
plt.title('Residuals')
plt.show()

# CPU-specific scatterplots
sns.scatterplot(data=regression_data, x='CPU Utilization', y='Proc Energy (Joules)', hue='CPU')
plt.title('Energy Consumption vs CPU Utilization by CPU')
plt.show()

sns.scatterplot(data=regression_data, x='FREQ', y='Proc Energy (Joules)', hue='CPU')
plt.title('Energy Consumption vs Frequency by CPU')
plt.show()

def generate_heatmap(data, title):
    correlation_data = data[['LoadPercent', 'Proc Energy (Joules)', 'FREQ', 'AFREQ', 'Temperature', 
                             'CPU Utilization', 'C1res%', 'C3res%',
                             'C6res%', 'C7res%', 'READ', 'WRITE']].corr()
    print(f"\nCorrelation Data for {title}:")
    print(correlation_data)
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_data, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title(title)
    plt.show()

# Filter data for each CPU and generate heatmaps
data_i7_7700K = all_data_filtered[all_data_filtered['CPU'] == 'i77700K']
data_i7_13700K = all_data_filtered[all_data_filtered['CPU'] == 'i713700K']

generate_heatmap(data_i7_7700K, "i7-7700K Heatmap")
generate_heatmap(data_i7_13700K, "i7-13700K Heatmap")

print("\nKey Metrics for i7-7700K:")
print(data_i7_7700K.describe())
print("\nKey Metrics for i7-13700K:")
print(data_i7_13700K.describe())


print("\nSummary of Key Metrics:")
print(all_data_filtered[['CPU', 'LoadPercent', 'Proc Energy (Joules)', 'Temperature', 'CPU Utilization']].describe())
print("\nAggregated Metrics by CPU and Load Percentage:")
print(cpu_comparison)
print("\nCorrelation Matrix of Key Metrics:")
correlation_matrix = all_data_filtered[['Proc Energy (Joules)', 'LoadPercent', 'Temperature', 'CPU Utilization']].corr()
print(correlation_matrix)
print("\nOutlier Detection - Rows with Extreme Energy Consumption:")
outliers = all_data_filtered[all_data_filtered['Proc Energy (Joules)'] > all_data_filtered['Proc Energy (Joules)'].quantile(0.99)]
print(outliers)
print("\nThread-Level Energy and Temperature Averages:")
thread_averages = all_data_filtered.groupby(['NumThreadsLabel', 'LoadPercent']).agg({
    'Proc Energy (Joules)': 'mean',
    'Temperature': 'mean',
    'CPU Utilization': 'mean'
}).reset_index()
print(thread_averages)

plt.figure(figsize=(12, 6))
sns.lineplot(data=all_data_filtered, x='LoadPercent', y='Proc Energy (Joules)', hue='NumThreadsLabel', style='CPU', marker='o')
plt.title('Energy Consumption by Thread Count')
plt.xlabel('Load Percentage (%)')
plt.ylabel('Energy Consumption (Joules)')
plt.legend(title='Thread Count and CPU')
plt.grid(True)
plt.show()

plt.figure(figsize=(12, 6))
sns.lineplot(data=all_data_filtered, x='LoadPercent', y='Temperature', hue='NumThreadsLabel', style='CPU', marker='o')
plt.title('Temperature by Thread Count')
plt.xlabel('Load Percentage (%)')
plt.ylabel('Temperature (°C)')
plt.legend(title='Thread Count and CPU')
plt.grid(True)
plt.show()

plt.figure(figsize=(12, 6))
sns.lineplot(data=all_data_filtered, x='LoadPercent', y='CPU Utilization', hue='NumThreadsLabel', style='CPU', marker='o')
plt.title('CPU Utilization by Thread Count')
plt.xlabel('Load Percentage (%)')
plt.ylabel('CPU Utilization (%)')
plt.legend(title='Thread Count and CPU')
plt.grid(True)
plt.show()
