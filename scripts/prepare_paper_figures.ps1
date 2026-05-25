# Copy experiment figures into the local Overleaf package (not uploaded to GitHub).
param(
    [string]$ProjectRoot = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = "Stop"
$srcRoot = Join-Path $ProjectRoot "results\temporal\figures"
$dstRoot = Join-Path $ProjectRoot "paper\icdm2026\overleaf_package\figures"
$legacyDst = Join-Path $ProjectRoot "paper\icdm2026\figures"

New-Item -ItemType Directory -Force -Path $dstRoot | Out-Null
New-Item -ItemType Directory -Force -Path $legacyDst | Out-Null

$map = @{
    "journal_topic_profile_heatmap.png" = "cross_journal\journal_topic_profile_heatmap.png"
    "journal_cosine_clustermap.png" = "cross_journal\journal_cosine_clustermap.png"
    "journal_jsd_clustermap.png" = "cross_journal\journal_jsd_clustermap.png"
    "journal_specialization_index.png" = "cross_journal\journal_specialization_index.png"
    "distinctive_topics_heatmap.png" = "cross_journal\distinctive_topics_heatmap.png"
    "journal_temporal_divergence.png" = "cross_journal\journal_temporal_divergence.png"
    "optimization_topic_year_heatmap.png" = "journals\optimization_topic_year_heatmap.png"
    "mathematical_programming_topic_year_heatmap.png" = "journals\mathematical_programming_topic_year_heatmap.png"
    "cpaior_topic_year_heatmap.png" = "journals\cpaior_topic_year_heatmap.png"
    "siam_control_topic_year_heatmap.png" = "journals\siam_journal_on_control_and_optimization_topic_year_heatmap.png"
    "structural_optimization_topic_year_heatmap.png" = "journals\structural_and_multidisciplinary_optimization_topic_year_heatmap.png"
    "mathematical_programming_topic_evolution_lines.png" = "journals\mathematical_programming_topic_evolution_lines.png"
}

foreach ($name in $map.Keys) {
    $source = Join-Path $srcRoot $map[$name]
    if (-not (Test-Path $source)) {
        throw "Missing figure source: $source"
    }
    Copy-Item -Force $source (Join-Path $dstRoot $name)
    Copy-Item -Force $source (Join-Path $legacyDst $name)
}

Write-Host "[OK] Paper figures synced to overleaf_package/figures" -ForegroundColor Green
