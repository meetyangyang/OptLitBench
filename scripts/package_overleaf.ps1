# Build a local Overleaf upload ZIP (kept out of GitHub).
param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "prepare_paper_figures.ps1") -ProjectRoot $ProjectRoot

$pkg = Join-Path $ProjectRoot "paper\icdm2026\overleaf_package"
$zip = Join-Path $ProjectRoot "paper\icdm2026\OptLitBench_ICDM2026_overleaf.zip"
if (-not (Test-Path (Join-Path $pkg "main.tex"))) {
    throw "Missing Overleaf source: $pkg\main.tex"
}

if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path (Join-Path $pkg "*") -DestinationPath $zip -Force
Write-Host "[OK] Overleaf package: $zip" -ForegroundColor Green
