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

#Suppress SettingWithCopyWarning
pd.options.mode.chained_assignment = None

sns.set_style('whitegrid')

base_dirs = {
    'i77700K': 'Data/NewData/Linux/StressNGData',
    'i713700K': 'Data/NewData/Linux/StressNGData/i713700K'
}

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

all_loads = list(range(0, 100, 10))
partial_loads = list(range(0, 100, 10))

def create_file_paths(directory, loads, suffix):
    return [os.path.join(directory, f'Linux{load}{suffix}.csv') for load in loads]

def load_data(files, num_threads_label, cpu_label):
    data_frames = []
    for file_path in files:
        if os.path.exists(file_path):
            print(f"Loading file: {file_path}")
            df = pd.read_csv(file_path, skiprows=1, header=0)
            df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')
            df.dropna(subset=['DateTime'], inplace=True)

            filename = os.path.basename(file_path)
            load_match = re.search(r'(\d+)', filename)
            load_percent = int(load_match.group(1)) if load_match else None

            df['LoadPercent'] = load_percent
            df['NumThreadsLabel'] = num_threads_label
            df['CPU'] = cpu_label
            df['SourceFile'] = filename

            data_frames.append(df)
        else:
            print(f"File not found: {file_path}")
    return data_frames

# Function to perform t-tests
def perform_t_tests(data, metric, thread_comparisons, cpu_label):
    results = []
    cpu_data = data[data['CPU'] == cpu_label]
    for group1, group2 in thread_comparisons:
        data1 = cpu_data[cpu_data['NumThreads'] == group1][metric]
        data2 = cpu_data[cpu_data['NumThreads'] == group2][metric]
        
        if len(data1) > 0 and len(data2) > 0:
            t_stat, p_value = ttest_ind(data1, data2, equal_var=False)
        else:
            t_stat, p_value = np.nan, np.nan
        
        results.append({
            'Group 1': group1,
            'Group 2': group2,
            't-statistic': t_stat,
            'p-value': p_value
        })

    return pd.DataFrame(results)

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
            # For 'Temperature', pick the exact match or the first match
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

all_data_filtered['Energy_per_Load'] = all_data_filtered['Proc Energy (Joules)'] / all_data_filtered['LoadPercent']

all_data_filtered['Energy_per_Thread'] = all_data_filtered['Proc Energy (Joules)'] / all_data_filtered['NumThreads']

all_data_filtered['Combined_Efficiency'] = (all_data_filtered['LoadPercent'] * all_data_filtered['NumThreads']) / all_data_filtered['Proc Energy (Joules)']

# Create a separate DataFrame excluding LoadPercent = 0 for EPUL
epul_data = all_data_filtered[all_data_filtered['LoadPercent'] > 0].copy()
# Recalculate Energy_per_Load to ensure no division by zero
epul_data['Energy_per_Load'] = epul_data['Proc Energy (Joules)'] / epul_data['LoadPercent']
# Update cpu_efficiency using epul_data
cpu_efficiency_epul = epul_data.groupby(['CPU', 'NumThreads', 'LoadPercent']).agg(
    AvgEnergy=('Proc Energy (Joules)', 'mean'),
    StdEnergy=('Proc Energy (Joules)', 'std'),
    AvgUtilization=('CPU Utilization', 'mean'),
    AvgTemperature=('Temperature', 'mean'),
    AvgEPUL=('Energy_per_Load', 'mean'),
    StdEPUL=('Energy_per_Load', 'std'),
    AvgEPT=('Energy_per_Thread', 'mean'),
    StdEPT=('Energy_per_Thread', 'std'),
    AvgCME=('Combined_Efficiency', 'mean'),
    StdCME=('Combined_Efficiency', 'std')
).reset_index()

# Group data by CPU, LoadPercent, and NumThreads for overall metrics
cpu_efficiency = all_data_filtered.groupby(['CPU', 'NumThreads', 'LoadPercent']).agg(
    AvgEnergy=('Proc Energy (Joules)', 'mean'),
    StdEnergy=('Proc Energy (Joules)', 'std'),
    AvgUtilization=('CPU Utilization', 'mean'),
    AvgTemperature=('Temperature', 'mean'),
    AvgEPUL=('Energy_per_Load', 'mean'),
    StdEPUL=('Energy_per_Load', 'std'),
    AvgEPT=('Energy_per_Thread', 'mean'),
    StdEPT=('Energy_per_Thread', 'std'),
    AvgCME=('Combined_Efficiency', 'mean'),
    StdCME=('Combined_Efficiency', 'std')
).reset_index()

# Visualization: Energy per Load Unit by Thread Count and CPU
plt.figure(figsize=(12, 6))
sns.lineplot(data=cpu_efficiency_epul, x='LoadPercent', y='AvgEPUL', hue='NumThreads', style='CPU', marker='o')
plt.title('Energy per Load Unit (EPUL) by Thread Count and CPU')
plt.xlabel('Load Percentage (%)')
plt.ylabel('Average EPUL (Joules/%)')
plt.legend(title='Thread Count and CPU')
plt.grid(True)
plt.show()

# Visualization: Energy per Thread by Thread Count and CPU
plt.figure(figsize=(12, 6))
sns.lineplot(data=cpu_efficiency_epul, x='LoadPercent', y='AvgEPT', hue='NumThreads', style='CPU', marker='o')
plt.title('Energy per Thread (EPT) by Thread Count and CPU')
plt.xlabel('Load Percentage (%)')
plt.ylabel('Average EPT (Joules/Thread)')
plt.legend(title='Thread Count and CPU')
plt.grid(True)
plt.show()

plt.figure(figsize=(12, 6))
sns.lineplot(data=cpu_efficiency_epul, x='LoadPercent', y='AvgCME', hue='NumThreads', style='CPU', marker='o')
plt.title('Combined Efficiency Metric (CME) by Thread Count and CPU')
plt.xlabel('Load Percentage (%)')
plt.ylabel('Average CME ((% Load * Threads)/Joules)')
plt.legend(title='Thread Count and CPU')
plt.grid(True)
plt.show()

# Regression Analysis
regression_data = all_data_filtered[['Proc Energy (Joules)', 'LoadPercent', 'NumThreads', 'FREQ', 'Temperature', 'CPU Utilization', 'CPU']].dropna()

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
plt.figure(figsize=(8, 6))
plt.scatter(y, y_pred, alpha=0.5)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--')
plt.title('Actual vs Predicted Energy Consumption')
plt.xlabel('Actual Energy (Joules)')
plt.ylabel('Predicted Energy (Joules)')
plt.grid(True)
plt.show()

# Residual Plot
residuals = y - y_pred
plt.figure(figsize=(8, 6))
plt.scatter(y_pred, residuals, alpha=0.5)
plt.axhline(0, color='red', linestyle='--')
plt.title('Residuals')
plt.xlabel('Predicted Energy (Joules)')
plt.ylabel('Residuals (Joules)')
plt.grid(True)
plt.show()

# CPU-specific scatterplots
plt.figure(figsize=(8, 6))
sns.scatterplot(data=regression_data, x='CPU Utilization', y='Proc Energy (Joules)', hue='CPU')
plt.title('Energy Consumption vs CPU Utilization by CPU')
plt.xlabel('CPU Utilization (%)')
plt.ylabel('Energy Consumption (Joules)')
plt.legend(title='CPU')
plt.grid(True)
plt.show()

plt.figure(figsize=(8, 6))
sns.scatterplot(data=regression_data, x='FREQ', y='Proc Energy (Joules)', hue='CPU')
plt.title('Energy Consumption vs Frequency by CPU')
plt.xlabel('Frequency (MHz)')
plt.ylabel('Energy Consumption (Joules)')
plt.legend(title='CPU')
plt.grid(True)
plt.show()

# Function to generate heatmap
def generate_heatmap(data, title):
    correlation_data = data[['LoadPercent', 'Proc Energy (Joules)', 'FREQ', 'AFREQ', 'Temperature', 
                             'CPU Utilization', 'C1res%', 'C3res%',
                             'C6res%', 'C7res%', 'READ', 'WRITE']].corr()
    print(f"\nCorrelation Data for {title}:")
    print(correlation_data)
    plt.figure(figsize=(12, 10))
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
print(cpu_efficiency_epul)

print("\nCorrelation Matrix of Key Metrics:")
correlation_matrix = all_data_filtered[['Proc Energy (Joules)', 'LoadPercent', 'Temperature', 'CPU Utilization']].corr()
print(correlation_matrix)

print("\nOutlier Detection - Rows with Extreme Energy Consumption:")
outliers = all_data_filtered[all_data_filtered['Proc Energy (Joules)'] > all_data_filtered['Proc Energy (Joules)'].quantile(0.99)]
print(outliers)

print("\nOutlier Detection - Rows with Extreme Energy per Load:")
outliers_epul = epul_data[epul_data['Energy_per_Load'] > epul_data['Energy_per_Load'].quantile(0.99)]
print(outliers_epul)

print("\nOutlier Detection - Rows with Extreme Energy per Thread:")
outliers_ept = all_data_filtered[all_data_filtered['Energy_per_Thread'] > all_data_filtered['Energy_per_Thread'].quantile(0.99)]
print(outliers_ept)

print("\nThread-Level Energy and Temperature Averages:")
thread_averages = all_data_filtered.groupby(['NumThreadsLabel', 'LoadPercent']).agg({
    'Proc Energy (Joules)': 'mean',
    'Temperature': 'mean',
    'CPU Utilization': 'mean',
    'Energy_per_Load': 'mean',
    'Energy_per_Thread': 'mean'
}).reset_index()
print(thread_averages)

# Define thread comparisons
thread_comparisons = [
    (2, 4),
    (4, 6),
    (2, 6)
]

# Function to perform t-tests for energy efficiency metrics
def perform_t_tests_efficiency(data, metric, thread_comparisons, cpu_label):
    results = []
    cpu_data = data[data['CPU'] == cpu_label]
    for group1, group2 in thread_comparisons:
        data1 = cpu_data[cpu_data['NumThreads'] == group1][metric]
        data2 = cpu_data[cpu_data['NumThreads'] == group2][metric]
        
        if len(data1) > 0 and len(data2) > 0:
            t_stat, p_value = ttest_ind(data1, data2, equal_var=False)
        else:
            t_stat, p_value = np.nan, np.nan
        
        results.append({
            'Group 1': group1,
            'Group 2': group2,
            't-statistic': t_stat,
            'p-value': p_value
        })

    return pd.DataFrame(results)

# Perform t-tests for Energy Consumption
energy_test_results = perform_t_tests(
    data=all_data_filtered,
    metric='Proc Energy (Joules)',
    thread_comparisons=thread_comparisons,
    cpu_label='i713700K'
)

print("\nT-Test Results for Energy Consumption (i7-13700K):")
print(energy_test_results)

# Perform t-tests for Energy per Load Unit (EPUL)
energy_efficiency_tests_epul = perform_t_tests_efficiency(
    data=epul_data,
    metric='Energy_per_Load',
    thread_comparisons=thread_comparisons,
    cpu_label='i713700K'
)

print("\nT-Test Results for Energy per Load Unit (EPUL) (i7-13700K):")
print(energy_efficiency_tests_epul)

# Perform t-tests for Energy per Thread (EPT)
energy_efficiency_tests_ept = perform_t_tests_efficiency(
    data=all_data_filtered,
    metric='Energy_per_Thread',
    thread_comparisons=thread_comparisons,
    cpu_label='i713700K'
)

print("\nT-Test Results for Energy per Thread (EPT) (i7-13700K):")
print(energy_efficiency_tests_ept)

# Perform t-tests for Temperature
temperature_test_results = perform_t_tests(
    data=all_data_filtered,
    metric='Temperature',
    thread_comparisons=thread_comparisons,
    cpu_label='i713700K'
)

print("\nT-Test Results for Temperature (i7-13700K):")
print(temperature_test_results)

# Scatterplot: Energy vs. Threads (i7-13700K)
plt.figure(figsize=(12, 6))
sns.scatterplot(data=all_data_filtered[all_data_filtered['CPU'] == 'i713700K'],
                x='NumThreadsLabel',
                y='Proc Energy (Joules)',
                hue='LoadPercent',
                palette='viridis')
plt.title('Energy Consumption by Threads (i7-13700K)')
plt.xlabel('Thread Group')
plt.ylabel('Energy Consumption (Joules)')
plt.legend(title='Load Percentage')
plt.grid(True)
plt.show()

# Scatterplot: Temperature vs. Threads (i7-13700K)
plt.figure(figsize=(12, 6))
sns.scatterplot(data=all_data_filtered[all_data_filtered['CPU'] == 'i713700K'],
                x='NumThreadsLabel',
                y='Temperature',
                hue='LoadPercent',
                palette='coolwarm')
plt.title('Temperature by Threads (i7-13700K)')
plt.xlabel('Thread Group')
plt.ylabel('Temperature (°C)')
plt.legend(title='Load Percentage')
plt.grid(True)
plt.show()
