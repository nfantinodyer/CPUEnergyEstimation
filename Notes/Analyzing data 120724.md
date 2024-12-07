#CSEN283 

I installed the same debian os onto my main pc. My main pc has a i7-13700K and the PC I was using for the windows 10 was a i7-7700K. This will show the differences between the generations.

I ran into an issue with my current scripts after I got the new data since the pcm csv output had 646 columns for the 13700K compared to the 272 of the 7700K. So I readjusted my CorrectDataLinux.ps1.  I also added the CPU column into my Linux Analyze script so that I can compare easier. Here are the results:

![[EnergyConsBetweenNewCPU.png]]![[TempComparisonNewOldCPU.png]]
![[EnerConsUtilNewOld.png]]![[EnerConsByFreq.png]]

![[oldcpuheatmap.png]]![[newcpuheatmap.png]]

![[EnergyConsByThread.png]]

![[TempByThread.png]]