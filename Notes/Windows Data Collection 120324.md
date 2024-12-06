#CSEN283 
Using Heavy Load to do similar things to stress-ng. I'm only able to specify threads not the actual load in windows.

there are options for using 1 and I may test that way. But for now just 2,4,6,8.

CPU Options Used logical processors: 2->8
Thread options: Below Normal

cd C:\Program Files (x86)\PCM
pcm.exe -r /csv 1 -i=30 > "C:\Users\Rob\Desktop\Data\Windows2threads.csv"
pcm.exe -r /csv 1 -i=30 > "C:\Users\Rob\Desktop\Data\Windows4threads.csv"
pcm.exe -r /csv 1 -i=30 > "C:\Users\Rob\Desktop\Data\Windows6threads.csv"
pcm.exe -r /csv 1 -i=30 > "C:\Users\Rob\Desktop\Data\Windows8threads.csv"


Ran memory tests at 1000 mb and 2000 mb at 1/5\*memory to try to emulate the 2 or 4 workers for 1G and 2G of stress-ng. WindowsMem1.csv and 2.

Did the hdd test on the test file test, for 2g and 4g at the 1/5\*size to try to test similar to the stress-ng. WindowsIO1.csv and 2.