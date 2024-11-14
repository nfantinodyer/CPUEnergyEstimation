$inputFile = "C:\Users\2013r\Downloads\CPUEnergyEstimation-main\CPUEnergyEstimation-main\dataOutput.csv"
$outputFile = "C:\Users\2013r\Downloads\CPUEnergyEstimation-main\CPUEnergyEstimation-main\dataOutputWithMeasurement.csv"
$measurement = "pcm_data"

# Read the CSV, prepend the measurement, and write to a new file
Get-Content $inputFile | ForEach-Object { "$measurement,$_" } | Set-Content $outputFile
