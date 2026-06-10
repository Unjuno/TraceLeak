<#
Bootstrap a local TraceLeak checkout for lightweight validation on Windows PowerShell.

This script intentionally runs only lightweight repository checks.
It does not run OpenSSL instrumentation, heavy trace generation, or NN training.

Usage:
  powershell -ExecutionPolicy Bypass -File scripts/bootstrap_local.ps1
  powershell -ExecutionPolicy Bypass -File scripts/bootstrap_local.ps1 -Dir C:\Users\junny\Desktop\TraceLeak
  powershell -ExecutionPolicy Bypass -File scripts/bootstrap_local.ps1 -Python python
  powershell -ExecutionPolicy Bypass -File scripts/bootstrap_local.ps1 -SkipTests
#>

param(
    [string]$RepoUrl = "https://github.com/Unjuno/TraceLeak.git",
    [string]$Dir = "TraceLeak",
    [string]$Python = "python",
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

function Test-CommandExists {
    param([string]$Name)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "required command not found: $Name"
    }
}

Test-CommandExists git
Test-CommandExists $Python

if (Test-Path (Join-Path $Dir ".git")) {
    Write-Host "[TraceLeak] updating existing checkout: $Dir"
    git -C $Dir pull --ff-only
} elseif (Test-Path $Dir) {
    throw "target exists but is not a git checkout: $Dir"
} else {
    Write-Host "[TraceLeak] cloning $RepoUrl -> $Dir"
    git clone $RepoUrl $Dir
}

Set-Location $Dir

if (-not (Test-Path "pyproject.toml")) {
    throw "pyproject.toml not found. Are you in the TraceLeak repository root?"
}

Write-Host "[TraceLeak] creating virtual environment"
& $Python -m venv .venv

$activate = Join-Path ".venv" "Scripts\Activate.ps1"
if (-not (Test-Path $activate)) {
    throw "virtual environment activation script not found: $activate"
}

. $activate

Write-Host "[TraceLeak] upgrading pip"
python -m pip install --upgrade pip

Write-Host "[TraceLeak] installing package with dev extras"
python -m pip install -e ".[dev]"

if (-not $SkipTests) {
    Write-Host "[TraceLeak] running lightweight tests"
    pytest
} else {
    Write-Host "[TraceLeak] skipping tests"
}

Write-Host ""
Write-Host "[TraceLeak] local bootstrap complete."
Write-Host ""
Write-Host "Next lightweight commands:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  pytest"
Write-Host ""
Write-Host "Heavy/local-only work, intentionally not run by this script:"
Write-Host "  - OpenSSL instrumentation builds"
Write-Host "  - raw trace generation"
Write-Host "  - NN training"
Write-Host "  - large experiment runs"
