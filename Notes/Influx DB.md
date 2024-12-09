#CSEN283
Downloaded from:
https://docs.influxdata.com/influxdb/v2/install/?t=Windows#download-and-install-influxdb-v2
https://docs.influxdata.com/influxdb/v2/tools/influx-cli/?t=Windows
Then ran it in powershell to host the local host. Then go to the website: http://localhost:8086/

You can also use the CLI and write using cmd or powershell.

>C:\Program Files\InfluxData

Login:
NicholasFD


Org:
CSEN283

API:
f0Hit-RPTtlylt6VKIHPzpMAX750CJ0o-uMdZaEiTtcnGy-Wa6DNKIN49Ujj9b5cv2K914JqGMyN8R_cP5AOGQ==

Format CSV:
\#datatype measurement,dateTime:2006-01-02 15:04:05,tag,double
pcm_data,time,metric,value

Write to Influx:
influx write -o CSEN283 -b pcm_data -f "C:\Users\2013r\Downloads\CPUEnergyEstimation-main\CPUEnergyEstimation-main\dataOutputWithMeasurement.csv" -t f0Hit-RPTtlylt6VKIHPzpMAX750CJ0o-uMdZaEiTtcnGy-Wa6DNKIN49Ujj9b5cv2K914JqGMyN8R_cP5AOGQ==

![[DataInfluxImage.png]]

### Now with better data:
Refer to [[Windows Intel Monitor#^bf74da]] to see how to get the data.

Run CorrectData.ps1, with the output.csv in the same directory.
Then run:
>cd "C:\Program Files\InfluxData"
>influx write -o CSEN283 -b pcm_data -f "C:\Users\2013r\Downloads\CPUEnergyEstimation-main\CPUEnergyEstimation-main\newout.csv" -t f0Hit-RPTtlylt6VKIHPzpMAX750CJ0o-uMdZaEiTtcnGy-Wa6DNKIN49Ujj9b5cv2K914JqGMyN8R_cP5AOGQ==

The measurement is now pcm, and you can select which filter you want.

![[Power.png]]


The windows header doesn't contain L2HITS which is why the data columns were one off when pushing the Linux Data. Fixed in the CorrectData.ps1 file by each one having its unique headers.
Also measurement is now WindowsPCM or LinuxPCM.