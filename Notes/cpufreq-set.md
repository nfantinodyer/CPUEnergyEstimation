#CSEN283

sudo apt-get install cpufrequtils
#### **Usage:**
- **Set Specific Frequency for All Cores:**
    `sudo cpufreq-set -r -f <frequency>`
    Set all cores to 2.0GHz:
    `sudo cpufreq-set -r -f 2.0GHz`
    
- **Set Scaling Governor:**
    You can set the CPU governor to control how frequencies are scaled.
    - **Available Governors:**
        cpufreq-info -g`
        
    - **Set Governor:**
        `sudo cpufreq-set -r -g <governor>`
        Set to performance governor (max frequency):
        sudo cpufreq-set -r -g performance`
        
        Set to powersave governor (min frequency):
        sudo cpufreq-set -r -g powersave`
        
- **List Available Frequencies:**
    cpufreq-info -l