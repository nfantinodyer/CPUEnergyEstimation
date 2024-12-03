#!/bin/bash

# Ensure you run this script with sudo as pcm requires root privileges

# Directories
PCM_DIR="/home/rob/Desktop/pcm/build/bin"
OUTPUT_DIR="/home/rob/Desktop/Data"

SAMPLING_INTERVAL=1  # Same as PCM sampling interval
TOTAL_DURATION=30    # 30 seconds

# Ensure the msr module is loaded
sudo modprobe msr

# Function to collect temperature data and output to stdout
collect_temp() {
    echo "Signal"
    echo "Temperature"

    COUNT=$((TOTAL_DURATION / SAMPLING_INTERVAL))

    for ((i=0; i<=COUNT; i++)); do
        # Use `sensors` to fetch the temperature
        TEMP=$(sensors -u | grep -E 'temp[1-9]_input' | head -1 | awk '{print $2}')
        if [ -z "$TEMP" ]; then
            TEMP="NaN"
        else
            # Format the temperature to three decimal places
            TEMP=$(awk "BEGIN {printf \"%.3f\", $TEMP}")
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

    # Start stress-ng in the background
    eval "$STRESS_NG_CMD" &

    # Start PCM data collection and redirect output to a temporary file
    PCM_TEMP_FILE="$(mktemp)"
    sudo "$PCM_DIR/pcm" /csv "$SAMPLING_INTERVAL" -i="$TOTAL_DURATION" 2> "$OUTPUT_DIR/pcm_errors.log" > "$PCM_TEMP_FILE" &

    # Collect temperature data and redirect output to a temporary file
    TEMP_TEMP_FILE="$(mktemp)"
    collect_temp > "$TEMP_TEMP_FILE" &

    # Wait for both background processes to finish
    wait

    # Merge PCM data and temperature data
    PCM_LINES=$(wc -l < "$PCM_TEMP_FILE")
    TEMP_LINES=$(wc -l < "$TEMP_TEMP_FILE")

    # Ensure both files have the same number of lines
    if [ "$PCM_LINES" -ne "$TEMP_LINES" ]; then
        echo "Mismatch in number of lines between PCM and temperature data."
        echo "PCM lines: $PCM_LINES, TEMP lines: $TEMP_LINES"
        echo "Adjusting temperature data to match PCM data."

        # Calculate the difference in lines
        LINE_DIFF=$((PCM_LINES - TEMP_LINES))

        # Add empty lines to TEMP_TEMP_FILE if necessary
        if [ "$LINE_DIFF" -gt 0 ]; then
            for ((i=0; i<LINE_DIFF; i++)); do
                echo "" >> "$TEMP_TEMP_FILE"
            done
        fi
    fi

    # Merge the two files
    paste -d ',' "$PCM_TEMP_FILE" "$TEMP_TEMP_FILE" > "$OUTPUT_DIR/$PCM_FILENAME"

    # Remove temporary files
    rm "$PCM_TEMP_FILE" "$TEMP_TEMP_FILE"

    # Wait for stress-ng to finish
    wait

    echo "Experiment completed: $STRESS_NG_CMD"
}

# Array of experiments
declare -a experiments=(
    # CPU Stress - All cores
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 0 --timeout $TOTAL_DURATION|Linux0Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 10 --timeout $TOTAL_DURATION|Linux10Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 20 --timeout $TOTAL_DURATION|Linux20Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 30 --timeout $TOTAL_DURATION|Linux30Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 40 --timeout $TOTAL_DURATION|Linux40Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 50 --timeout $TOTAL_DURATION|Linux50Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 60 --timeout $TOTAL_DURATION|Linux60Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 70 --timeout $TOTAL_DURATION|Linux70Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 80 --timeout $TOTAL_DURATION|Linux80Static.csv"
    "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 90 --timeout $TOTAL_DURATION|Linux90Static.csv"

    # CPU Stress - 2 threads
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 0 --timeout $TOTAL_DURATION|Linux0Static2threads.csv"
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 10 --timeout $TOTAL_DURATION|Linux10Static2threads.csv"
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 20 --timeout $TOTAL_DURATION|Linux20Static2threads.csv"
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 30 --timeout $TOTAL_DURATION|Linux30Static2threads.csv"
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 40 --timeout $TOTAL_DURATION|Linux40Static2threads.csv"
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 50 --timeout $TOTAL_DURATION|Linux50Static2threads.csv"
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 60 --timeout $TOTAL_DURATION|Linux60Static2threads.csv"
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 70 --timeout $TOTAL_DURATION|Linux70Static2threads.csv"
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 80 --timeout $TOTAL_DURATION|Linux80Static2threads.csv"
    "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 90 --timeout $TOTAL_DURATION|Linux90Static2threads.csv"

    # CPU Stress - 4 threads
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 0 --timeout $TOTAL_DURATION|Linux0Static4threads.csv"
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 10 --timeout $TOTAL_DURATION|Linux10Static4threads.csv"
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 20 --timeout $TOTAL_DURATION|Linux20Static4threads.csv"
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 30 --timeout $TOTAL_DURATION|Linux30Static4threads.csv"
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 40 --timeout $TOTAL_DURATION|Linux40Static4threads.csv"
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 50 --timeout $TOTAL_DURATION|Linux50Static4threads.csv"
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 60 --timeout $TOTAL_DURATION|Linux60Static4threads.csv"
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 70 --timeout $TOTAL_DURATION|Linux70Static4threads.csv"
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 80 --timeout $TOTAL_DURATION|Linux80Static4threads.csv"
    "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 90 --timeout $TOTAL_DURATION|Linux90Static4threads.csv"

    # CPU Stress - 6 threads
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 0 --timeout $TOTAL_DURATION|Linux0Static6threads.csv"
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 10 --timeout $TOTAL_DURATION|Linux10Static6threads.csv"
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 20 --timeout $TOTAL_DURATION|Linux20Static6threads.csv"
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 30 --timeout $TOTAL_DURATION|Linux30Static6threads.csv"
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 40 --timeout $TOTAL_DURATION|Linux40Static6threads.csv"
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 50 --timeout $TOTAL_DURATION|Linux50Static6threads.csv"
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 60 --timeout $TOTAL_DURATION|Linux60Static6threads.csv"
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 70 --timeout $TOTAL_DURATION|Linux70Static6threads.csv"
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 80 --timeout $TOTAL_DURATION|Linux80Static6threads.csv"
    "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 90 --timeout $TOTAL_DURATION|Linux90Static6threads.csv"
    

    # Memory Stress
    "stress-ng --vm 2 --vm-bytes 1G --timeout $TOTAL_DURATION|LinuxMem1.csv"
    "stress-ng --vm 4 --vm-bytes 2G --timeout $TOTAL_DURATION|LinuxMem2.csv"

    # I/O Stress
    "stress-ng --hdd 2 --timeout $TOTAL_DURATION|LinuxIO1.csv"
    "stress-ng --hdd 4 --timeout $TOTAL_DURATION|LinuxIO2.csv"
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
