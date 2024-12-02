#!/bin/bash

# Ensure you run this script with sudo as pcm requires root privileges

# Directories
PCM_DIR="/home/rob/Desktop/pcm/build/bin"
OUTPUT_DIR="/home/rob/Desktop/Data"

# Ensure the msr module is loaded
sudo modprobe msr

# Function to collect temperature data and output to stdout
collect_temp() {
    SAMPLING_INTERVAL=1  # Same as PCM sampling interval
    TOTAL_DURATION=60    # 60 seconds
    COUNT=$((TOTAL_DURATION / SAMPLING_INTERVAL))

    for ((i=0; i<COUNT; i++)); do
        DATE_TIME=$(date +"%Y-%m-%d %H:%M:%S.%N %z")
        TEMP=$(sensors -u | grep 'temp1_input' | head -1 | awk '{print $2}')
        if [ -z "$TEMP" ]; then
            TEMP="NaN"
        fi
        echo "$TEMP"
        sleep "$SAMPLING_INTERVAL"
    done
}

# Function to run a single experiment
run_experiment() {
    STRESS_NG_CMD="$1"
    PCM_FILENAME="$2"

    echo "Starting experiment with command: $STRESS_NG_CMD"
    echo "PCM output file: $PCM_FILENAME"

    # Start PCM data collection and merge with temperature data
    PCM_OUTPUT_FILE="$OUTPUT_DIR/$PCM_FILENAME"
    
    # Start stress-ng in the background
    eval "$STRESS_NG_CMD" &

    # Collect PCM data and merge with temperature
    sudo "$PCM_DIR/pcm" /csv 1 -i=60 2> "$OUTPUT_DIR/pcm_errors.log" | \
    paste -d ',' - <(collect_temp) > "$PCM_OUTPUT_FILE"

    # Wait for stress-ng to finish
    wait

    echo "Experiment completed: $STRESS_NG_CMD"
}

# Array of experiments
declare -a experiments=(
    # CPU Stress - All cores
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 0 --timeout 60s|Linux0Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 10 --timeout 60s|Linux10Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 20 --timeout 60s|Linux20Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 30 --timeout 60s|Linux30Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 40 --timeout 60s|Linux40Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 50 --timeout 60s|Linux50Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 60 --timeout 60s|Linux60Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 70 --timeout 60s|Linux70Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 80 --timeout 60s|Linux80Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 90 --timeout 60s|Linux90Static.csv"

    # CPU Stress - 2 threads
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 0 --timeout 60s|Linux0Static2threads.csv"
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 30 --timeout 60s|Linux30Static2threads.csv"
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 60 --timeout 60s|Linux60Static2threads.csv"
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 90 --timeout 60s|Linux90Static2threads.csv"

    # CPU Stress - 4 threads
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 0 --timeout 60s|Linux0Static4threads.csv"
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 30 --timeout 60s|Linux30Static4threads.csv"
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 60 --timeout 60s|Linux60Static4threads.csv"
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 90 --timeout 60s|Linux90Static4threads.csv"

    # CPU Stress - 6 threads
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 0 --timeout 60s|Linux0Static6threads.csv"
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 30 --timeout 60s|Linux30Static6threads.csv"
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 60 --timeout 60s|Linux60Static6threads.csv"
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 90 --timeout 60s|Linux90Static6threads.csv"

    # Memory Stress
    "stress-ng --vm 2 --vm-bytes 1G --timeout 60s|LinuxMem1.csv"
    "stress-ng --vm 4 --vm-bytes 2G --timeout 60s|LinuxMem2.csv"

    # I/O Stress
    "stress-ng --hdd 2 --timeout 60s|LinuxIO1.csv"
    "stress-ng --hdd 4 --timeout 60s|LinuxIO2.csv"
)

# Main loop to run all experiments
for exp in "${experiments[@]}"; do
    # Parse the experiment string
    IFS='|' read -r STRESS_NG_CMD PCM_FILENAME <<< "$exp"

    # Run the experiment
    run_experiment "$STRESS_NG_CMD" "$PCM_FILENAME"

    # Optional: Add a short delay between experiments
    sleep 1
done

echo "All experiments completed."
