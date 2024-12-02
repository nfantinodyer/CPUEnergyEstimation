#!/bin/bash

# Ensure the msr module is loaded
sudo modprobe msr

# Directories
PCM_DIR="$HOME/Desktop/pcm/build/bin"
OUTPUT_DIR="$HOME/Desktop"

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

# Export the function so it's available in subshells
export -f collect_temp

# Function to run a single experiment
run_experiment() {
    STRESS_NG_CMD="$1"
    PCM_FILENAME="$2"
    TEMP_FILENAME="$3"

    echo "Starting experiment with command: $STRESS_NG_CMD"
    echo "PCM output file: $PCM_FILENAME"
    echo "Temperature output file: $TEMP_FILENAME"

    # Start temperature logging in the background
    bash -c "collect_temp '$OUTPUT_DIR/$TEMP_FILENAME'" &
    TEMP_PID=$!

    # Start pcm data collection in the background
    PCM_OUTPUT_FILE="$OUTPUT_DIR/$PCM_FILENAME"
    (
        cd "$PCM_DIR" || exit
        sudo ./pcm /csv 1 60 > "$PCM_OUTPUT_FILE" 2>> "$OUTPUT_DIR/pcm_errors.log"
    ) &
    PCM_PID=$!

    # Start stress-ng
    eval "$STRESS_NG_CMD"

    # Wait for background processes to finish
    wait $TEMP_PID
    wait $PCM_PID

    # Adjust ownership of the pcm output file
    sudo chown "$USER":"$USER" "$PCM_OUTPUT_FILE"

    echo "Experiment completed: $STRESS_NG_CMD"
}

# Array of experiments
declare -a experiments=(
    # CPU Stress - All cores
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 0 --timeout 60s|Linux0Static.csv|Temp0Static.csv"
    # Include other experiments as needed
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
