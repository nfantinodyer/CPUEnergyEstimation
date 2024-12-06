#CSEN283
## Installing PCM
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


### To run PCM.exe
Disable Secure Boot first in BIOS
bcdedit /set testsigning on

Only allow signed:
bcdedit /set testsigning off


### For perfmon:
in the pcm dir
>cmake --build build --target pcm-lib --config Release
>This will generate `PCM-Service.exe` in the same directory as other build outputs (e.g., `C:\Users\2013r\pcm\build\bin\Release`

Copy the following files into a `PCM` sub-directory in `C:\Program Files`:
- `PCM-Service.exe`
- `PCM-Service.exe.config`
- `pcm-lib.dll`

> cd "C:\Program Files\PCM"
> "PCM-Service.exe" -Install

### Starting perfmon 
> cd "C:\Program Files\PCM"
> net start pcmservice
- Open **Performance Monitor** (Perfmon) by typing `perfmon` in the Start menu and pressing Enter.
- In Perfmon, add new counters by clicking the green "+" icon.
- You should see new counters starting with `PCM*`, which are provided by the `PCM-Service.exe`.

Run the dataOut.ps1 file to get data and put it into a csv. It runs for 5 seconds and gets data very 250 milliseconds.


### Just straight output

^7aaa98

Turns out you can just do
>pcm.exe /csv 1 > output.csv

This will output to the csv every 1 second. You can also do every .1 seconds and that's what i have it on currently:
>pcm.exe /csv .1 > output.csv

^bf74da

