#CSEN283 

Today I've been perfecting my automation script to gather the data and I went back to running it the background with the -i= part added. 

I'm merging the temp data with the pcm output in a new temperature column.

its called mergingTempRun.sh

To compile run: 
chmod +x mergingTempRun.sh

Then 
sudo ./mergingTempRun.sh


The automation runs for 2 minutes and at the end of each test it outputs that there is a line mismatch of PCM:121 and TEMP:123 so im not sure whats going on there but i had the last line removed:
     lines.Count - 2

Sadly the temp is still not reporting more than just the whole number. I would prefer it to report up to 3 decimal places.