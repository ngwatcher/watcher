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

# Get the data in the right format
$startDate = Get-Date -Day 29 -Month 01 -Year 2020
$endDate = Get-Date -Day 04 -Month 06 -Year 2020

$DataPaths = @()
while($startDate -le $endDate){
    $MonthName = Get-Date $startDate -format MM | %{(Get-Culture).DateTimeFormat.GetMonthName($_)}
    $Year = Get-Date $startDate -format yyyy
    $DayString = Get-Date $startDate -format dd-MM-yy

    $DataPath = "$Year/DAILYPAYMENT/" + $MonthName.ToUpper() + "/$DayString"
    $DataPaths += @{
        "path" = $DataPath;
        "dayString" = $DayString
    }

    $startDate = $startDate.AddDays(1)
}

$BaseEndpoint = "https://opentreasury.gov.ng/images/"
$LocalBasePath = "data\"

foreach($DataPath in $DataPaths) {

    $Source = $BaseEndpoint + $DataPath.path + ".xlsx"
    $Destination = $LocalBasePath + $DataPath.dayString + ".xlsx"

    Write-Host "Source: $Source"
    Write-Host "Destination: $Destination"

    # Now make API Call to get excel files
    Invoke-WebRequest -Uri $Source -OutFile $Destination

}