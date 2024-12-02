#!/bin/bash

# Ensure the script is run with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit
fi

# Load the msr module
modprobe msr

# Variables
PCM_DIR="/Desktop/pcm/build/bin"
OUTPUT_DIR="$HOME/Desktop"
PCM_EXEC="$PCM_DIR/pcm"
SAMPLING_INTERVAL="0.05"
TOTAL_DURATION="60"  # In seconds
PCM_COUNT=$(echo "$TOTAL_DURATION / $SAMPLING_INTERVAL" | bc)

# Ensure PCM directory exists
if [ ! -d "$PCM_DIR" ]; then
  echo "PCM directory not found at $PCM_DIR"
  exit 1
fi

# Ensure PCM executable exists
if [ ! -f "$PCM_EXEC" ]; then
  echo "PCM executable not found at $PCM_EXEC"
  exit 1
fi

# Create an array of test configurations
declare -a tests=(
  # CPU stress tests (each core/thread)
  "stress-ng --cpu 1 --timeout ${TOTAL_DURATION}s" "LinuxCPUTest1Thread.csv"
  "stress-ng --cpu 2 --timeout ${TOTAL_DURATION}s" "LinuxCPUTest2Threads.csv"
  "stress-ng --cpu 3 --timeout ${TOTAL_DURATION}s" "LinuxCPUTest3Threads.csv"
  "stress-ng --cpu 4 --timeout ${TOTAL_DURATION}s" "LinuxCPUTest4Threads.csv"
  # Memory stress tests
  "stress-ng --vm 2 --vm-bytes 1G --timeout ${TOTAL_DURATION}s" "LinuxMemTest2VM.csv"
  "stress-ng --vm 4 --vm-bytes 2G --timeout ${TOTAL_DURATION}s" "LinuxMemTest4VM.csv"
  # I/O stress tests
  "stress-ng --hdd 2 --timeout ${TOTAL_DURATION}s" "LinuxIOTest2HDD.csv"
  "stress-ng --hdd 4 --timeout ${TOTAL_DURATION}s" "LinuxIOTest4HDD.csv"
  # Static load on all cores
  "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 10 --timeout ${TOTAL_DURATION}s" "Linux10Static.csv"
  "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 20 --timeout ${TOTAL_DURATION}s" "Linux20Static.csv"
  "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 30 --timeout ${TOTAL_DURATION}s" "Linux30Static.csv"
  "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 40 --timeout ${TOTAL_DURATION}s" "Linux40Static.csv"
  "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 50 --timeout ${TOTAL_DURATION}s" "Linux50Static.csv"
  "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 60 --timeout ${TOTAL_DURATION}s" "Linux60Static.csv"
  "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 70 --timeout ${TOTAL_DURATION}s" "Linux70Static.csv"
  "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 80 --timeout ${TOTAL_DURATION}s" "Linux80Static.csv"
  "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 90 --timeout ${TOTAL_DURATION}s" "Linux90Static.csv"
  "stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 0 --timeout ${TOTAL_DURATION}s"  "Linux0Static.csv"
  # Static load on 2 threads
  "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 90 --timeout ${TOTAL_DURATION}s" "Linux90Static2Threads.csv"
  "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 60 --timeout ${TOTAL_DURATION}s" "Linux60Static2Threads.csv"
  "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 30 --timeout ${TOTAL_DURATION}s" "Linux30Static2Threads.csv"
  "stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 0 --timeout ${TOTAL_DURATION}s"  "Linux0Static2Threads.csv"
  # Static load on 4 threads
  "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 90 --timeout ${TOTAL_DURATION}s" "Linux90Static4Threads.csv"
  "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 60 --timeout ${TOTAL_DURATION}s" "Linux60Static4Threads.csv"
  "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 30 --timeout ${TOTAL_DURATION}s" "Linux30Static4Threads.csv"
  "stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 0 --timeout ${TOTAL_DURATION}s"  "Linux0Static4Threads.csv"
  # Static load on 6 threads
  "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 90 --timeout ${TOTAL_DURATION}s" "Linux90Static6Threads.csv"
  "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 60 --timeout ${TOTAL_DURATION}s" "Linux60Static6Threads.csv"
  "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 30 --timeout ${TOTAL_DURATION}s" "Linux30Static6Threads.csv"
  "stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 0 --timeout ${TOTAL_DURATION}s"  "Linux0Static6Threads.csv"
)

# Function to collect temperature data
collect_temp() {
  local TEMP_OUTPUT_FILE="$1"
  local SAMPLING_INTERVAL="2"  # Adjust as needed
  local COUNT=$(echo "$TOTAL_DURATION / $SAMPLING_INTERVAL" | bc)
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

# Main loop to run tests
for ((i=0; i<${#tests[@]}; i+=2)); do
  STRESS_CMD="${tests[i]}"
  OUTPUT_FILENAME="${tests[i+1]}"
  PCM_OUTPUT_FILE="$OUTPUT_DIR/$OUTPUT_FILENAME"
  TEMP_OUTPUT_FILE="$OUTPUT_DIR/Temp_${OUTPUT_FILENAME}"

  echo "Running test: $STRESS_CMD"
  echo "PCM data will be saved to: $PCM_OUTPUT_FILE"
  echo "Temperature data will be saved to: $TEMP_OUTPUT_FILE"

  # Remove existing output files if they exist
  rm -f "$PCM_OUTPUT_FILE" "$TEMP_OUTPUT_FILE"

  # Navigate to PCM directory
  cd "$PCM_DIR"

  # Start temperature collection in the background
  collect_temp "$TEMP_OUTPUT_FILE" &

  # Start PCM data collection in the background
  sudo ./pcm /csv "$SAMPLING_INTERVAL" "$PCM_COUNT" > "$PCM_OUTPUT_FILE" 2>/dev/null &

  # Start stress-ng
  eval "$STRESS_CMD" &

  # Wait for stress-ng to complete
  wait %3  # Wait for the stress-ng process

  # Kill any remaining background processes (pcm and temp collection)
  kill %1 %2 2>/dev/null

  echo "Test completed: $STRESS_CMD"
  echo "---------------------------------------"
done

echo "All tests completed."
