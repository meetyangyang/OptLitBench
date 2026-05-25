# Compile the ICDM 2026 paper locally and publish PDF for GitHub.
param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot),
    [string]$OutputPdfName = "OptLitBench_ICDM2026.pdf"
)

$ErrorActionPreference = "Stop"
& (Join-Path $PSScriptRoot "prepare_paper_figures.ps1") -ProjectRoot $ProjectRoot

$pkg = Join-Path $ProjectRoot "paper\icdm2026\overleaf_package"
$mainTex = Join-Path $pkg "main.tex"
$releasePdf = Join-Path $ProjectRoot "paper\icdm2026\$OutputPdfName"

if (-not (Test-Path $mainTex)) {
    throw "Missing LaTeX source: $mainTex"
}

function Find-LatexEngine {
    foreach ($cmd in @("pdflatex", "latexmk")) {
        $found = Get-Command $cmd -ErrorAction SilentlyContinue
        if ($found) { return $found.Source }
    }
    return $null
}

$engine = Find-LatexEngine
if (-not $engine) {
    Write-Host "[WARN] pdflatex/latexmk not found in PATH." -ForegroundColor Yellow
    Write-Host "       Compile on Overleaf, then save the PDF as:" -ForegroundColor Yellow
    Write-Host "       $releasePdf" -ForegroundColor Yellow
    & (Join-Path $PSScriptRoot "package_overleaf.ps1") -ProjectRoot $ProjectRoot
    exit 0
}

Push-Location $pkg
try {
    if ((Split-Path $engine -Leaf) -eq "latexmk") {
        & $engine -pdf -interaction=nonstopmode main.tex
    }
    else {
        foreach ($i in 1..2) { & $engine -interaction=nonstopmode main.tex | Out-Null }
        if (Test-Path "references.bib") {
            $bibtex = Get-Command bibtex -ErrorAction SilentlyContinue
            if ($bibtex) {
                & $bibtex.Source main | Out-Null
                & $engine -interaction=nonstopmode main.tex | Out-Null
                & $engine -interaction=nonstopmode main.tex | Out-Null
            }
        }
    }

    $builtPdf = Join-Path $pkg "main.pdf"
    if (-not (Test-Path $builtPdf)) {
        throw "Compilation finished but main.pdf was not created."
    }
    Copy-Item -Force $builtPdf $releasePdf
    Write-Host "[OK] Release PDF: $releasePdf" -ForegroundColor Green
}
finally {
    Pop-Location
}

# Local authoring artifacts only
& (Join-Path $PSScriptRoot "package_overleaf.ps1") -ProjectRoot $ProjectRoot
