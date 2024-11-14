$outputFile = "dataOutput.csv"

if(!(Test-Path $outputFile)){
    "Timestamp,Counter,Value"|Out-File -FilePath $outputFile -Encoding utf8
}
$pcmCounterPaths=Get-Counter -ListSet "PCM*" | ForEach-Object {$_.Paths}

while($true){
    $pcmCounters=Get-Counter -Counter $pcmCounterPaths
    $timestamp=(Get-Date).ToString("yyyy-MM-dd HH:mm:ss")

    foreach($counter in $pcmCounters.CounterSamples){
        $counterPath= $counter.Path.Replace("\","_").Replace(" ","_")
        $value=$counter.CookedValue
        "$timestamp,$counterPath,$value" | Out-File -FilePath $outputFile -Append -Encoding utf8
    }

    Start-Sleep -Seconds 10
}