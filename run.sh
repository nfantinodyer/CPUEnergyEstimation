#!/bin/bash

# run.sh
# Usage: sudo ./run.sh

# Ensure the script is run with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root using sudo."
  exit
fi

# Export environment variables for GUI applications
export DISPLAY=:0
export XAUTHORITY=/home/rob/.Xauthority

# Directories
PCM_DIR="Desktop/pcm/build/bin"
OUTPUT_DIR="Desktop/Data"

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
  pcm_error_log="$OUTPUT_DIR/pcm_errors.log"

  echo "Starting test: Threads=$num_threads, Load=$load_percent%, Output File=$output_filename"

  # Remove existing files if they exist
  rm -f "$pcm_output_file" "$temp_output_file"

  # Calculate sampling interval and count for pcm
  PCM_SAMPLING_INTERVAL="1"  # Adjust as needed
  PCM_DURATION="60"  # seconds
  PCM_COUNT="60"

  # Build stress-ng command
  if [ "$num_threads" -eq 8 ]; then
    # All threads
    stress_cmd="stress-ng --cpu 0 --cpu-method matrixprod --cpu-load $load_percent --timeout ${PCM_DURATION}s"
  else
    # Specific number of threads
    stress_cmd="stress-ng --cpu $num_threads --cpu-method matrixprod --cpu-load $load_percent --timeout ${PCM_DURATION}s"
  fi

  # Start pcm data collection
  xterm -hold -e bash -c "
    echo 'Starting pcm data collection...';
    sudo "$PCM_DIR/pcm" /csv "$PCM_SAMPLING_INTERVAL" "$PCM_COUNT" > "$pcm_output_file" 2> "$pcm_error_log";
    echo 'pcm data collection completed.';
  "&
  pcm_pid=$!

  # Start temperature logging in a new xterm window
  xterm -hold -e bash -c "
    echo 'Starting temperature logging...';
    SAMPLING_INTERVAL='$PCM_SAMPLING_INTERVAL';
    TOTAL_DURATION='$PCM_DURATION';
    COUNT=\$(echo \"\$TOTAL_DURATION / \$SAMPLING_INTERVAL\" | bc);
    echo 'DateTime,TEMP' > '$temp_output_file';
    for ((i=0; i<COUNT; i++)); do
        DATE_TIME=\$(date '+%Y-%m-%d %H:%M:%S.%N %z');
        TEMP=\$(sensors -u | grep 'temp1_input' | head -1 | awk '{print \$2}');
        if [ -z \"\$TEMP\" ]; then
            TEMP='NaN';
        fi
        echo \"\$DATE_TIME,\$TEMP\" >> '$temp_output_file';
        sleep \$SAMPLING_INTERVAL;
    done;
    echo 'Temperature logging completed.';
    read -p 'Press Enter to close...';
  " &

  temp_pid=$!


  # Start stress-ng in a new xterm window
  xterm -hold -e bash -c "
    echo 'Starting stress-ng...';
    sudo $stress_cmd;
    echo 'stress-ng completed.';
    read -p 'Press Enter to close...';
  " &

  stress_pid=$!



  # Wait for the duration of the test plus a buffer
  sleep $(($PCM_DURATION + 5))

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
