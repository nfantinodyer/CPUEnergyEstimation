import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.metrics import mean_squared_error, r2_score

# Set seaborn style
sns.set_style('whitegrid')

# Define base directory
base_dir = "Data/NewData/Windows"

# Define thread-specific files
thread_files = {
    '2 Threads': os.path.join(base_dir, 'Windows2threads.csv'),
    '4 Threads': os.path.join(base_dir, 'Windows4threads.csv'),
    '6 Threads': os.path.join(base_dir, 'Windows6threads.csv'),
    '8 Threads': os.path.join(base_dir, 'Windows8threads.csv')
}

# Function to load data
def load_data(file_path, num_threads_label):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    
    print(f"Loading file: {file_path}")
    
    # Read the file, skipping the first row (datatype row) and identifying the correct header
    df = pd.read_csv(file_path, skiprows=1)
    
    # Ensure the DateTime column exists
    if 'DateTime' not in df.columns:
        print(f"'DateTime' column not found in {file_path}. Ensure the correct header row is specified.")
        return None
    
    # Convert DateTime column to datetime format
    df['DateTime'] = pd.to_datetime(df['DateTime'], errors='coerce')
    df.dropna(subset=['DateTime'], inplace=True)
    
    # Rename 'C0res%' to 'LoadPercent' for consistency
    if 'C0res%' in df.columns:
        df.rename(columns={'C0res%': 'LoadPercent'}, inplace=True)
        print("Renamed 'C0res%' to 'LoadPercent'")
    
    # Add thread label for identification
    df['NumThreads'] = int(num_threads_label.split()[0])
    
    return df


# Load and combine data
data_frames = []
for num_threads_label, file_path in thread_files.items():
    df = load_data(file_path, num_threads_label)
    if df is not None:
        data_frames.append(df)

# Combine all thread-specific data
if not data_frames:
    print("No data files loaded. Exiting.")
    exit()

all_data = pd.concat(data_frames, ignore_index=True)

# Check if the dataset is empty
if all_data.empty:
    print("Dataset is empty. Exiting.")
    exit()

# --- TEMP Analysis ---

# Filter data for TEMP analysis
TEMP_data = all_data[['LoadPercent', 'NumThreads', 'TEMP']].dropna()

# Average TEMP by thread count and load
avg_temp = TEMP_data.groupby(['NumThreads', 'LoadPercent'])['TEMP'].mean().reset_index()

# Plot average TEMP
plt.figure(figsize=(10, 6))

# Scatter plot for TEMP analysis
sns.scatterplot(
    data=avg_temp,
    x='LoadPercent',
    y='TEMP',
    hue='NumThreads',
    style='NumThreads',
    palette='coolwarm',
    s=100
)

# Add annotations for small LoadPercent values
for i, row in avg_temp.iterrows():
    if row['LoadPercent'] < 1:
        plt.text(row['LoadPercent'], row['TEMP'], 
                 f"{row['LoadPercent']:.2f}", 
                 fontsize=9, ha='center')

plt.title('Average TEMP by Threads and Load')
plt.xlabel('Load Percentage (%)')
plt.ylabel('TEMP (°C)')
plt.legend(title='Threads')
plt.grid(True)
plt.show()

# --- Additional Metrics: Correlation with Energy ---

# Investigate correlation between TEMP and energy consumption
correlation_data = all_data[['TEMP', 'Proc Energy (Joules)', 'LoadPercent', 'NumThreads']].dropna()

# Scatter plot: TEMP vs Energy
plt.figure(figsize=(10, 6))
sns.scatterplot(
    data=correlation_data,
    x='TEMP',
    y='Proc Energy (Joules)',
    hue='NumThreads',
    style='NumThreads',
    palette='coolwarm',
    s=100
)
plt.title('Processor Energy Consumption vs TEMP')
plt.xlabel('TEMP (°C)')
plt.ylabel('Energy Consumption (Joules)')
plt.legend(title='Threads')
plt.grid(True)
plt.show()

# --- Regression Analysis ---

# Prepare data for regression
regression_data = all_data[['LoadPercent', 'NumThreads', 'FREQ', 'TEMP', 'Proc Energy (Joules)']].dropna()

# Features and target
X = regression_data[['LoadPercent', 'NumThreads', 'FREQ', 'TEMP']]
y = regression_data['Proc Energy (Joules)']

# Normalize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Polynomial regression
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X_scaled)

model = LinearRegression()
model.fit(X_poly, y)

# Predictions and metrics
y_pred = model.predict(X_poly)
mse = mean_squared_error(y, y_pred)
r2 = r2_score(y, y_pred)

print(f"Polynomial Regression - RMSE: {np.sqrt(mse):.4f}")
print(f"Polynomial Regression - R-squared: {r2:.4f}")

# Plot Actual vs Predicted
plt.figure(figsize=(10, 6))
plt.scatter(y, y_pred, alpha=0.5)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'r--', label='Perfect Fit')
plt.xlabel('Actual Energy Consumption (Joules)')
plt.ylabel('Predicted Energy Consumption (Joules)')
plt.title('Actual vs Predicted Energy Consumption')
plt.legend()
plt.grid(True)
plt.show()

# Residuals plot
residuals = y - y_pred
plt.figure(figsize=(10, 6))
plt.scatter(y_pred, residuals, alpha=0.5)
plt.axhline(y=0, color='r', linestyle='--', label='Zero Error')
plt.xlabel('Predicted Energy Consumption (Joules)')
plt.ylabel('Residuals')
plt.title('Residual Plot')
plt.legend()
plt.grid(True)
plt.show()

print("Analysis complete.")
