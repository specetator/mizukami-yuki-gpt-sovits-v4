param(
    [Parameter(Mandatory = $true)]
    [string]$InputDir,
    [Parameter(Mandatory = $true)]
    [string]$OutputDir,
    [string]$Extension = "*.*"
)

$ErrorActionPreference = "Stop"
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    throw "ffmpeg was not found in PATH."
}

New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
$files = Get-ChildItem -LiteralPath $InputDir -File -Filter $Extension | Sort-Object Name
if ($files.Count -eq 0) {
    throw "No input files found in $InputDir"
}

$index = 0
foreach ($file in $files) {
    $index++
    $stem = [IO.Path]::GetFileNameWithoutExtension($file.Name)
    $out = Join-Path $OutputDir "$stem.wav"
    Write-Host ("[{0}/{1}] {2} -> {3}" -f $index, $files.Count, $file.Name, $out)
    & ffmpeg -hide_banner -y -i $file.FullName -ac 1 -ar 16000 -c:a pcm_s16le $out
    if ($LASTEXITCODE -ne 0) {
        throw "ffmpeg failed for $($file.FullName)"
    }
}

Write-Host "Converted $($files.Count) files to $OutputDir"
