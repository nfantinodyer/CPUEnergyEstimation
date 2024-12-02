#!/bin/bash

# Usage: sudo ./run_experiments.sh

# Ensure you run this script with sudo as pcm requires root privileges

# Directories
PCM_DIR="/Desktop/pcm/build/bin"
OUTPUT_DIR="$HOME/Desktop"

# Ensure the msr module is loaded
sudo modprobe msr

# Function to collect temperature data
collect_temp() {
    TEMP_OUTPUT_FILE="$1"
    SAMPLING_INTERVAL=0.5  # Adjust as needed
    TOTAL_DURATION=60      # 60 seconds
    COUNT=$(echo "$TOTAL_DURATION / $SAMPLING_INTERVAL" | bc)

    echo "DateTime,TEMP" > "$TEMP_OUTPUT_FILE"

    for ((i=0; i<COUNT; i++)); do
        DATE_TIME=$(date +"%Y-%m-%d %H:%M:%S.%N %z")
        TEMP=$(sensors -u | grep 'temp1_input' | head -1 | awk '{print $2}')
        if [ -z "$TEMP" ]; then
            TEMP="NaN"
        fi
        echo "$DATE_TIME,$TEMP" >> "$TEMP_OUTPUT_FILE"
        sleep "$SAMPLING_INTERVAL"
    done
}

# Function to run a single experiment
run_experiment() {
    STRESS_NG_CMD="$1"
    PCM_FILENAME="$2"
    TEMP_FILENAME="$3"

    echo "Starting experiment with command: $STRESS_NG_CMD"
    echo "PCM output file: $PCM_FILENAME"
    echo "Temperature output file: $TEMP_FILENAME"

    # Start temperature logging in the background
    collect_temp "$TEMP_FILENAME" &
    TEMP_PID=$!

    # Start pcm data collection in the background
    PCM_OUTPUT_FILE="$OUTPUT_DIR/$PCM_FILENAME"
    sudo "$PCM_DIR/pcm" /csv 1 60 > "$PCM_OUTPUT_FILE" 2> "$OUTPUT_DIR/pcm_errors.log" &
    PCM_PID=$!

    # Start stress-ng
    eval "$STRESS_NG_CMD"

    # Wait for background processes to finish
    wait $TEMP_PID
    wait $PCM_PID

    echo "Experiment completed: $STRESS_NG_CMD"
}

# Array of experiments
declare -a experiments=(
    # CPU Stress - All cores
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 0 --timeout 60s|Linux0Static.csv|Temp0Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 10 --timeout 60s|Linux10Static.csv|Temp10Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 20 --timeout 60s|Linux20Static.csv|Temp20Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 30 --timeout 60s|Linux30Static.csv|Temp30Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 40 --timeout 60s|Linux40Static.csv|Temp40Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 50 --timeout 60s|Linux50Static.csv|Temp50Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 60 --timeout 60s|Linux60Static.csv|Temp60Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 70 --timeout 60s|Linux70Static.csv|Temp70Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 80 --timeout 60s|Linux80Static.csv|Temp80Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 90 --timeout 60s|Linux90Static.csv|Temp90Static.csv"

    # CPU Stress - 2 threads
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 0 --timeout 60s|Linux0Static2threads.csv|Temp0Static2threads.csv"
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 30 --timeout 60s|Linux30Static2threads.csv|Temp30Static2threads.csv"
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 60 --timeout 60s|Linux60Static2threads.csv|Temp60Static2threads.csv"
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 90 --timeout 60s|Linux90Static2threads.csv|Temp90Static2threads.csv"

    # CPU Stress - 4 threads
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 0 --timeout 60s|Linux0Static4threads.csv|Temp0Static4threads.csv"
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 30 --timeout 60s|Linux30Static4threads.csv|Temp30Static4threads.csv"
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 60 --timeout 60s|Linux60Static4threads.csv|Temp60Static4threads.csv"
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 90 --timeout 60s|Linux90Static4threads.csv|Temp90Static4threads.csv"

    # CPU Stress - 6 threads
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 0 --timeout 60s|Linux0Static6threads.csv|Temp0Static6threads.csv"
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 30 --timeout 60s|Linux30Static6threads.csv|Temp30Static6threads.csv"
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 60 --timeout 60s|Linux60Static6threads.csv|Temp60Static6threads.csv"
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 90 --timeout 60s|Linux90Static6threads.csv|Temp90Static6threads.csv"

    # Memory Stress
    "stress-ng --vm 2 --vm-bytes 1G --timeout 60s|LinuxMem1.csv|TempMem1.csv"
    "stress-ng --vm 4 --vm-bytes 2G --timeout 60s|LinuxMem2.csv|TempMem2.csv"

    # I/O Stress
    "stress-ng --hdd 2 --timeout 60s|LinuxIO1.csv|TempIO1.csv"
    "stress-ng --hdd 4 --timeout 60s|LinuxIO2.csv|TempIO2.csv"
)

# Main loop to run all experiments
for exp in "${experiments[@]}"; do
    # Parse the experiment string
    IFS='|' read -r STRESS_NG_CMD PCM_FILENAME TEMP_FILENAME <<< "$exp"

    # Run the experiment
    run_experiment "$STRESS_NG_CMD" "$PCM_FILENAME" "$TEMP_FILENAME"

    # Optional: Add a short delay between experiments
    sleep 10
done

echo "All experiments completed."
