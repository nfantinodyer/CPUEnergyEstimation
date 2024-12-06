#CSEN283 

Using the [[Gathering Data 120224]] we now are getting temperature readings from the temperature sensor instead of pcm. 

![[ProcEnerCons120224.png]]![[averfreq.png]]
![[tempPreLoad.png]]![[utilload.png]]
![[tempperfeerwq.png]]![[predenercons.png]]
![[ResidualPlot.png]]![[enerconscputuil.png]]
![[eneroric.png]]
There are still some inconstancies with the way I imagine the spread should be. The next step will be getting more accurate temp data instead of every Celsius it will be to a more specific number.

For my temp sensor I am using:
```shell
TEMP=$(sensors -u | grep -E 'temp[1-9]_input' | head -1 | awk '{printf "%.3f", $2}')
```

printf "%.3f", $2 gets the 3rd decimal places.

Also now that its automated I increased the amount of tests:
partial_loads = list(range(0, 100, 10))
since 2,4,6 threads now measure all 10
"stress-ng --cpu 2 --cpu-method matrixprod --cpu-load 0 --timeout 60s|Linux0Static2threads.csv"

I will be increasing the length of measure as well by 2 by increasing length by 60seconds