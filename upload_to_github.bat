@echo off
chcp 65001 >nul
title OptLitBench - GitHub Upload
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\upload_to_github.ps1"
echo.
pause
