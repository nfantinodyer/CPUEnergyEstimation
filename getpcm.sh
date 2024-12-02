#!/bin/bash

# test_pcm.sh
# Usage: sudo ./test_pcm.sh

# Ensure the script is run with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root using sudo."
  exit
fi

# Directory where pcm is located
PCM_DIR="/Desktop/pcm/build/bin"

# Output file
OUTPUT_FILE="pcm_test_output.csv"

# Remove existing output file if it exists
rm -f "$OUTPUT_FILE"

# Sampling interval and duration
SAMPLING_INTERVAL="0.05"  # Adjust as needed
DURATION="60"  # seconds
COUNT=$(echo "$DURATION / $SAMPLING_INTERVAL" | bc)

# Run pcm
cd "$PCM_DIR"
sudo ./pcm /csv "$SAMPLING_INTERVAL" "$COUNT" > "$OUTPUT_FILE" 2>/dev/null

echo "pcm test completed. Output saved to $OUTPUT_FILE"