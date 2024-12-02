#!/bin/bash

# automate_data_collection.sh
# Usage: sudo ./automate_data_collection.sh

# Ensure the script is run with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root using sudo."
  exit
fi

# Directories
PCM_DIR="/Desktop/pcm/build/bin"
OUTPUT_DIR="/Desktop/DataCollection"
TEMP_SCRIPT_PATH="/path/to/collect_temp.sh"  # Update this path to where your collect_temp.sh script is located

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

  # Calculate sampling interval and count for pcm
  PCM_SAMPLING_INTERVAL="0.05"  # Adjust as needed
  PCM_DURATION="60"  # seconds
  PCM_COUNT=$(echo "$PCM_DURATION / $PCM_SAMPLING_INTERVAL" | bc)

  # Build stress-ng command
  if [ "$num_threads" -eq 8 ]; then
    # All threads
    stress_cmd="stress-ng --cpu 0 --cpu-method matrixprod --cpu-load $load_percent --timeout ${PCM_DURATION}s"
  else
    # Specific number of threads
    stress_cmd="stress-ng --cpu $num_threads --cpu-method matrixprod --cpu-load $load_percent --timeout ${PCM_DURATION}s"
  fi

  # Start temperature logging in the background
  bash "$TEMP_SCRIPT_PATH" "$temp_output_file" "$PCM_SAMPLING_INTERVAL" "$PCM_DURATION" &
  temp_pid=$!

  # Start pcm data collection in the background
  cd "$PCM_DIR"
  sudo ./pcm /csv "$PCM_SAMPLING_INTERVAL" "$PCM_COUNT" > "$pcm_output_file" 2>/dev/null &
  pcm_pid=$!

  # Start stress-ng (foreground)
  eval "$stress_cmd"

  # Wait for background processes to finish
  wait $temp_pid
  wait $pcm_pid

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
