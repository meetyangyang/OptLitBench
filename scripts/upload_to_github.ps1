# OptLitBench one-click pack, commit, create repo (if needed), and push to GitHub.
# Usage:
#   Option 1: Double-click upload_to_github.bat
#   Option 2: $env:GITHUB_TOKEN = "ghp_xxxx"; .\scripts\upload_to_github.ps1

param(
    [string]$Token = $env:GITHUB_TOKEN,
    [string]$RepoOwner = "meetyangyang",
    [string]$RepoName = "OptLitBench"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $ProjectRoot "README.md"))) {
    throw "Cannot locate repository root from $PSScriptRoot"
}

$GitExe = "C:\Program Files\Git\bin\git.exe"
if (-not (Test-Path $GitExe)) {
    $cmd = Get-Command git -ErrorAction SilentlyContinue
    if ($cmd) { $GitExe = $cmd.Source }
}
if (-not $GitExe) {
    Write-Host "[ERROR] Git not found. Install from https://git-scm.com/download/win" -ForegroundColor Red
    exit 1
}

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$GitArgs,
        [switch]$AllowFailure
    )
    & $GitExe -C "$ProjectRoot" @GitArgs
    if (-not $AllowFailure -and $LASTEXITCODE -ne 0) {
        throw "Git failed: git $($GitArgs -join ' ')"
    }
    return $LASTEXITCODE
}

Write-Host "=== OptLitBench GitHub Upload ===" -ForegroundColor Cyan
Write-Host "Project: $ProjectRoot"

# --- Get GitHub Token ---
if (-not $Token) {
    Write-Host ""
    Write-Host "Paste your GitHub Personal Access Token (classic, scope: repo)." -ForegroundColor Yellow
    Write-Host "Create at: https://github.com/settings/tokens" -ForegroundColor Yellow
    $secure = Read-Host "Token (ghp_...)" -AsSecureString
    $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    $Token = [Runtime.InteropServices.Marshal]::PtrToStringAuto($ptr)
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
}
if (-not $Token -or $Token.Length -lt 10) {
    Write-Host "[ERROR] Token is empty." -ForegroundColor Red
    exit 1
}

$headers = @{
    Authorization = "Bearer $Token"
    Accept        = "application/vnd.github+json"
    "User-Agent"  = "OptLitBench-Upload"
}

# --- Create remote repository if missing ---
$repoApi = "https://api.github.com/repos/$RepoOwner/$RepoName"
try {
    Invoke-RestMethod -Uri $repoApi -Headers $headers -Method Get | Out-Null
    Write-Host "[OK] Remote repository already exists." -ForegroundColor Green
}
catch {
    Write-Host "[INFO] Creating repository $RepoOwner/$RepoName ..." -ForegroundColor Yellow
    $body = @{
        name        = $RepoName
        description = "OptLitBench: temporal topic mining benchmark on optimization literature (ICDM 2026)"
        private     = $false
        auto_init   = $false
    } | ConvertTo-Json
    try {
        Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Headers $headers -Method Post -Body $body | Out-Null
        Write-Host "[OK] Repository created." -ForegroundColor Green
    }
    catch {
        $err = $_.ErrorDetails.Message
        if ($err -match "name already exists") {
            Write-Host "[OK] Repository already exists (API race)." -ForegroundColor Green
        }
        else {
            throw "Failed to create repository: $err"
        }
    }
}

# --- Git init / remote ---
if (-not (Test-Path (Join-Path $ProjectRoot ".git"))) {
    Invoke-Git -GitArgs @("init") | Out-Null
    Write-Host "[OK] Git repository initialized." -ForegroundColor Green
}

$remoteUrl = "https://github.com/$RepoOwner/$RepoName.git"
Invoke-Git -GitArgs @("remote", "remove", "origin") -AllowFailure | Out-Null
$remoteAddCode = Invoke-Git -GitArgs @("remote", "add", "origin", $remoteUrl) -AllowFailure
if ($remoteAddCode -ne 0) {
    Invoke-Git -GitArgs @("remote", "set-url", "origin", $remoteUrl) | Out-Null
}
Write-Host "[OK] Remote origin configured." -ForegroundColor Green

Invoke-Git -GitArgs @("branch", "-M", "main") | Out-Null

# --- Ensure release PDF exists before upload ---
$releasePdf = Join-Path $ProjectRoot "paper\icdm2026\OptLitBench_ICDM2026.pdf"
if (-not (Test-Path $releasePdf)) {
    Write-Host "[WARN] Missing paper/icdm2026/OptLitBench_ICDM2026.pdf" -ForegroundColor Yellow
    Write-Host "       Run .\scripts\build_paper.ps1 or save your Overleaf PDF to that path." -ForegroundColor Yellow
}
else {
    Write-Host "[OK] Release PDF found: paper/icdm2026/OptLitBench_ICDM2026.pdf" -ForegroundColor Green
}

# --- Commit all changes (LaTeX under paper/ is gitignored; PDF is tracked) ---
Invoke-Git -GitArgs @("add", "-A") | Out-Null
$statusLines = & $GitExe -C "$ProjectRoot" status --porcelain
if ($statusLines) {
    Invoke-Git -GitArgs @(
        "-c", "user.name=Yang Yang",
        "-c", "user.email=yangyang@cipuc.edu.cn",
        "commit", "-m", "OptLitBench: corpus, pipeline, results, and ICDM 2026 paper"
    ) | Out-Null
    Write-Host "[OK] Changes committed." -ForegroundColor Green
}
else {
    Write-Host "[OK] Working tree clean (no new commit)." -ForegroundColor Green
}

# --- Push with token ---
$pushUrl = "https://${Token}@github.com/$RepoOwner/$RepoName.git"
Write-Host "[INFO] Pushing to GitHub (this may take several minutes, ~450MB)..." -ForegroundColor Yellow
& $GitExe -C "$ProjectRoot" push -u $pushUrl main
if ($LASTEXITCODE -ne 0) {
    throw "Push failed (exit $LASTEXITCODE). Check token repo scope and network."
}

# Restore clean remote URL without embedded token
Invoke-Git -GitArgs @("remote", "set-url", "origin", $remoteUrl) | Out-Null
Invoke-Git -GitArgs @("branch", "--set-upstream-to=origin/main", "main") -AllowFailure | Out-Null

Write-Host ""
Write-Host "=== SUCCESS ===" -ForegroundColor Green
Write-Host "Repository: https://github.com/$RepoOwner/$RepoName"
Write-Host "Clone:      git clone https://github.com/$RepoOwner/$RepoName.git"
