#!/bin/bash

# run.sh
# Usage: ./run.sh

# Directories
PCM_DIR="/home/rob/Desktop/pcm/build/bin"
OUTPUT_DIR="/home/rob/Desktop/Data"

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Load percentages for all threads
all_thread_loads=(0 10 20 30 40 50 60 70 80 90)

# Load percentages for partial threads
partial_thread_loads=(0 30 60 90)

# Thread counts
thread_counts=(2 4 6 8)  # 8 represents 'All Threads'

# Function to run a single test configuration
run_test() {
  local num_threads=$1
  local load_percent=$2

  # Determine thread label for filenames
  if [ "$num_threads" -eq 8 ]; then
    thread_label=""
  else
    thread_label="${num_threads}threads"
  fi

  # Construct filenames
  output_filename="Linux${load_percent}Static${thread_label}.csv"
  pcm_output_file="$OUTPUT_DIR/$output_filename"
  temp_output_file="$OUTPUT_DIR/temp_${output_filename}"

  echo "Starting test: Threads=$num_threads, Load=$load_percent%, Output File=$output_filename"

  # Remove existing files if they exist
  rm -f "$pcm_output_file" "$temp_output_file"

  # Define durations
  PCM_SAMPLING_INTERVAL="1"  # Adjust as needed
  PCM_DURATION="60"  # seconds
  PCM_COUNT="$PCM_DURATION"
  STRESS_DURATION=$((PCM_DURATION * 2))  # 120 seconds

  # Build stress-ng command
  if [ "$num_threads" -eq 8 ]; then
    # All threads
    stress_cmd="stress-ng --cpu 0 --cpu-method matrixprod --cpu-load $load_percent --timeout ${STRESS_DURATION}s"
  else
    # Specific number of threads
    stress_cmd="stress-ng --cpu $num_threads --cpu-method matrixprod --cpu-load $load_percent --timeout ${STRESS_DURATION}s"
  fi

  # Start stress-ng in a new terminal via keyboard shortcut and automate typing the command
  xdotool key ctrl+alt+t
  sleep 1  # Wait for the terminal to open
  xdotool type --delay 100 "$stress_cmd"
  xdotool key Return

  # Wait a moment to ensure stress-ng has started
  sleep 2

  # Start pcm data collection in a new terminal via keyboard shortcut and automate typing the command
  xdotool key ctrl+alt+t
  sleep 1  # Wait for the terminal to open
  xdotool type --delay 100 "sudo $PCM_DIR/pcm /csv $PCM_SAMPLING_INTERVAL $PCM_COUNT > '$pcm_output_file' 2> '$OUTPUT_DIR/pcm_errors.log'"
  xdotool key Return

  # Type the root password when prompted
  sleep 1  # Wait for the password prompt
  xdotool type --delay 100 "5809"
  xdotool key Return

  # Wait for PCM_DURATION to allow pcm data collection to complete
  sleep "$PCM_DURATION"

  # Start temperature logging in a new terminal via keyboard shortcut and automate typing the command
  xdotool key ctrl+alt+t
  sleep 1  # Wait for the terminal to open
  xdotool type --delay 100 "echo 'DateTime,TEMP' > '$temp_output_file'; \
for ((i=0; i<$PCM_COUNT; i++)); do \
  DATE_TIME=\$(date '+%Y-%m-%d %H:%M:%S.%N %z'); \
  TEMP=\$(sensors -u | grep 'temp1_input' | head -1 | awk '{print \$2}'); \
  if [ -z \"\$TEMP\" ]; then TEMP='NaN'; fi; \
  echo \"\$DATE_TIME,\$TEMP\" >> '$temp_output_file'; \
  sleep $PCM_SAMPLING_INTERVAL; \
done"
  xdotool key Return

  # Wait for PCM_DURATION to allow temperature logging to complete
  sleep "$PCM_DURATION"

  # Wait for stress-ng to complete if it hasn't already
  sleep $((STRESS_DURATION - PCM_DURATION * 2))

  echo "Completed test: Threads=$num_threads, Load=$load_percent%"
}

# Main loop over thread counts and load percentages
for num_threads in "${thread_counts[@]}"; do
  if [ "$num_threads" -eq 8 ]; then
    # All threads, use all_thread_loads
    for load_percent in "${all_thread_loads[@]}"; do
      run_test "$num_threads" "$load_percent"
    done
  else
    # Partial threads, use partial_thread_loads
    for load_percent in "${partial_thread_loads[@]}"; do
      run_test "$num_threads" "$load_percent"
    done
  fi
done

echo "All tests completed."
