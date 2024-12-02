#!/bin/bash

# Usage: ./collect_temp.sh output_filename.csv sampling_interval total_duration

OUTPUT_FILE="$1"
SAMPLING_INTERVAL="$2"
TOTAL_DURATION="$3"

if [ -z "$OUTPUT_FILE" ] || [ -z "$SAMPLING_INTERVAL" ] || [ -z "$TOTAL_DURATION" ]; then
    echo "Usage: ./collect_temp.sh output_filename.csv sampling_interval total_duration"
    exit 1
fi

# Calculate the number of samples
COUNT=$(echo "$TOTAL_DURATION / $SAMPLING_INTERVAL" | bc)

echo "DateTime,TEMP" > "$OUTPUT_FILE"

for ((i=0; i<COUNT; i++)); do
    DATE_TIME=$(date +"%Y-%m-%d %H:%M:%S.%N %z")
    TEMP=$(sensors -u | grep 'temp1_input' | head -1 | awk '{print $2}')
    if [ -z "$TEMP" ]; then
        TEMP="NaN"
    fi
    echo "$DATE_TIME,$TEMP" >> "$OUTPUT_FILE"
    sleep "$SAMPLING_INTERVAL"
done
