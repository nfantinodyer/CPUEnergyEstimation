import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
import numpy as np

# Data sources
linux = 'Data/newLinux.csv'
windows = 'Data/newWindows.csv'

# Load data
linux_data = pd.read_csv(linux, skiprows=1)
windows_data = pd.read_csv(windows, skiprows=1)

# Convert DateTime
linux_data['DateTime'] = pd.to_datetime(linux_data['DateTime'], errors='coerce')
windows_data['DateTime'] = pd.to_datetime(windows_data['DateTime'], errors='coerce')

# Check for any parsing errors
linux_data = linux_data.dropna(subset=['DateTime'])
windows_data = windows_data.dropna(subset=['DateTime'])

# Print columns to check
print("Linux data columns:")
print(linux_data.columns)
print("Windows data columns:")
print(windows_data.columns)

# Due to duplicate columns, pandas appends '.1', '.2', etc.
# Let's create a mapping of columns of interest to actual columns in the data

columns_of_interest = [
    'Proc Energy (Joules)', 'CPU Utilization', 'L3MISS', 'L2MISS', 'L3HIT', 'L2HIT', 'EXEC', 'IPC',
    'FREQ', 'AFREQ', 'CFREQ', 'TEMP', 'INSTnom', 'INSTnom%', 'C0res%', 'C1res%', 'C3res%',
    'C6res%', 'C7res%', 'READ', 'WRITE', 'L3MPI', 'L2MPI', 'TIME(ticks)', 'PhysIPC',
    'PhysIPC%', 'SKT0'
]

def get_matching_columns(columns_list, data_columns):
    matching_columns = {}
    for col in columns_list:
        matches = [c for c in data_columns if c.startswith(col)]
        if matches:
            # Select the first occurrence
            matching_columns[col] = matches[0]
    return matching_columns

linux_matching_columns = get_matching_columns(columns_of_interest, linux_data.columns)
windows_matching_columns = get_matching_columns(columns_of_interest, windows_data.columns)

print("\nLinux matching columns:")
print(linux_matching_columns)
print("\nWindows matching columns:")
print(windows_matching_columns)

# Filter data for columns of interest
linux_data_filtered = linux_data[list(linux_matching_columns.values())].copy()
windows_data_filtered = windows_data[list(windows_matching_columns.values())].copy()

# Rename the columns to standard names
linux_data_filtered.columns = list(linux_matching_columns.keys())
windows_data_filtered.columns = list(windows_matching_columns.keys())

# Add DateTime back to filtered data
linux_data_filtered['DateTime'] = linux_data['DateTime'].values
windows_data_filtered['DateTime'] = windows_data['DateTime'].values

# Calculate the total duration of recording for Linux and Windows
linux_duration = (linux_data_filtered['DateTime'].max() - linux_data_filtered['DateTime'].min()).total_seconds()
windows_duration = (windows_data_filtered['DateTime'].max() - windows_data_filtered['DateTime'].min()).total_seconds()

# Print the total durations
print(f"\nLinux Total Duration (seconds): {linux_duration}")
print(f"Windows Total Duration (seconds): {windows_duration}")

# Calculate the difference in duration between Linux and Windows recordings
duration_difference = abs(linux_duration - windows_duration)
print(f"Difference in Recording Durations (seconds): {duration_difference}")

# Compare the durations to the expected 3 minutes
expected_duration = 3 * 60  # 3 minutes in seconds
linux_difference_from_expected = linux_duration - expected_duration
windows_difference_from_expected = windows_duration - expected_duration

# Print the deviations from the expected duration
print(f"Linux Deviation from Expected Duration (seconds): {linux_difference_from_expected}")
print(f"Windows Deviation from Expected Duration (seconds): {windows_difference_from_expected}")

# Check for duplicate timestamps
print(f"\nDuplicate timestamps in Windows: {windows_data_filtered['DateTime'].duplicated().sum()}")
print(f"Duplicate timestamps in Linux: {linux_data_filtered['DateTime'].duplicated().sum()}")

# Analyze time intervals
windows_intervals = windows_data_filtered['DateTime'].diff().dropna()
linux_intervals = linux_data_filtered['DateTime'].diff().dropna()

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.hist(windows_intervals.dt.total_seconds(), bins=50, color='orange', alpha=0.7)
plt.title('Windows Timestamp Intervals')
plt.xlabel('Interval (seconds)')
plt.ylabel('Frequency')

plt.subplot(1, 2, 2)
plt.hist(linux_intervals.dt.total_seconds(), bins=50, color='blue', alpha=0.7)
plt.title('Linux Timestamp Intervals')
plt.xlabel('Interval (seconds)')
plt.ylabel('Frequency')

plt.tight_layout()
plt.show()

# Compare data points per second
linux_rate = len(linux_data_filtered) / linux_duration
windows_rate = len(windows_data_filtered) / windows_duration

print(f"\nLinux Data Points per Second: {linux_rate}")
print(f"Windows Data Points per Second: {windows_rate}")

# Compute correlations
linux_corr = linux_data_filtered.drop(columns=['DateTime']).corr()
windows_corr = windows_data_filtered.drop(columns=['DateTime']).corr()

# Plot correlation matrices
plt.figure(figsize=(18, 8))
plt.subplot(1, 2, 1)
sns.heatmap(linux_corr, annot=False, cmap='coolwarm', xticklabels=True, yticklabels=True)
plt.title('Linux Correlation Matrix')

plt.subplot(1, 2, 2)
sns.heatmap(windows_corr, annot=False, cmap='coolwarm', xticklabels=True, yticklabels=True)
plt.title('Windows Correlation Matrix')

plt.tight_layout()
plt.show()

# Print correlation with energy usage
print("\nLinux Correlation with Energy Usage:")
print(linux_corr['Proc Energy (Joules)'].sort_values(ascending=False))

print("\nWindows Correlation with Energy Usage:")
print(windows_corr['Proc Energy (Joules)'].sort_values(ascending=False))

# Scatterplots for key variables vs energy
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.scatter(linux_data_filtered['FREQ'], linux_data_filtered['Proc Energy (Joules)'], alpha=0.6)
plt.xlabel('Frequency (FREQ)')
plt.ylabel('Processor Energy (Joules)')
plt.title('Linux: Frequency vs Energy')

plt.subplot(1, 2, 2)
plt.scatter(windows_data_filtered['FREQ'], windows_data_filtered['Proc Energy (Joules)'], alpha=0.6)
plt.xlabel('Frequency (FREQ)')
plt.ylabel('Processor Energy (Joules)')
plt.title('Windows: Frequency vs Energy')

plt.tight_layout()
plt.show()

# Grouped average energy consumption by OS
linux_data_filtered['OS'] = 'Linux'
windows_data_filtered['OS'] = 'Windows'
combined_data = pd.concat([linux_data_filtered, windows_data_filtered], ignore_index=True)

grouped_data = combined_data.groupby('OS').mean()
grouped_data['Proc Energy (Joules)'].plot(kind='bar', color=['blue', 'orange'])
plt.ylabel('Average Energy (Joules)')
plt.title('Average Energy Consumption by OS')
plt.show()

# --- Estimation Model Development ---

# Use 'C0res%' as a proxy for CPU Utilization if not present
if 'CPU Utilization' not in linux_data_filtered.columns and 'C0res%' in linux_data_filtered.columns:
    linux_data_filtered['CPU Utilization'] = linux_data_filtered['C0res%']

if 'CPU Utilization' not in windows_data_filtered.columns and 'C0res%' in windows_data_filtered.columns:
    windows_data_filtered['CPU Utilization'] = windows_data_filtered['C0res%']

# Prepare the data for regression analysis
variables = [
    'Proc Energy (Joules)',    # Dependent variable
    'CPU Utilization',
    'FREQ', 'IPC',
    'L3MPI',
    'TEMP',
    # Add more variables if needed and available
]

# Ensure all variables are present
linux_vars_present = [var for var in variables if var in linux_data_filtered.columns]
windows_vars_present = [var for var in variables if var in windows_data_filtered.columns]

# Drop any rows with missing values
linux_regression_data = linux_data_filtered[linux_vars_present].dropna().copy()
windows_regression_data = windows_data_filtered[windows_vars_present].dropna().copy()

# --- Ridge Regression to Handle Multicollinearity for Windows ---

from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

# Prepare data for Windows
X_windows_full = windows_regression_data.drop(columns=['Proc Energy (Joules)'])
y_windows = windows_regression_data['Proc Energy (Joules)']

# Create a pipeline with scaling and Ridge Regression
ridge_pipeline_windows = make_pipeline(StandardScaler(), Ridge(alpha=1.0))

# Fit the Ridge model for Windows
ridge_pipeline_windows.fit(X_windows_full, y_windows)

# Predict using the Ridge model
windows_regression_data['Estimated Power'] = ridge_pipeline_windows.predict(X_windows_full)

# Calculate errors for the Ridge model
mae_windows_ridge = mean_absolute_error(y_windows, windows_regression_data['Estimated Power'])
rmse_windows_ridge = np.sqrt(mean_squared_error(y_windows, windows_regression_data['Estimated Power']))
print(f"\nWindows Ridge Model MAE: {mae_windows_ridge}")
print(f"Windows Ridge Model RMSE: {rmse_windows_ridge}")

# For Linux, you can also apply Ridge Regression if desired
# Prepare data for Linux
X_linux_full = linux_regression_data.drop(columns=['Proc Energy (Joules)'])
y_linux = linux_regression_data['Proc Energy (Joules)']

# Create a pipeline with scaling and Ridge Regression
ridge_pipeline_linux = make_pipeline(StandardScaler(), Ridge(alpha=1.0))

# Fit the Ridge model for Linux
ridge_pipeline_linux.fit(X_linux_full, y_linux)

# Predict using the Ridge model
linux_regression_data['Estimated Power'] = ridge_pipeline_linux.predict(X_linux_full)

# Calculate errors for the Ridge model
mae_linux_ridge = mean_absolute_error(y_linux, linux_regression_data['Estimated Power'])
rmse_linux_ridge = np.sqrt(mean_squared_error(y_linux, linux_regression_data['Estimated Power']))
print(f"\nLinux Ridge Model MAE: {mae_linux_ridge}")
print(f"Linux Ridge Model RMSE: {rmse_linux_ridge}")

# --- Extract Coefficients from Ridge Models ---

# Function to extract and display coefficients
def get_ridge_coefficients(model, feature_names):
    coefs = model.named_steps['ridge'].coef_
    intercept = model.named_steps['ridge'].intercept_
    coef_dict = {'Intercept': intercept}
    for coef, name in zip(coefs, feature_names):
        coef_dict[name] = coef
    return coef_dict

# Get coefficients for Windows Ridge model
windows_coef_ridge = get_ridge_coefficients(ridge_pipeline_windows, X_windows_full.columns)
print("\nWindows Ridge Model Coefficients:")
for key, value in windows_coef_ridge.items():
    print(f"{key}: {value}")

# Get coefficients for Linux Ridge model
linux_coef_ridge = get_ridge_coefficients(ridge_pipeline_linux, X_linux_full.columns)
print("\nLinux Ridge Model Coefficients:")
for key, value in linux_coef_ridge.items():
    print(f"{key}: {value}")

# --- Plot Actual vs Estimated Power Consumption for Ridge Models ---

plt.figure(figsize=(12, 5))

# Linux Ridge Plot
plt.subplot(1, 2, 1)
plt.scatter(y_linux, linux_regression_data['Estimated Power'], alpha=0.5)
plt.plot([y_linux.min(), y_linux.max()], [y_linux.min(), y_linux.max()], 'r--')
plt.xlabel('Actual Power Consumption (Joules)')
plt.ylabel('Estimated Power Consumption (Joules)')
plt.title('Linux Ridge Model: Actual vs Estimated Power')

# Windows Ridge Plot
plt.subplot(1, 2, 2)
plt.scatter(y_windows, windows_regression_data['Estimated Power'], alpha=0.5, color='orange')
plt.plot([y_windows.min(), y_windows.max()], [y_windows.min(), y_windows.max()], 'r--')
plt.xlabel('Actual Power Consumption (Joules)')
plt.ylabel('Estimated Power Consumption (Joules)')
plt.title('Windows Ridge Model: Actual vs Estimated Power')

plt.tight_layout()
plt.show()

# --- Calculate R-squared for Ridge Models ---

# For Linux Ridge Model
r_squared_linux = ridge_pipeline_linux.score(X_linux_full, y_linux)
print(f"\nLinux Ridge Model R-squared: {r_squared_linux}")

# For Windows Ridge Model
r_squared_windows = ridge_pipeline_windows.score(X_windows_full, y_windows)
print(f"Windows Ridge Model R-squared: {r_squared_windows}")
