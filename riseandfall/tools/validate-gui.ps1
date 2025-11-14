<#
validate-gui.ps1 — simple checks for CK3 GUI modding
- Checks brace balance in .gui files under the mod folder
- Finds any "riseandfall." localization IDs and reports missing keys in `localization/english`
- Reports files that mention `riseandfall.` more than once (possible duplicate ids)

Usage:
& .\validate-gui.ps1 -Root "C:\Users\Aweso\Documents\Paradox Interactive\Crusader Kings III\mod\development"
#>
param(
    [string]$Root = "$(Split-Path -Path $PSScriptRoot -Parent)",
    [switch]$Verbose
)

function Check-FileBraceBalance {
    param([string]$Path)
    $text = Get-Content -Raw -Path $Path -ErrorAction SilentlyContinue
    if (-not $text) { return @{Path=$Path; Ok=$true} }
    $open = ($text -split '\{' | Measure-Object).Count - 1
    $close = ($text -split '\}' | Measure-Object).Count - 1
    return @{Path=$Path; Open=$open; Close=$close; Ok=($open -eq $close)}
}

Write-Host "[validate-gui] Root: $Root" -ForegroundColor Cyan
$guiFiles = Get-ChildItem -Path $Root -Recurse -Include *.gui,*.txt -File
$errors = @()
foreach ($f in $guiFiles) {
    $res = Check-FileBraceBalance -Path $f.FullName
    if (-not $res.Ok) {
        $errors += "Brace mismatch: $($res.Path) -> {=$($res.Open) }=$($res.Close)"
    }
}

if ($errors.Count -gt 0) {
    Write-Host "Brace balance issues found:" -ForegroundColor Yellow
    $errors | ForEach-Object { Write-Host $_ }
} else { Write-Host "Brace balance: OK" -ForegroundColor Green }

# Localization coverage: find all riseandfall. keys
$pattern = 'riseandfall\.'
$repoGuiFiles = Get-ChildItem -Path $Root -Recurse -Include *.gui,*.txt -File
$keys = @{}
foreach ($f in $repoGuiFiles) {
    $text = Get-Content -Raw -Path $f.FullName -ErrorAction SilentlyContinue
    if ($text -match $pattern) {
        foreach ($m in ([regex]::Matches($text, ${pattern}[A-Za-z0-9_\-\.]+))) {
            $id = $m.Value
            if ($keys.ContainsKey($id)) { $keys[$id]++ } else { $keys[$id] = 1 }
        }
    }
}

Write-Host "Found $($keys.Keys.Count) riseandfall. localization tokens in GUI files." -ForegroundColor Cyan
# Report duplicates
$dupes = $keys.GetEnumerator() | Where-Object { $_.Value -gt 1 } | Sort-Object -Property Name
if ($dupes) {
    Write-Host "Potential duplicate keys referencing the same token (occurrences):" -ForegroundColor Yellow
    $dupes | ForEach-Object { Write-Host "  $($_.Name) -> $($_.Value)" }
}

# Check localization files for tokens
$locFiles = Get-ChildItem -Path (Join-Path $Root 'localization\english') -Filter *.yml -Recurse -File -ErrorAction SilentlyContinue
$locText = ($locFiles | ForEach-Object { Get-Content -Raw $_ } ) -join "`n"
$missing = @()
foreach ($k in $keys.Keys) {
    # Remove trailing punctuation
    $lookup = $k
    if (-not ($locText -match [regex]::Escape($lookup))) { $missing += $lookup }
}
if ($missing.Count -gt 0) {
    Write-Host "Missing localization keys:" -ForegroundColor Yellow
    $missing | ForEach-Object { Write-Host "  $_" }
} else { Write-Host "Localization: All riseandfall tokens have entries (or none referenced)." -ForegroundColor Green }

Write-Host "Done." -ForegroundColor Cyan
