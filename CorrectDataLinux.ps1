$inputDirectory = "Data\Linux\StressNGData"
$outputDirectory = "Data\NewData\Linux\StressNGData"
if (!(Test-Path $outputDirectory)) {
    New-Item -Path $outputDirectory -ItemType Directory -Force | Out-Null
}

#resolve to full absolute paths
$inputDirectory = (Get-Item -Path $inputDirectory).FullName
$outputDirectory = (Get-Item -Path $outputDirectory).FullName

$measurement = "LinuxPCM"
$headerRow = $measurement + ",DateTime,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,READ,WRITE,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,C0res%,C1res%,C3res%,C6res%,C7res%,C0res%,C2res%,C3res%,C6res%,C7res%,C8res%,C9res%,C10res%,Proc Energy (Joules),Power Plane 0 Energy (Joules),Power Plane 1 Energy (Joules),EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,READ,WRITE,IO,IA,GT,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,C0res%,C1res%,C3res%,C6res%,C7res%,C0res%,C2res%,C3res%,C6res%,C7res%,C8res%,C9res%,C10res%,SKT0,SKT0,SKT0,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L2HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,Temperature"
$datatypeRow = "#datatype measurement,dateTime:2006-01-02T15:04:05.000Z,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double"

$inputFiles = Get-ChildItem -Path $inputDirectory -Filter "*.csv" -Recurse

foreach ($inputFile in $inputFiles) {
    # Ensure consistent path formats
    $inputFileFullName = $inputFile.FullName -replace '\\', '/'
    $inputDirNormalized = $inputDirectory -replace '\\', '/'

    $relativePath = $inputFileFullName.Substring($inputDirNormalized.Length)
    $relativePath = $relativePath.TrimStart('/', '\')

    $outputFilePath = Join-Path $outputDirectory $relativePath

    $outputFileDirectory = Split-Path $outputFilePath -Parent
    if (!(Test-Path $outputFileDirectory)) {
        New-Item -Path $outputFileDirectory -ItemType Directory -Force | Out-Null
    }

    $lines = Get-Content -Path $inputFile.FullName

    $adjustedLines = @()
    $adjustedLines += $datatypeRow
    $adjustedLines += $headerRow

    foreach ($line in $lines[2..($lines.Count - 1)]) {
        $adjustedLine = $line -replace '(^\d{4}-\d{2}-\d{2}),(\d{2}:\d{2}:\d{2}\.\d+)', '$1T$2Z'
        $adjustedLine = $measurement + "," + $adjustedLine
        $adjustedLines += $adjustedLine
    }

    $adjustedLines | Set-Content -Path $outputFilePath
}