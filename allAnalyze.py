import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import ttest_ind

# Set seaborn style
sns.set_style('whitegrid')

# Define data directories for Linux and Windows
base_dirs = {
    'Linux': 'Data/NewData/Linux/StressNGData',
    'Windows': 'Data/NewData/Windows'
}

# Define thread and load-specific files
linux_thread_dirs = {
    'All Threads': os.path.join(base_dirs['Linux'], 'Static/AllThreads'),
    '2 Threads': os.path.join(base_dirs['Linux'], 'Static/TwoThreads'),
    '4 Threads': os.path.join(base_dirs['Linux'], 'Static/FourThreads'),
    '6 Threads': os.path.join(base_dirs['Linux'], 'Static/SixThreads')
}
windows_thread_files = {
    '2 Threads': os.path.join(base_dirs['Windows'], 'Windows2threads.csv'),
    '4 Threads': os.path.join(base_dirs['Windows'], 'Windows4threads.csv'),
    '6 Threads': os.path.join(base_dirs['Windows'], 'Windows6threads.csv'),
    '8 Threads': os.path.join(base_dirs['Windows'], 'Windows8threads.csv')
}

# Load data functions
def load_linux_data(thread_dirs):
    all_data = []
    for thread_label, directory in thread_dirs.items():
        if not os.path.exists(directory):
            print(f"Directory not found: {directory}")
            continue
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and file.endswith('.csv'):
                print(f"Loading Linux file: {file_path}")
                df = pd.read_csv(file_path, skiprows=1)
                df['NumThreadsLabel'] = thread_label
                df['SourceFile'] = file
                df['OS'] = 'Linux'
                df.rename(columns={'Temperature': 'Temp'}, inplace=True)
                all_data.append(df)
    print("Linux data loaded.")
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def load_windows_data(thread_files):
    all_data = []
    for thread_label, file_path in thread_files.items():
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            continue
        print(f"Loading Windows file: {file_path}")
        df = pd.read_csv(file_path, skiprows=1)
        df['NumThreadsLabel'] = thread_label
        df['SourceFile'] = os.path.basename(file_path)
        df['OS'] = 'Windows'
        df.rename(columns={'TEMP': 'Temp'}, inplace=True)
        all_data.append(df)
    print("Windows data loaded.")
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

# Load both datasets
linux_data = load_linux_data(linux_thread_dirs)
windows_data = load_windows_data(windows_thread_files)

print("Linux data sample:")
print(linux_data.head())
print("\nWindows data sample:")
print(windows_data.head())

# Clean and deduplicate data
linux_numeric_data = linux_data.select_dtypes(include=[np.number])
windows_numeric_data = windows_data.select_dtypes(include=[np.number])

# Remove duplicate columns
linux_numeric_data = linux_numeric_data.loc[:, ~linux_numeric_data.columns.duplicated()]
windows_numeric_data = windows_numeric_data.loc[:, ~windows_numeric_data.columns.duplicated()]

print("\nLinux numeric data columns:")
print(linux_numeric_data.columns.tolist())
print("\nWindows numeric data columns:")
print(windows_numeric_data.columns.tolist())

# Column categorization for heatmaps
categories = {
    "CPU and Energy Metrics": [
        "CPU Utilization", "Energy Consumption (Joules)", "Frequency", "Actual Frequency", "Temp"
    ],
    "Cache and Memory Metrics": [
        "L3MISS", "L2MISS", "IPC", "EXEC", "INSTnom", "TIME(ticks)", "PhysIPC"
    ],
    "Utilization Metrics": [
        "CPU Utilization", "C0res%", "C3res%", "C6res%", "C7res%"
    ],
    "Performance Metrics": [
        "IPC", "EXEC", "INSTnom", "TIME(ticks)", "PhysIPC"
    ]
}

# Function for heatmaps
def plot_heatmap(data, title):
    if data.shape[1] < 2:
        print(f"Skipping heatmap for '{title}' due to insufficient data.")
        return
    print(f"\nGenerating heatmap for '{title}'")
    print(data.corr())
    plt.figure(figsize=(12, 10))
    sns.heatmap(data.corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title(title)
    plt.show()

# Function for scatterplots
def scatter_plot(data, x, y, hue, title):
    if x not in data.columns or y not in data.columns:
        print(f"Skipping scatter plot for '{title}' due to missing columns.")
        return
    print(f"\nScatter plot data for '{title}':")
    print(data[[x, y, hue]].dropna().head())
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=data, x=x, y=y, hue=hue, palette='viridis', alpha=0.7)
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.grid(True)
    plt.legend(title=hue)
    plt.show()

# Function for line plots
def line_plot(data, x, y, hue, title):
    if x not in data.columns or y not in data.columns:
        print(f"Skipping line plot for '{title}' due to missing columns.")
        return
    print(f"\nLine plot data for '{title}':")
    print(data[[x, y]].dropna().head())
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=data, x=x, y=y, hue=hue, marker='o')
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.grid(True)
    plt.show()

# Generate and plot heatmaps for each category
for category, cols in categories.items():
    print(f"\nProcessing category: {category}")
    linux_subset = linux_numeric_data[linux_numeric_data.columns.intersection(cols)]
    windows_subset = windows_numeric_data[windows_numeric_data.columns.intersection(cols)]

    if not linux_subset.empty:
        plot_heatmap(linux_subset, f"Linux Heatmap: {category}")
    if not windows_subset.empty:
        plot_heatmap(windows_subset, f"Windows Heatmap: {category}")

# Scatterplots for Cache and Memory Metrics
scatter_plot(linux_data, "L3MISS", "IPC", "NumThreadsLabel", "Linux: IPC vs. L3MISS by Threads")
scatter_plot(windows_data, "L3MISS", "IPC", "NumThreadsLabel", "Windows: IPC vs. L3MISS by Threads")

# Scatterplots for Performance Metrics
scatter_plot(linux_data, "EXEC", "INSTnom", "NumThreadsLabel", "Linux: EXEC vs. INSTnom by Threads")
scatter_plot(windows_data, "EXEC", "INSTnom", "NumThreadsLabel", "Windows: EXEC vs. INSTnom by Threads")

# Additional correlations (cache vs. power utilization)
scatter_plot(linux_data, "L3MISS", "Proc Energy (Joules)", "NumThreadsLabel", "Linux: L3MISS vs. Proc Energy by Threads")
scatter_plot(windows_data, "L3MISS", "Proc Energy (Joules)", "NumThreadsLabel", "Windows: L3MISS vs. Proc Energy by Threads")

# Line plots for EXEC vs. INSTnom
line_plot(linux_numeric_data, "INSTnom", "EXEC", None, "Linux: EXEC vs. INSTnom")
line_plot(windows_numeric_data, "INSTnom", "EXEC", None, "Windows: EXEC vs. INSTnom")

# Energy efficiency calculations and visualizations
def compute_energy_efficiency(data):
    if 'INST' in data.columns and 'TIME(ticks)' in data.columns and 'Proc Energy (Joules)' in data.columns:
        data['Energy per Instruction'] = data['Proc Energy (Joules)'] / data['INST']
        data['Energy per Cycle'] = data['Proc Energy (Joules)'] / data['TIME(ticks)']
        data['Cache Miss per Joule'] = data['L3MISS'] / data['Proc Energy (Joules)']
    return data

linux_data = compute_energy_efficiency(linux_data)
windows_data = compute_energy_efficiency(windows_data)

# Summarize energy efficiency
def summarize_efficiency(data, os_name):
    print(f"\n{os_name} Energy Efficiency Summary:")
    summary = data[['Energy per Instruction', 'Energy per Cycle', 'Cache Miss per Joule']].describe().T
    print(summary)
    return summary

linux_summary = summarize_efficiency(linux_data, "Linux")
windows_summary = summarize_efficiency(windows_data, "Windows")

# Scatterplots for energy efficiency
scatter_plot(linux_data, "NumThreadsLabel", "Energy per Instruction", "NumThreadsLabel", "Linux: Energy per Instruction vs. Threads")
scatter_plot(windows_data, "NumThreadsLabel", "Energy per Instruction", "NumThreadsLabel", "Windows: Energy per Instruction vs. Threads")
scatter_plot(linux_data, "NumThreadsLabel", "Energy per Cycle", "NumThreadsLabel", "Linux: Energy per Cycle vs. Threads")
scatter_plot(windows_data, "NumThreadsLabel", "Energy per Cycle", "NumThreadsLabel", "Windows: Energy per Cycle vs. Threads")
scatter_plot(linux_data, "NumThreadsLabel", "Cache Miss per Joule", "NumThreadsLabel", "Linux: Cache Miss per Joule vs. Threads")
scatter_plot(windows_data, "NumThreadsLabel", "Cache Miss per Joule", "NumThreadsLabel", "Windows: Cache Miss per Joule vs. Threads")

# Compare energy efficiency metrics across Linux and Windows
def compare_efficiency(linux_data, windows_data, metric, metric_name):
    linux_values = linux_data[metric].dropna()
    windows_values = windows_data[metric].dropna()
    
    print(f"\nComparing {metric_name} between Linux and Windows:")
    t_stat, p_value = ttest_ind(linux_values, windows_values, equal_var=False)
    print(f"T-statistic: {t_stat}, P-value: {p_value}")
    
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=[linux_values, windows_values], notch=True)
    plt.xticks([0, 1], ["Linux", "Windows"])
    plt.title(f"Comparison of {metric_name} between Linux and Windows")
    plt.ylabel(metric_name)
    plt.show()

# Compare energy efficiency metrics
compare_efficiency(linux_data, windows_data, "Energy per Instruction", "Energy per Instruction")
compare_efficiency(linux_data, windows_data, "Energy per Cycle", "Energy per Cycle")
compare_efficiency(linux_data, windows_data, "Cache Miss per Joule", "Cache Miss per Joule")

print("Full analysis complete.")

