# Simple validation script for Rise and Fall mod
# Checks for basic syntax issues and missing localization keys

Write-Host "Checking Rise and Fall mod files..." -ForegroundColor Green

$modPath = Split-Path $PSScriptRoot
$errorsFound = $false

# Check for brace balance in text files
Get-ChildItem -Path $modPath -Recurse -Include "*.txt" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content) {
        $openBraces = ($content.ToCharArray() | Where-Object { $_ -eq '{' }).Count
        $closeBraces = ($content.ToCharArray() | Where-Object { $_ -eq '}' }).Count
        
        if ($openBraces -ne $closeBraces) {
            Write-Host "BRACE MISMATCH in $($_.Name): $openBraces open, $closeBraces close" -ForegroundColor Red
            $errorsFound = $true
        }
    }
}

# Check for missing localization keys
$locFiles = Get-ChildItem -Path "$modPath\localization\english" -Include "*.yml" -Recurse
$locKeys = @()

# Extract all localization keys
$locFiles | ForEach-Object {
    $content = Get-Content $_.FullName
    $content | ForEach-Object {
        if ($_ -match '^\s*([^:]+):') {
            $locKeys += $matches[1].Trim()
        }
    }
}

# Check script files for referenced keys
Get-ChildItem -Path $modPath -Recurse -Include "*.txt" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    if ($content) {
        # Look for potential localization key references
        $matches = [regex]::Matches($content, 'riseandfall\.\w+(?:\.\w+)*')
        $matches | ForEach-Object {
            $key = $_.Value
            if ($key -notmatch '\.(t|d|a)$' -and $locKeys -notcontains $key) {
                Write-Host "POTENTIAL MISSING LOC KEY: $key in $($_.Name)" -ForegroundColor Yellow
            }
        }
    }
}

if (-not $errorsFound) {
    Write-Host "Basic validation passed!" -ForegroundColor Green
} else {
    Write-Host "Errors found - please review above." -ForegroundColor Red
}
