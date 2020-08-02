<#

.SYNOPSIS
This is a simple Powershell script to fetch data from Nigeria's Open Treasury Portal

.EXAMPLE
./FetchDaijy-Data.ps1

.LINK
https://oreogundipe.dev`

#>

# Data Structure
# Data is stored incrementally daily in the format below
# https://opentreasury.gov.ng/images/<YEAR>/DAILYPAYMENT/<MONTHNAME>/<DAY string e.g 29-01-20>.xlsx"

# Define data sources & result paths
$BaseEndpoint = "https://opentreasury.gov.ng/images/"
$LocalBasePath = "$(Get-Location)\data\"

# Create excel client
$excelApp = New-Object -ComObject Excel.Application 
$excelApp.DisplayAlerts = $false 

# Get the date periods in the right format
$startDate = Get-Date -Day 29 -Month 01 -Year 2020
$endDate = Get-Date -Day 31 -Month 07 -Year 2020

# Get candidate data path strings
$DataPaths = @()
while($startDate -le $endDate){
    $MonthName = Get-Date $startDate -format MM | ForEach-Object{(Get-Culture).DateTimeFormat.GetMonthName($_)}
    $Year = Get-Date $startDate -format yyyy
    $SourceDayString = Get-Date $startDate -format dd-MM-yy
    $DestDayString = Get-Date $startDate -format MM-dd-yy

    $DataPath = "$Year/DAILYPAYMENT/" + $MonthName.ToUpper() + "/$SourceDayString"
    $DataPaths += @{
        "path" = $DataPath;
        "destDayString" = $DestDayString
    }

    $startDate = $startDate.AddDays(1)
}


# Recursively fetch data entries and convert each entry to csv
foreach($DataPath in $DataPaths) {
    $Source = $BaseEndpoint + $DataPath.path + ".xlsx"
    $ExcelDestination = $LocalBasePath + $DataPath.destDayString + ".xlsx"

    Write-Host "Source: $Source"
    Write-Host "ExcelDestination: $ExcelDestination"

    # Now make API Call to get excel files
    Invoke-WebRequest -Uri $Source -OutFile $ExcelDestination
}