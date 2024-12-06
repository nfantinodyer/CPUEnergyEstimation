#CSEN283 
Using [[Gathering Data 120324]]

![[average2222.png]]![[avgrefere.png]]
![[avgetemp.png]]![[estiemate.png]]
![[scatterdww.png]]![[Pasted image 20241203125106.png]]

I went back to using the sensor data since it was the most updated one. And also ran it for 30 seconds:
![[Pasted image 20241203134227.png]]![[Pasted image 20241203134241.png]]
![[Pasted image 20241203134259.png]]![[Pasted image 20241203134312.png]]
![[Pasted image 20241203134330.png]]![[Pasted image 20241203134351.png]]
![[Pasted image 20241203134404.png]]![[Pasted image 20241203134427.png]]
![[Pasted image 20241203134455.png]]
It could be that pcm isnt properly measuring after a certain cpu load, or that after 30 load, the cpu evens out in its frequency and energy usage. The temp doesn't measure anything other than a whole number due to hardware.
- Maximum consumption is observed at **40% load**.
- Energy consumption decreases beyond **50% load**, suggesting possible efficiency optimizations or system throttling.


After gathering the windows data [[Windows Data Collection 120324]] here are the graphs and analysis:
![[Pasted image 20241203212611.png]]![[Pasted image 20241203212617.png]]
![[Pasted image 20241203212623.png]]![[Pasted image 20241203212630.png]]
![[Pasted image 20241203212636.png]]![[Pasted image 20241203212642.png]]
![[Pasted image 20241203212654.png]]![[Pasted image 20241203212704.png]]
![[Pasted image 20241203212714.png]]![[Pasted image 20241203212723.png]]
![[Pasted image 20241203212732.png]]![[Pasted image 20241203212742.png]]
![[Pasted image 20241203212752.png]]![[Pasted image 20241203212759.png]]
![[Pasted image 20241203212809.png]]![[Pasted image 20241203212817.png]]
![[Pasted image 20241203212823.png]]![[Pasted image 20241203212830.png]]
![[Pasted image 20241203212837.png]]![[Pasted image 20241203212843.png]]
![[Pasted image 20241203212853.png]]![[Pasted image 20241203212911.png]]
![[Pasted image 20241203212921.png]]### Energy Efficiency Metrics Summary

1. **Linux:**
    
    - **Energy per Instruction** has a mean of `0.060461` with a max value of `2.274047`.
    - **Energy per Cycle** shows an average value of `0.007575` and ranges up to `0.015929`.
    - **Cache Miss per Joule** has a mean of `0.000935`, indicating efficient use of cache resources relative to energy consumption.
2. **Windows:**
    
    - **Energy per Instruction** has a higher mean of `0.947550`, with significantly higher variability (std dev `1.726532`) and a max value of `6.217391`.
    - **Energy per Cycle** has a similar mean (`0.007452`) to Linux, showing comparable energy per clock cycle.
    - **Cache Miss per Joule** averages `0.109597`, much higher than Linux, suggesting less efficient cache use per energy unit.

### Statistical Comparison (t-test results)

1. **Energy per Instruction:**
    
    - The t-statistic of `-5.5316` and p-value of `2.0134e-07` indicate a statistically significant difference between Linux and Windows. Linux is more energy-efficient per instruction on average.
2. **Energy per Cycle:**
    
    - The t-statistic of `0.9030` and p-value of `0.3675` suggest no significant difference in energy per cycle between Linux and Windows.
3. **Cache Miss per Joule:**
    
    - The t-statistic of `-53.9805` and p-value of `1.3407e-83` reveal a substantial difference, with Linux showing far better cache efficiency relative to energy usage.

### Visual Observations

Scatterplots and boxplots visualize the differences:

- **Energy per Instruction:** Linux exhibits tighter grouping and lower values, while Windows shows high variance and higher outliers.
- **Energy per Cycle:** Both operating systems have similar distributions, confirming the t-test result.
- **Cache Miss per Joule:** Windows demonstrates significantly higher values, indicating inefficiency compared to Linux.

### Insights

1. **Linux Advantages:**
    
    - More energy-efficient per instruction, likely due to optimized CPU utilization and instruction scheduling.
    - Superior cache utilization efficiency, as reflected in the lower `Cache Miss per Joule` values.
2. **Windows Advantages:**
    
    - None specific in energy efficiency, though it matches Linux in energy per cycle.
3. **Areas for Improvement:**
    
    - Windows can optimize instruction execution and cache management to reduce energy consumption and improve efficiency metrics.
    - Linux could further align its cycle-based energy usage for workloads where such efficiency matters.



INST also has some anomalies in its data. Some values are far too low which skew the resulting graphs and data. So I will not include anything with 0.