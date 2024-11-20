import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

# Data sources
linux = 'Data/newLinux.csv'
windows = 'Data/newWindows.csv'

# Load data
linux_data = pd.read_csv(linux, skiprows=1)
windows_data = pd.read_csv(windows, skiprows=1)

# Convert DateTime
linux_data['DateTime'] = pd.to_datetime(linux_data['DateTime'])
windows_data['DateTime'] = pd.to_datetime(windows_data['DateTime'])

# Calculate the total duration of recording for Linux and Windows
linux_duration = (linux_data['DateTime'].max() - linux_data['DateTime'].min()).total_seconds()
windows_duration = (windows_data['DateTime'].max() - windows_data['DateTime'].min()).total_seconds()

# Print the total durations
print(f"Linux Total Duration (seconds): {linux_duration}")
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

# Columns of interest
linux_columns_of_interest = [
    'Proc Energy (Joules)', 'L3MISS', 'L2MISS', 'L3HIT', 'L2HIT', 'EXEC', 'IPC', 'FREQ', 'AFREQ', 'CFREQ',
    'TEMP', 'INSTnom', 'INSTnom%', 'C0res%', 'C1res%', 'C3res%', 'C6res%', 'C7res%', 'READ', 'WRITE',
    'L3MPI', 'L2MPI', 'TIME(ticks)', 'PhysIPC', 'PhysIPC%', 'SKT0'
]

windows_columns_of_interest = [
    'Proc Energy (Joules)', 'L3MISS', 'L2MISS', 'L3HIT', 'EXEC', 'IPC', 'FREQ', 'AFREQ', 'CFREQ',
    'TEMP', 'INSTnom', 'INSTnom%', 'C0res%', 'C1res%', 'C3res%', 'C7res%', 'READ', 'WRITE',
    'L3MPI', 'L2MPI', 'TIME(ticks)', 'PhysIPC', 'PhysIPC%', 'SKT0'
]

# Filter data for correlation analysis
linux_data_filtered = linux_data[[col for col in linux_columns_of_interest if col in linux_data.columns]]
windows_data_filtered = windows_data[[col for col in windows_columns_of_interest if col in windows_data.columns]]

# Check for duplicate timestamps
print(f"Duplicate timestamps in Windows: {windows_data['DateTime'].duplicated().sum()}")

# Analyze time intervals
windows_intervals = windows_data['DateTime'].diff().dropna()
linux_intervals = linux_data['DateTime'].diff().dropna()

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.hist(windows_intervals.dt.total_seconds(), bins=50, color='orange', alpha=0.7)
plt.title('Windows Timestamp Intervals')

plt.subplot(1, 2, 2)
plt.hist(linux_intervals.dt.total_seconds(), bins=50, color='blue', alpha=0.7)
plt.title('Linux Timestamp Intervals')
plt.tight_layout()
plt.show()

# Compare data points per second
linux_rate = len(linux_data) / (linux_data['DateTime'].max() - linux_data['DateTime'].min()).total_seconds()
windows_rate = len(windows_data) / (windows_data['DateTime'].max() - windows_data['DateTime'].min()).total_seconds()

print(f"Linux Data Points per Second: {linux_rate}")
print(f"Windows Data Points per Second: {windows_rate}")

# Remove non-numeric columns for resampling
linux_numeric = linux_data.select_dtypes(include=[float, int])
linux_numeric['DateTime'] = linux_data['DateTime']

windows_numeric = windows_data.select_dtypes(include=[float, int])
windows_numeric['DateTime'] = windows_data['DateTime']

# Resample to uniform intervals
linux_resampled = linux_numeric.set_index('DateTime').resample('25ms').mean().reset_index()
windows_resampled = windows_numeric.set_index('DateTime').resample('25ms').mean().reset_index()

print(f"Linux Resampled Rows: {len(linux_resampled)}")
print(f"Windows Resampled Rows: {len(windows_resampled)}")

# Check for missing timestamps in Linux
linux_missing = pd.date_range(start=linux_data['DateTime'].min(), end=linux_data['DateTime'].max(), freq='25ms').difference(linux_data['DateTime'])
print(f"Missing Timestamps in Linux: {len(linux_missing)}")

# Compute correlations
linux_corr = linux_data_filtered.corr()
windows_corr = windows_data_filtered.corr()

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
print("Linux Correlation with Energy Usage:")
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
combined_data = pd.concat([linux_data_filtered, windows_data_filtered])

grouped_data = combined_data.groupby('OS').mean()
grouped_data['Proc Energy (Joules)'].plot(kind='bar', color=['blue', 'orange'])
plt.ylabel('Average Energy (Joules)')
plt.title('Average Energy Consumption by OS')
plt.show()

# Regression analysis for Linux data
X_linux = linux_data_filtered[['FREQ', 'IPC', 'L3MISS']].dropna()  # Replace with relevant variables
y_linux = linux_data_filtered['Proc Energy (Joules)'].loc[X_linux.index]

X_linux = sm.add_constant(X_linux)  # Add intercept
model_linux = sm.OLS(y_linux, X_linux).fit()
print("Linux Regression Analysis:")
print(model_linux.summary())

# Regression analysis for Windows data
X_windows = windows_data_filtered[['FREQ', 'IPC', 'L3MISS']].dropna()  # Replace with relevant variables
y_windows = windows_data_filtered['Proc Energy (Joules)'].loc[X_windows.index]

X_windows = sm.add_constant(X_windows)  # Add intercept
model_windows = sm.OLS(y_windows, X_windows).fit()
print("Windows Regression Analysis:")
print(model_windows.summary())
