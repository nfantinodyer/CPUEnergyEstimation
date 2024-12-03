import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Define base directory (adjust this path as needed)
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
            print(f"Loading file: {file_path}")
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
            df['SourceFile'] = filename  # Include the source file name
            
            data_frames.append(df)
        else:
            print(f"File not found: {file_path}")
    return data_frames

# Determine the actual maximum number of threads
# For the purpose of this code, let's assume it's 8
max_threads = 8  # Adjust this number to match your system's maximum threads

# Adjust the mapping
num_threads_labels = {
    max_threads: '8 Threads',  # Update label to '8 Threads' for clarity
    2: '2 Threads',
    4: '4 Threads',
    6: '6 Threads'
}

# Initialize data frames list
data_frames = []

# Iterate over each directory and load data
for label, dir_path in directories.items():
    if 'All' in label:
        files = create_file_paths(dir_path, all_loads, 'Static')
        num_threads = max_threads  # Set num_threads to the actual max threads
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

# Convert 'NumThreads' to numeric (should already be numeric)
all_data['NumThreads'] = pd.to_numeric(all_data['NumThreads'], errors='coerce')
all_data.dropna(subset=['NumThreads'], inplace=True)

# Print unique values of NumThreads
print("Unique NumThreads values in all_data:")
print(all_data['NumThreads'].unique())

# Print columns in all_data
print("Columns in all_data:")
print(all_data.columns.tolist())

# Define columns of interest
columnsOfInterest = [
    'DateTime', 'LoadPercent', 'NumThreads', 'SourceFile',
    'Proc Energy (Joules)', 'CPU Utilization', 'FREQ', 'AFREQ', 'TEMP', 'C0res%', 'C1res%', 'C3res%',
    'C6res%', 'C7res%', 'READ', 'WRITE'
]

# Function to get matching columns
def getMatchingColumns(columnsList, dataColumns):
    matchingColumns = {}
    for col in columnsList:
        matches = [c for c in dataColumns if c.startswith(col)]
        if matches:
            # For 'TEMP', pick the exact match or the first match
            if col == 'TEMP':
                temp_matches = [c for c in matches if c == 'TEMP']
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

# Print columns in all_data_filtered
print("Columns in all_data_filtered:")
print(all_data_filtered.columns.tolist())

# Data cleaning
all_data_filtered['LoadPercent'] = pd.to_numeric(all_data_filtered['LoadPercent'], errors='coerce')
all_data_filtered['NumThreads'] = pd.to_numeric(all_data_filtered['NumThreads'], errors='coerce')

# Map 'NumThreads' to labels
all_data_filtered['NumThreadsLabel'] = all_data_filtered['NumThreads'].map(num_threads_labels)

# Print unique NumThreadsLabel values
print("Unique NumThreadsLabel values in all_data_filtered:")
print(all_data_filtered['NumThreadsLabel'].unique())

# Check for 'CPU Utilization'
if 'CPU Utilization' not in all_data_filtered.columns and 'C0res%' in all_data_filtered.columns:
    all_data_filtered['CPU Utilization'] = all_data_filtered['C0res%']
    print("Created 'CPU Utilization' from 'C0res%'")
else:
    print("'CPU Utilization' is present in data.")

# Print first few rows of all_data_filtered
print("First few rows of all_data_filtered:")
print(all_data_filtered.head())

# Replace missing or non-numeric TEMP values with NaN
all_data_filtered['TEMP'] = pd.to_numeric(all_data_filtered['TEMP'], errors='coerce')

# Find entries with zero or missing temperature values
zero_temp_entries = all_data_filtered[(all_data_filtered['TEMP'].isna()) | (all_data_filtered['TEMP'] == 0)]

# Check if any zero or missing temperature entries are found
if not zero_temp_entries.empty:
    print("Entries with zero or missing temperature values and their source files:")
    print(zero_temp_entries[['DateTime', 'LoadPercent', 'NumThreads', 'NumThreadsLabel', 'SourceFile', 'TEMP']])
else:
    print("No zero or missing temperature values found.")

# --- Compare Temperature Readings at Different Levels for 2, 4, 6, 8 Threads ---

# Remove entries with zero or missing temperature values
valid_temp_data = all_data_filtered[~((all_data_filtered['TEMP'].isna()) | (all_data_filtered['TEMP'] == 0))].copy()

# Check if we have valid temperature data
if valid_temp_data.empty:
    print("No valid temperature data available for comparison.")
else:
    # Plotting temperature readings against load percentages for each thread count
    plt.figure(figsize=(12, 8))
    sns.lineplot(
        data=valid_temp_data,
        x='LoadPercent',
        y='TEMP',
        hue='NumThreadsLabel',
        estimator='mean',
        marker='o'
    )
    plt.title('Average Temperature vs Load Percentage for Different Thread Counts')
    plt.xlabel('Load Percentage (%)')
    plt.ylabel('Average Temperature (°C)')
    plt.legend(title='Thread Count')
    plt.grid(True)
    plt.show()
    
    # Print statistical summaries
    temp_summary = valid_temp_data.groupby(['NumThreadsLabel', 'LoadPercent'])['TEMP'].describe().reset_index()
    print("Temperature Summary Statistics:")
    print(temp_summary)

    # Additional visualization: Boxplot of temperature distributions
    plt.figure(figsize=(12, 8))
    sns.boxplot(
        data=valid_temp_data,
        x='LoadPercent',
        y='TEMP',
        hue='NumThreadsLabel'
    )
    plt.title('Temperature Distribution by Load Percentage and Thread Count')
    plt.xlabel('Load Percentage (%)')
    plt.ylabel('Temperature (°C)')
    plt.legend(title='Thread Count')
    plt.grid(True)
    plt.show()
