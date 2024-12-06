#CSEN283 
### On linux
Used [[stress-ng]] and then ran the pcm for about 30 seconds or so for each. I had firefox open on the my git repo to be able to upload quicker. 

cd Desktop/pcm/build/bin
sudo modprobe msr
sudo ./pcm /csv .025 > ~/Desktop/Linux{whateverProcessImDoing}.csv 2>/dev/null

This tests each core (but really each thread)
stress-ng --cpu 0 --timeout 60s

These are per thread
stress-ng --cpu 1 --timeout 60s
stress-ng --cpu 2 --timeout 60s
stress-ng --cpu 3 --timeout 60s
stress-ng --cpu 4 --timeout 60s

This is to test memory stress
stress-ng --vm 2 --vm-bytes 1G --timeout 60s
stress-ng --vm 4 --vm-bytes 2G --timeout 60s

This is to test I/O stress
stress-ng --hdd 2 --timeout 60s
stress-ng --hdd 4 --timeout 60s

To test static load on all cores
stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 10 --timeout 60s
stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 20 --timeout 60s
stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 30 --timeout 60s
stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 40 --timeout 60s
stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 50 --timeout 60s
stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 60 --timeout 60s
stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 70 --timeout 60s
stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 80 --timeout 60s
stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 90 --timeout 60s
stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 0 --timeout 60s

To test static on 1 core (2 threads)
stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 90 --timeout 60s
stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 60 --timeout 60s
stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 30 --timeout 60s
stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 0 --timeout 60s

To test on 4 threads
stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 30 --timeout 60s
stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 60 --timeout 60s
stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 90 --timeout 60s
stress-ng --cpu 4 --cpu-method matrixprod --cpu-load 0 --timeout 60s

To test on 6 threads
stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 90 --timeout 60s
stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 60 --timeout 60s
stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 30 --timeout 60s
stress-ng --cpu 6 --cpu-method matrixprod --cpu-load 0 --timeout 60s


To try to not have incorrect data points:
stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 0 --timeout 180s
sudo ./pcm /csv .05 -i=2400 > ~/Desktop/Linux0Static.csv 2>/dev/null

Repeated that for every 10 for the static load.

Since that didn't fix the issue, I've further adjusted:
sudo ./pcm /csv 2 -i=60 > ~/Desktop/Linux0Static.csv 2>/dev/null

trying every 5 seconds 12 times.

tried to make a script to automatically run tests but pcm doesnt like it, and refuses to report data on time. Tried Expect, gnome, and xdotool. it was all due to not having -i={num}...................................... sigh......................