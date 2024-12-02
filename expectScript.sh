#!/usr/bin/expect -f

# run_pcm_expect.sh
# Usage: ./run_pcm_expect.sh

set PCM_DIR "/home/rob/Desktop/pcm/build/bin"
set PCM_SAMPLING_INTERVAL "1"
set PCM_COUNT "60"
set OUTPUT_FILE "/home/rob/Desktop/Data/Linux$env(LOAD_PERCENT)Static$env(THREAD_LABEL).csv"

# Run pcm with sudo
spawn sudo "$PCM_DIR/pcm" /csv "$PCM_SAMPLING_INTERVAL" "$PCM_COUNT"

# Log output to file
log_file -a "$OUTPUT_FILE"

# Wait for the process to complete
expect eof
