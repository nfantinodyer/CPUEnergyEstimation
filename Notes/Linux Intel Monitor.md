#CSEN283
I'll be using Desbian edu 12.8.0 amd 64 netinst since it's primarily for Windows Intel CPUs. It'll be loaded onto the same drive as windows on the main testing PC so I can test on the same CPU. 
Sign in is rob and nfd

Follow the steps and before running 
>bin/pcm

Be sure to run
>sudo modprobe msr
>sudo bin/pcm

This is assuming you are in the build directory.

Then to output to a file do:
> cd bin
> sudo ./pcm /csv .025 > ~/Desktop/LinuxOutput.csv 2>/dev/null