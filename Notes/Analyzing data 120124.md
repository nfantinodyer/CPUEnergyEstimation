#CSEN283
Analyzing the data gathered from [[Gathering data 120124]]
Looking into the stress-ng pcm results for the different amount of cpu stress that can affect energy usage.

![[AverageProcessorEnergyConsumptionImage.png]]This seems a bit counter intuitive so to investigate I will see about checking the data to see if something went wrong or if there is a column mismatch or if the cpu throttles performance to keep cooler.

![[AverageCPUUtilImage.png]]This makes sense.


This is to show the anomaly by itself.
![[APEC(all).png]]
![[avgFreq(all).png]]

This is the freq based on the load percentage.
![[LoadFreqImage.png]]
![[avgTemp.png]]![[OS CSEN283/Images/cpuUtil.png]]
![[freqVsTemp.png]]![[newpredic.png]]
![[energvsutil.png]]![[freqvsenergy 1.png]]

Average Energy Consumption for All Threads:
   LoadPercent  Proc Energy (Joules)
0           10              0.705062
1           20              0.983351
2           30              1.304802
3           40              1.303918
4           50              1.169284
5           60              1.012540
6           70              1.113566
7           80              0.981216
8           90              0.942394

The processor energy consumption increases from 0.705 Joules at 10% load to approximately 1.304 Joules at 30-40% load.
Beyond 40% load, the energy consumption starts to decrease, dropping to 0.942 Joules at 90% load.
This behavior seems counterintuitive, as we might expect energy consumption to continue increasing with higher loads.

So I decided to retest and regather all the data. I also added a new load of 0 percent to get a baseline.

After further refinement, and regathering of the data it was more consistant:
Average Energy Consumption for All Threads:
   LoadPercent  Proc Energy (Joules)
0            0              0.288597
1           10              0.764240
2           20              1.039056
3           30              1.148429
4           40              1.023292
5           50              0.916693
6           60              1.278048
7           70              1.046810
8           80              0.993945
9           90              0.993272

- Energy consumption increases from 0% to 30% load, peaks at 30%, and then decreases slightly at higher loads.
- The inclusion of the 0% load provides a clear baseline for idle energy consumption.

![[newCorrected.png]]

The data still seems to be incorrect. The issue lies with pcm not getting the accurate data. I am left with leaving it running for longer and removing the outliers in the data set (like how there was a 140% cpu utilization data point which is impossible, as well as 3 instances of 0 energy usage.) 

I will change the data collection time to be for 3 minutes instead of just the 30 seconds to try to just get more data so the average isn't skewed. 

I think pcm is messing up somehow, lets set it to get the data every 0.05 instead of 0.025 and set it to gather data for 2 minutes. The command I currently run is:
sudo ./pcm /csv .025 > ~/Desktop/Linux{whatever I'm currently getting}.csv 2>/dev/null

To achieve this I used:
stress-ng --cpu 0 --cpu-method matrixprod --cpu-load 0 --timeout 180s
sudo ./pcm /csv .05 -i=2400 > ~/Desktop/Linux{whatever I'm currently getting}.csv 2>/dev/null

So I changed the timeout of the stress test to be longer and the pcm test will stop no matter what at 2400 data points found which should be after 2 minutes based on
count= total_duration/delay=120/0.05=2400.

Also gathered the data consecutively instead of sporadically. Also making it a guaranteed two minutes will increase my averages to be more accurate. I gathered the data for the 10% loads for all threads as well as the 2,4,6 0,30,60,90 loads. To be able to fully retest. I hope pcm doesn't have inaccuracies in the data again.

Even after testing with the new data the temp is incorrect and there are some other inconsistencies.
![[AvgProcEngCon.png]]![[averageFreq.png]]
![[stillwrongtemp.png]]![[cpuutil 1.png]]
![[tempervsfreq.png]]![[procenergyConsumption.png]]
![[freqen.png]]
I think pcm isnt properly gathering the data properly after the 0% utilization for some reason, so I will collect a lot less data. I will attempt every 2 seconds gathering for two minutes to see if this fixes the issue.
sudo ./pcm /csv 2 -i=60 > ~/Desktop/Linux0Static.csv 2>/dev/null

Energy consumption looks more accurate
![[eeenery.png]]

![[freqqq.png]]
![[temp.png]]
![[utilll.png]]
![[cpu freq vs tmp.png]]
![[procenery.png]]
![[frwqqcons.png]]

Trying every 5 seconds 12 times. Since the previous one didn't fix the temp not being measured properly. As well as some zeros still being gathered.