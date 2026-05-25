# Push OptLitBench to GitHub (meetyangyang)

Run this script after installing [Git](https://git-scm.com/download/win) and configuring GitHub authentication.

## Prerequisites

1. Install Git for Windows
2. Create an empty repository on GitHub: https://github.com/new
   - Repository name: `OptLitBench`
   - Owner: `meetyangyang`
   - Do **not** initialize with README (we provide one)

3. Authenticate (choose one):
   - GitHub CLI: `gh auth login`
   - Or HTTPS with Personal Access Token

## One-time push

```powershell
cd "e:\GITHUB\topic analysis with NMF"

git init
git add .
git commit -m "Release OptLitBench: benchmark, pipeline, ICDM 2026 paper, and results"

git branch -M main
git remote add origin https://github.com/meetyangyang/OptLitBench.git
git push -u origin main
```

## If repository already exists with README

```powershell
git remote add origin https://github.com/meetyangyang/OptLitBench.git
git pull origin main --rebase
git push -u origin main
```

## Large file note

Total repo size is ~450 MB (includes `Data_Abstract/` and `results/`).
If push fails due to size limits, use Git LFS for `Data_Abstract/` or upload data as a GitHub Release asset.
