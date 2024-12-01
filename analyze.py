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
linux = 'Data/Linux/newLinux.csv'
windows = 'Data/Windows/newWindows.csv'

# Load data
linuxData = pd.read_csv(linux, skiprows=1)
windowsData = pd.read_csv(windows, skiprows=1)

# Convert DateTime
linuxData['DateTime'] = pd.to_datetime(linuxData['DateTime'], errors='coerce')
windowsData['DateTime'] = pd.to_datetime(windowsData['DateTime'], errors='coerce')

# Check for any parsing errors
linuxData = linuxData.dropna(subset=['DateTime'])
windowsData = windowsData.dropna(subset=['DateTime'])

# Print columns to check
print("Linux data columns:")
print(linuxData.columns)
print("Windows data columns:")
print(windowsData.columns)

# Mapping of columns of interest to actual columns in the data
columnsOfInterest = [
    'Proc Energy (Joules)', 'CPU Utilization', 'L3MISS', 'L2MISS', 'L3HIT', 'L2HIT', 'EXEC', 'IPC',
    'FREQ', 'AFREQ', 'CFREQ', 'TEMP', 'INSTnom', 'INSTnom%', 'C0res%', 'C1res%', 'C3res%',
    'C6res%', 'C7res%', 'READ', 'WRITE', 'L3MPI', 'L2MPI', 'TIME(ticks)', 'PhysIPC',
    'PhysIPC%', 'SKT0'
]

def getMatchingColumns(columnsList, dataColumns):
    matchingColumns = {}
    for col in columnsList:
        matches = [c for c in dataColumns if c.startswith(col)]
        if matches:
            # Select the first occurrence
            matchingColumns[col] = matches[0]
    return matchingColumns

linuxMatchingColumns = getMatchingColumns(columnsOfInterest, linuxData.columns)
windowsMatchingColumns = getMatchingColumns(columnsOfInterest, windowsData.columns)

print("\nLinux matching columns:")
print(linuxMatchingColumns)
print("\nWindows matching columns:")
print(windowsMatchingColumns)

# Filter data for columns of interest
linuxDataFiltered = linuxData[list(linuxMatchingColumns.values())].copy()
windowsDataFiltered = windowsData[list(windowsMatchingColumns.values())].copy()

# Rename the columns to standard names
linuxDataFiltered.columns = list(linuxMatchingColumns.keys())
windowsDataFiltered.columns = list(windowsMatchingColumns.keys())

# Add DateTime back to filtered data
linuxDataFiltered['DateTime'] = linuxData['DateTime'].values
windowsDataFiltered['DateTime'] = windowsData['DateTime'].values

# Calculate the total duration of recording for Linux and Windows
linuxDuration = (linuxDataFiltered['DateTime'].max() - linuxDataFiltered['DateTime'].min()).total_seconds()
windowsDuration = (windowsDataFiltered['DateTime'].max() - windowsDataFiltered['DateTime'].min()).total_seconds()

# Print the total durations
print(f"\nLinux Total Duration (seconds): {linuxDuration}")
print(f"Windows Total Duration (seconds): {windowsDuration}")

# Calculate the difference in duration between Linux and Windows recordings
durationDifference = abs(linuxDuration - windowsDuration)
print(f"Difference in Recording Durations (seconds): {durationDifference}")

# Compare the durations to the expected 3 minutes
expectedDuration = 3 * 60  # 3 minutes in seconds
linuxDeviationFromExpected = linuxDuration - expectedDuration
windowsDeviationFromExpected = windowsDuration - expectedDuration

# Print the deviations from the expected duration
print(f"Linux Deviation from Expected Duration (seconds): {linuxDeviationFromExpected}")
print(f"Windows Deviation from Expected Duration (seconds): {windowsDeviationFromExpected}")

# Check for duplicate timestamps
print(f"\nDuplicate timestamps in Windows: {windowsDataFiltered['DateTime'].duplicated().sum()}")
print(f"Duplicate timestamps in Linux: {linuxDataFiltered['DateTime'].duplicated().sum()}")

# Analyze time intervals
linuxIntervals = linuxDataFiltered['DateTime'].diff().dropna()
windowsIntervals = windowsDataFiltered['DateTime'].diff().dropna()

plt.figure(figsize=(12, 6))

# Linux Histogram - Adjusted to be first
plt.subplot(1, 2, 1)
plt.hist(linuxIntervals.dt.total_seconds(), bins=50, color='blue', alpha=0.7)
plt.title('Linux Timestamp Intervals')
plt.xlabel('Interval (seconds)')
plt.ylabel('Frequency')

# Windows Histogram
plt.subplot(1, 2, 2)
plt.hist(windowsIntervals.dt.total_seconds(), bins=50, color='orange', alpha=0.7)
plt.title('Windows Timestamp Intervals')
plt.xlabel('Interval (seconds)')
plt.ylabel('Frequency')

plt.tight_layout()
plt.show()

# Compare data points per second
linuxRate = len(linuxDataFiltered) / linuxDuration
windowsRate = len(windowsDataFiltered) / windowsDuration

print(f"\nLinux Data Points per Second: {linuxRate}")
print(f"Windows Data Points per Second: {windowsRate}")

# Compute correlations
linuxCorr = linuxDataFiltered.drop(columns=['DateTime']).corr()
windowsCorr = windowsDataFiltered.drop(columns=['DateTime']).corr()

# Plot correlation matrices
plt.figure(figsize=(18, 8))

# Linux Correlation Matrix
plt.subplot(1, 2, 1)
sns.heatmap(linuxCorr, annot=False, cmap='coolwarm', xticklabels=True, yticklabels=True)
plt.title('Linux Correlation Matrix')

# Windows Correlation Matrix
plt.subplot(1, 2, 2)
sns.heatmap(windowsCorr, annot=False, cmap='coolwarm', xticklabels=True, yticklabels=True)
plt.title('Windows Correlation Matrix')

plt.tight_layout()
plt.show()

# Print correlation with energy usage
print("\nLinux Correlation with Energy Usage:")
print(linuxCorr['Proc Energy (Joules)'].sort_values(ascending=False))

print("\nWindows Correlation with Energy Usage:")
print(windowsCorr['Proc Energy (Joules)'].sort_values(ascending=False))

# Scatterplots for key variables vs energy
plt.figure(figsize=(12, 6))

# Linux Scatterplot - Adjusted to be first
plt.subplot(1, 2, 1)
plt.scatter(linuxDataFiltered['FREQ'], linuxDataFiltered['Proc Energy (Joules)'], alpha=0.6, color='blue')
plt.xlabel('Frequency (FREQ)')
plt.ylabel('Processor Energy (Joules)')
plt.title('Linux: Frequency vs Energy')

# Windows Scatterplot
plt.subplot(1, 2, 2)
plt.scatter(windowsDataFiltered['FREQ'], windowsDataFiltered['Proc Energy (Joules)'], alpha=0.6, color='orange')
plt.xlabel('Frequency (FREQ)')
plt.ylabel('Processor Energy (Joules)')
plt.title('Windows: Frequency vs Energy')

plt.tight_layout()
plt.show()

# Grouped average energy consumption by OS
linuxDataFiltered['OS'] = 'Linux'
windowsDataFiltered['OS'] = 'Windows'
combinedData = pd.concat([linuxDataFiltered, windowsDataFiltered], ignore_index=True)

# Ensure Linux is first in the bar plot
groupedData = combinedData.groupby('OS').mean()
groupedData = groupedData.reindex(['Linux', 'Windows'])  # Adjusted to ensure Linux is first

groupedData['Proc Energy (Joules)'].plot(kind='bar', color=['blue', 'orange'])
plt.ylabel('Average Energy (Joules)')
plt.title('Average Energy Consumption by OS')
plt.show()

# --- Estimation Model Development ---

# Use 'C0res%' as a proxy for CPU Utilization if not present
if 'CPU Utilization' not in linuxDataFiltered.columns and 'C0res%' in linuxDataFiltered.columns:
    linuxDataFiltered['CPU Utilization'] = linuxDataFiltered['C0res%']

if 'CPU Utilization' not in windowsDataFiltered.columns and 'C0res%' in windowsDataFiltered.columns:
    windowsDataFiltered['CPU Utilization'] = windowsDataFiltered['C0res%']

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
linuxVarsPresent = [var for var in variables if var in linuxDataFiltered.columns]
windowsVarsPresent = [var for var in variables if var in windowsDataFiltered.columns]

# Drop any rows with missing values
linuxRegressionData = linuxDataFiltered[linuxVarsPresent].dropna().copy()
windowsRegressionData = windowsDataFiltered[windowsVarsPresent].dropna().copy()

# --- Ridge Regression to Handle Multicollinearity for Windows ---

# Prepare data for Linux
XLinuxFull = linuxRegressionData.drop(columns=['Proc Energy (Joules)'])
yLinux = linuxRegressionData['Proc Energy (Joules)']

# Create a pipeline with scaling and Ridge Regression
ridgePipelineLinux = make_pipeline(StandardScaler(), Ridge(alpha=1.0))

# Fit the Ridge model for Linux
ridgePipelineLinux.fit(XLinuxFull, yLinux)

# Predict using the Ridge model
linuxRegressionData['Estimated Power'] = ridgePipelineLinux.predict(XLinuxFull)

# Calculate errors for the Ridge model
maeLinuxRidge = mean_absolute_error(yLinux, linuxRegressionData['Estimated Power'])
rmseLinuxRidge = np.sqrt(mean_squared_error(yLinux, linuxRegressionData['Estimated Power']))
print(f"\nLinux Ridge Model MAE: {maeLinuxRidge}")
print(f"Linux Ridge Model RMSE: {rmseLinuxRidge}")

# Prepare data for Windows
XWindowsFull = windowsRegressionData.drop(columns=['Proc Energy (Joules)'])
yWindows = windowsRegressionData['Proc Energy (Joules)']

# Create a pipeline with scaling and Ridge Regression
ridgePipelineWindows = make_pipeline(StandardScaler(), Ridge(alpha=1.0))

# Fit the Ridge model for Windows
ridgePipelineWindows.fit(XWindowsFull, yWindows)

# Predict using the Ridge model
windowsRegressionData['Estimated Power'] = ridgePipelineWindows.predict(XWindowsFull)

# Calculate errors for the Ridge model
maeWindowsRidge = mean_absolute_error(yWindows, windowsRegressionData['Estimated Power'])
rmseWindowsRidge = np.sqrt(mean_squared_error(yWindows, windowsRegressionData['Estimated Power']))
print(f"\nWindows Ridge Model MAE: {maeWindowsRidge}")
print(f"Windows Ridge Model RMSE: {rmseWindowsRidge}")

# --- Extract Coefficients from Ridge Models ---

# Simplified function to extract coefficients
def getRidgeCoefficients(model, featureNames):
    # Retrieve the intercept and coefficients
    intercept = model.named_steps['ridge'].intercept_
    coefficients = model.named_steps['ridge'].coef_
    # Combine feature names and coefficients into a dictionary
    coefDict = {'Intercept': intercept}
    coefDict.update(dict(zip(featureNames, coefficients)))
    return coefDict

# Get coefficients for Linux Ridge model
linuxCoefRidge = getRidgeCoefficients(ridgePipelineLinux, XLinuxFull.columns)
print("\nLinux Ridge Model Coefficients:")
for key, value in linuxCoefRidge.items():
    print(f"{key}: {value}")

# Get coefficients for Windows Ridge model
windowsCoefRidge = getRidgeCoefficients(ridgePipelineWindows, XWindowsFull.columns)
print("\nWindows Ridge Model Coefficients:")
for key, value in windowsCoefRidge.items():
    print(f"{key}: {value}")

# --- Plot Actual vs Estimated Power Consumption for Ridge Models ---

plt.figure(figsize=(12, 5))

# Linux Ridge Plot
plt.subplot(1, 2, 1)
plt.scatter(yLinux, linuxRegressionData['Estimated Power'], alpha=0.5, color='blue')
plt.plot([yLinux.min(), yLinux.max()], [yLinux.min(), yLinux.max()], 'r--')
plt.xlabel('Actual Power Consumption (Joules)')
plt.ylabel('Estimated Power Consumption (Joules)')
plt.title('Linux Ridge Model: Actual vs Estimated Power')

# Windows Ridge Plot
plt.subplot(1, 2, 2)
plt.scatter(yWindows, windowsRegressionData['Estimated Power'], alpha=0.5, color='orange')
plt.plot([yWindows.min(), yWindows.max()], [yWindows.min(), yWindows.max()], 'r--')
plt.xlabel('Actual Power Consumption (Joules)')
plt.ylabel('Estimated Power Consumption (Joules)')
plt.title('Windows Ridge Model: Actual vs Estimated Power')

plt.tight_layout()
plt.show()

# --- Calculate R-squared for Ridge Models ---

# For Linux Ridge Model
rSquaredLinux = ridgePipelineLinux.score(XLinuxFull, yLinux)
print(f"\nLinux Ridge Model R-squared: {rSquaredLinux}")

# For Windows Ridge Model
rSquaredWindows = ridgePipelineWindows.score(XWindowsFull, yWindows)
print(f"Windows Ridge Model R-squared: {rSquaredWindows}")
