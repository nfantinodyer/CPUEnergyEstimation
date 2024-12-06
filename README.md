# CPU Performance Analysis: Addressing Inaccuracies in Monitoring Tools
## Overview
  This project investigates inaccuracies in CPU performance and energy consumption metrics collected using various tools, including Intel PCM, Linux sensors, and stress-testing utilities like stress-ng and HeavyLoad. The analysis compares results across Windows and Linux environments, identifying tool limitations, exploring mitigation strategies, and evaluating energy efficiency.

## Features
- Automated data collection for CPU performance metrics and temperature readings for Linux.
- Merged, cleaned, and preprocessed datasets ready for in-depth analysis.
- Visualizations, including scatter plots and heatmaps, to highlight trends and anomalies.
- Statistical analysis comparing Windows and Linux systems under varying loads and thread configurations.

## Setup and Installation
Prerequisites
  - Linux or Windows 10.

Install and follow directions from:
https://github.com/intel/pcm

### For Windows Intel Monitor I followed these steps
#### Installing PCM
https://github.com/intel/pcm

>git clone --recursive https://github.com/intel/pcm
>cd pcm
>git submodule update --init --recursive
>mkdir build
>cd build

Install cmake: https://cmake.org/download/

>cmake ..
>cmake --build .
>cmake --build . --parallel
>cmake --build . --config Release

https://github.com/intel/pcm/blob/master/doc/WINDOWS_HOWTO.md

#### To run PCM.exe
Disable Secure Boot first in BIOS
bcdedit /set testsigning on

Only allow signed:
bcdedit /set testsigning off

#### For perfmon:
in the pcm dir
>cmake --build build --target pcm-lib --config Release
>This will generate `PCM-Service.exe` in the same directory as other build outputs (e.g., `C:\Users\2013r\pcm\build\bin\Release`

Copy the following files into a `PCM` sub-directory in `C:\Program Files`:
- `PCM-Service.exe`
- `PCM-Service.exe.config`
- `pcm-lib.dll`

> cd "C:\Program Files\PCM"
> "PCM-Service.exe" -Install

#### Starting perfmon 
> cd "C:\Program Files\PCM"
> net start pcmservice
- Open **Performance Monitor** (Perfmon) by typing `perfmon` in the Start menu and pressing Enter.
- In Perfmon, add new counters by clicking the green "+" icon.
- You should see new counters starting with `PCM*`, which are provided by the `PCM-Service.exe`.

Run the dataOut.ps1 file to get data and put it into a csv. It runs for 5 seconds and gets data very 250 milliseconds.

#### Just straight output
Turns out you can just do
>pcm.exe /csv 1 > output.csv

This will output to the csv every 1 second. You can also do every .1 seconds and that's what i have it on currently:
>pcm.exe /csv .1 > output.csv

### For Linux I followed these steps
I'll be using Desbian edu 12.8.0 amd 64 netinst since it's primarily for Windows Intel CPUs. It'll be loaded onto the same drive as windows on the main testing PC so I can test on the same CPU. 

#### Be sure to install
sudo apt-get update
sudo apt-get install stress-ng gcc g++ libacl1-dev libaio-dev libapparmor-dev libatomic1 libattr1-dev libbsd-dev libcap-dev libeigen3-dev libgbm-dev libcrypt-dev libglvnd-dev libipsec-mb-dev libjpeg-dev libjudy-dev libkeyutils-dev libkmod-dev libmd-dev libmpfr-dev libsctp-dev libxxhash-dev zlib1g-dev cmake

Go to the bin directory in the build one.
If you want to run it yourself manually you can do:
>sudo modprobe msr
> sudo ./pcm /csv .025 > ~/Desktop/LinuxOutput.csv 2>/dev/null

But if you want to have it automatically run expeiments you can run my mergingTempRun.sh file. It will output everything into the Data folder on your desktop:

You will need to edit the file to tell it where you installed pcm as well as where you need the output to go.
chmod +x mergingTempRun.sh

sudo ./mergingTempRun.sh

## Some Notes
All of my notes throughout this project are under the Notes directory in that same repository. Following the steps on the readme you can install pcm and run it on your pc as well. Initially I used Influx to try to push my data to which is what got me started with reformatting the csv files into the format influx needed, but I ended up still using that CorrectData script throughout because I liked the consistency. For Linux I was able to automate the data collection using the mergingTempRun.sh since the amount of experiments I was running was tedious to run by hand. However for windows I wasn't given the opportunity to edit the amount of load on the cpu as well as some other things that I could do on linux so the data collection was minimal in comparison.
