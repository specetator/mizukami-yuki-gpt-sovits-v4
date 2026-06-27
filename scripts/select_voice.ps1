param(
    [Parameter(Mandatory = $true)]
    [string]$SourceDir,
    [Parameter(Mandatory = $true)]
    [string]$OutputDir,
    [int]$Top = 50,
    [string]$Extension = "*.ogg"
)

$ErrorActionPreference = "Stop"
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

function Clamp([double]$value, [double]$min, [double]$max) {
    if ($value -lt $min) { return $min }
    if ($value -gt $max) { return $max }
    return $value
}

function TriScore([double]$value, [double]$ideal, [double]$tolerance) {
    return (Clamp (1.0 - ([math]::Abs($value - $ideal) / $tolerance)) 0.0 1.0)
}

function Parse-LastNumber($text, [string]$pattern) {
    $matches = [regex]::Matches($text, $pattern)
    if ($matches.Count -eq 0) { return $null }
    for ($i = $matches.Count - 1; $i -ge 0; $i--) {
        $raw = $matches[$i].Groups[1].Value
        if ($raw -match "inf") { continue }
        return [double]::Parse($raw, [Globalization.CultureInfo]::InvariantCulture)
    }
    return $null
}

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    throw "ffmpeg was not found in PATH."
}
if (-not (Get-Command ffprobe -ErrorAction SilentlyContinue)) {
    throw "ffprobe was not found in PATH."
}
if (-not (Test-Path -LiteralPath $SourceDir)) {
    throw "Source directory not found: $SourceDir"
}

$files = Get-ChildItem -LiteralPath $SourceDir -File -Filter $Extension | Sort-Object Name
if ($files.Count -lt $Top) {
    throw "Only $($files.Count) files found; need $Top."
}

$results = New-Object System.Collections.Generic.List[object]
$total = $files.Count
$index = 0

foreach ($file in $files) {
    $index++
    if (($index % 50) -eq 0 -or $index -eq 1 -or $index -eq $total) {
        Write-Host ("Analyzing {0}/{1}: {2}" -f $index, $total, $file.Name)
    }

    try {
        $probeJson = & ffprobe -v error -show_entries format=duration,bit_rate -show_entries stream=sample_rate,channels -of json $file.FullName
        $probe = $probeJson | ConvertFrom-Json
        $duration = [double]::Parse($probe.format.duration, [Globalization.CultureInfo]::InvariantCulture)
        $bitRate = if ($probe.format.bit_rate) { [double]$probe.format.bit_rate } else { 0.0 }
        $sampleRate = if ($probe.streams.Count -gt 0) { [int]$probe.streams[0].sample_rate } else { 0 }
        $channels = if ($probe.streams.Count -gt 0) { [int]$probe.streams[0].channels } else { 0 }

        $oldErrorActionPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        $ffmpegOutput = (& ffmpeg -hide_banner -nostats -i $file.FullName -af "astats=metadata=0:reset=0,silencedetect=noise=-45dB:d=0.20" -f null - 2>&1) -join "`n"
        $ErrorActionPreference = $oldErrorActionPreference
        $peakDb = Parse-LastNumber $ffmpegOutput "Peak level dB:\s+(-?inf|[-+]?\d+(?:\.\d+)?)"
        $rmsDb = Parse-LastNumber $ffmpegOutput "RMS level dB:\s+(-?inf|[-+]?\d+(?:\.\d+)?)"
        $peakCount = Parse-LastNumber $ffmpegOutput "Peak count:\s+([-+]?\d+(?:\.\d+)?)"

        $silenceDuration = 0.0
        foreach ($m in [regex]::Matches($ffmpegOutput, "silence_duration:\s+([-+]?\d+(?:\.\d+)?)")) {
            $silenceDuration += [double]::Parse($m.Groups[1].Value, [Globalization.CultureInfo]::InvariantCulture)
        }
        $silenceRatio = if ($duration -gt 0) { $silenceDuration / $duration } else { 1.0 }

        if ($null -eq $peakDb -or $null -eq $rmsDb -or [double]::IsInfinity($peakDb) -or [double]::IsInfinity($rmsDb)) {
            $score = -1000.0
        } else {
            $durationScore = TriScore $duration 6.5 5.5
            $bitRateScore = Clamp ($bitRate / 96000.0) 0.0 1.0
            $rmsScore = TriScore $rmsDb -19.0 9.0
            $peakScore = TriScore $peakDb -3.0 6.0
            $silenceScore = Clamp (1.0 - ($silenceRatio / 0.28)) 0.0 1.0

            $clipPenalty = 0.0
            if ($peakDb -gt -0.35) { $clipPenalty += 0.35 }
            if ($peakCount -gt 20) { $clipPenalty += 0.15 }
            if ($duration -lt 2.0 -or $duration -gt 15.0) { $clipPenalty += 0.30 }

            $score = (
                0.30 * $durationScore +
                0.25 * $silenceScore +
                0.20 * $rmsScore +
                0.15 * $peakScore +
                0.10 * $bitRateScore -
                $clipPenalty
            )
        }

        $results.Add([pscustomobject]@{
            Rank = $null
            FileName = $file.Name
            FullName = $file.FullName
            DurationSec = [math]::Round($duration, 3)
            BitRate = [int]$bitRate
            SampleRate = $sampleRate
            Channels = $channels
            RmsDb = if ($null -eq $rmsDb) { $null } else { [math]::Round($rmsDb, 3) }
            PeakDb = if ($null -eq $peakDb) { $null } else { [math]::Round($peakDb, 3) }
            PeakCount = if ($null -eq $peakCount) { $null } else { [int]$peakCount }
            SilenceSec = [math]::Round($silenceDuration, 3)
            SilenceRatio = [math]::Round($silenceRatio, 4)
            Score = [math]::Round($score, 6)
        })
    }
    catch {
        $results.Add([pscustomobject]@{
            Rank = $null
            FileName = $file.Name
            FullName = $file.FullName
            Score = -1000.0
            Error = $_.Exception.Message
        })
    }
}

New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
$allCsv = Join-Path $OutputDir "voice_quality_scores.csv"
$results | Sort-Object Score -Descending | Export-Csv -LiteralPath $allCsv -NoTypeInformation -Encoding UTF8

$selected = $results |
    Where-Object { $_.Score -gt 0 -and $_.DurationSec -ge 2.0 -and $_.DurationSec -le 15.0 -and $_.SilenceRatio -le 0.28 -and $_.PeakDb -le -0.35 } |
    Sort-Object Score -Descending |
    Select-Object -First $Top

if ($selected.Count -lt $Top) {
    Write-Host "All scores CSV: $allCsv"
    $results | Sort-Object Score -Descending | Select-Object -First 10 | Format-Table -AutoSize
    throw "Only $($selected.Count) files passed quality filters; adjust thresholds if needed."
}

$selectedDir = Join-Path $OutputDir "selected_audio"
New-Item -ItemType Directory -Path $selectedDir -Force | Out-Null

$rank = 0
foreach ($item in $selected) {
    $rank++
    $item.Rank = $rank
    Copy-Item -LiteralPath $item.FullName -Destination (Join-Path $selectedDir $item.FileName) -Force
}

$topCsv = Join-Path $OutputDir "selected_top.csv"
$listTxt = Join-Path $OutputDir "selected_top.txt"
$selected | Export-Csv -LiteralPath $topCsv -NoTypeInformation -Encoding UTF8
$selected | ForEach-Object { $_.FileName } | Set-Content -LiteralPath $listTxt -Encoding UTF8

Write-Host ""
Write-Host "Selected top $Top files into: $selectedDir"
Write-Host "Top CSV: $topCsv"
Write-Host "All scores CSV: $allCsv"
$selected | Select-Object Rank,FileName,DurationSec,RmsDb,PeakDb,SilenceRatio,BitRate,Score | Format-Table -AutoSize
