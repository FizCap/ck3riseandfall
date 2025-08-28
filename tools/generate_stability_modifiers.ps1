# Generates 100 stability modifiers interpolated from 5 stage anchors
$stages = @(0,25,50,75,100)
$ind = @(-50,-25,0,10,30)
$vass = @(-25,-10,0,5,10)
$county = @(-30,-15,0,5,10)
$court = @(-25,-10,0,5,10)
function interp($s,$x0,$x1,$y0,$y1){
    if (($x1 - $x0) -eq 0) { return $y0 }
    else { return [math]::Round($y0 + ($y1 - $y0) * (($s - $x0) / ($x1 - $x0))) }
}

$outPath = "c:\Users\Aweso\Documents\Paradox Interactive\Crusader Kings III\mod\riseandfall\common\modifiers\riseandfall_stability_levels.txt"
$lines = New-Object System.Collections.Generic.List[string]
for ($i = 1; $i -le 100; $i++) {
    $s = ($i - 1) * 100.0 / 99.0
    for ($seg = 0; $seg -lt 4; $seg++) {
        if ($s -ge $stages[$seg] -and $s -le $stages[$seg + 1]) {
            $x0 = $stages[$seg]; $x1 = $stages[$seg + 1]
            $indVal = interp $s $x0 $x1 $ind[$seg] $ind[$seg+1]
            $vassVal = interp $s $x0 $x1 $vass[$seg] $vass[$seg+1]
            $countyVal = interp $s $x0 $x1 $county[$seg] $county[$seg+1]
            $courtVal = interp $s $x0 $x1 $court[$seg] $court[$seg+1]
            break
        }
    }
    if ($indVal -lt 0) { $icon = 'intrigue_negative' } else { $icon = 'intrigue_positive' }
    $lines.Add("riseandfall_stability_$i = {")
    $lines.Add("    independent_ruler_opinion = $indVal")
    $lines.Add("    vassal_opinion = $vassVal")
    $lines.Add("    county_opinion_add = $countyVal")
    $lines.Add("    courtier_opinion = $courtVal")
    $lines.Add("    icon = $icon")
    $lines.Add("}")
    $lines.Add("")
}
$lines | Out-File -FilePath $outPath -Encoding utf8
Write-Output "Wrote $($lines.Count) lines to $outPath"
