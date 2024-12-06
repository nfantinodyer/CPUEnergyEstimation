#CSEN283 

I will be trying to further refine the temp measurement. Using the sensor data only returned whole numbers so I will try to use hwmon to return temp with higher precision. 

I added this into the analyze script to account for the new data. Since hwmon returns 40000 instead of 40.000:
```python
all_data_filtered.loc[:, 'Temperature'] = all_data_filtered['Temperature'].replace(0, np.nan)
all_data_filtered['Temperature'] = pd.to_numeric(all_data_filtered['Temperature'], errors='coerce') / 1000.0
all_data_filtered['Temperature'] = all_data_filtered['Temperature'].interpolate(method='linear')

```
The hwmon gave 1 decimal of precision by default but I will try to get more.

```bash
TEMP=$(echo "$TEMP" | awk '{printf "%.3f", $1 / 1000}')
``` 
This returns 28.000 but somehow in the csv it shows only the 28.0 part.

hwmon wasnt updating live and also didnt allow me to force update. so im going back to sensors