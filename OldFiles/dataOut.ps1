$outputFile = "dataOutputWithMeasurement.csv"
$measurement = "pcm_data"
$durationSeconds = 120 # Set the run duration to 5 seconds
$startTime = Get-Date

# Create the file with headers if it doesn't exist
if (!(Test-Path $outputFile)) {
    @"
#datatype measurement,dateTime:2006-01-02 15:04:05,tag,double
pcm_data,time,metric,value
"@ | Out-File -FilePath $outputFile -Encoding utf8
}

# Get the list of PCM counter paths
$pcmCounterPaths = Get-Counter -ListSet "PCM*" | ForEach-Object { $_.Paths }

# Start the loop to capture counter data
while ((Get-Date) -lt $startTime.AddSeconds($durationSeconds)) {
    $pcmCounters = Get-Counter -Counter $pcmCounterPaths
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")

    foreach ($counter in $pcmCounters.CounterSamples) {
        $counterPath = $counter.Path.Replace("\", "_").Replace(" ", "_")
        $value = $counter.CookedValue
        # Prepend the measurement to each line
        "$measurement,$timestamp,$counterPath,$value" | Out-File -FilePath $outputFile -Append -Encoding utf8
    }

    Start-Sleep -Milliseconds 250
}