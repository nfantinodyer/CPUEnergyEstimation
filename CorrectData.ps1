# Define the input and output file paths
$inputFile = "output.csv"
$outputFile = "newout.csv"

# Step 1: Insert the #datatype row at the top
$datatypeRow = "#datatype measurement,dateTime:2006-01-02T15:04:05.000Z,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double,double"

# Define the second row as the column header row
$headerRow = "pcm,DateTime,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,READ,WRITE,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,C0res%,C1res%,C3res%,C6res%,C7res%,C0res%,C2res%,C3res%,C6res%,C7res%,C8res%,C9res%,C10res%,Proc Energy (Joules),Power Plane 0 Energy (Joules),Power Plane 1 Energy (Joules),EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,READ,WRITE,IO,IA,GT,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,C0res%,C1res%,C3res%,C6res%,C7res%,C0res%,C2res%,C3res%,C6res%,C7res%,C8res%,C9res%,C10res%,SKT0,SKT0,SKT0,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%,EXEC,IPC,FREQ,AFREQ,CFREQ,L3MISS,L2MISS,L3HIT,L3MPI,L2MPI,C0res%,C1res%,C3res%,C6res%,C7res%,TEMP,INST,ACYC,TIME(ticks),PhysIPC,PhysIPC%,INSTnom,INSTnom%"

# Read the CSV file contents and split it into lines
$lines = Get-Content -Path $inputFile

# Step 2: Remove the second row and adjust headers
$adjustedLines = @()
$adjustedLines += $datatypeRow  # Insert #datatype row
$adjustedLines += $headerRow    # Insert the header row with DateTime column merged

# Step 3: Process each data row
foreach ($line in $lines[2..($lines.Count - 1)]) {
    # Step 4: Adjust Date and Time columns into DateTime format with "T" separator and "Z" at the end
    $line = $line -replace '(^\d{4}-\d{2}-\d{2}),(\d{2}:\d{2}:\d{2}\.\d+)', '$1T$2Z'

    # Step 5: Prepend "pcm," to each row
    $line = "pcm," + $line

    # Add the modified line to the output collection
    $adjustedLines += $line
}

# Save the processed lines to the output file
$adjustedLines | Set-Content -Path $outputFile
