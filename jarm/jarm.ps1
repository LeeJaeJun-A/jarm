# jarm.ps1

param (
    [string]$inputFile,
    [string]$outputFile
)

if (-not $inputFile -or -not $outputFile) {
    Write-Host "Two arguments required: (1) a list of IPs/domains in a"
    Write-Host "file, separated by line and (2) an output file name."
    Write-Host "Example: .\jarm.ps1 alexa500.txt jarm_alexa_500.csv"
    exit 1
}

Get-Content $inputFile | ForEach-Object {
    Start-Process -NoNewWindow -FilePath "python" -ArgumentList "jarm.py $_ -v -o $outputFile"
}

Get-Job | Wait-Job
