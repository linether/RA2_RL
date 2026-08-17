# dev.ps1 - RA2_RL development convenience entry (Agent-10, see TASK.md item 4)
# Usage:
#   scripts\dev.ps1 test        -> pytest (unit only, per pyproject addopts)
#   scripts\dev.ps1 test-all    -> pytest -m "unit or integration" (set RA2RL_INTEGRATION=1 first)
#   scripts\dev.ps1 lint        -> ruff check .
#   scripts\dev.ps1 server-up   -> start openra-rl Docker server on :8000
#
# Track B (real game, venv B) is intentionally NOT wired here - see Agent-09 docs.
# server-up note: switches to Agent-05 ensure_server() health check once ra2_env/recovery lands.

param(
    [Parameter(Position = 0)]
    [ValidateSet("test", "test-all", "lint", "server-up")]
    [string]$Command = "test"
)

$ErrorActionPreference = "Stop"
$PyA = "E:\conda_envs\ra2rl\Scripts\python.exe"   # venv A (agents/README.md section 6)

# run from repo root regardless of caller cwd
$repoRoot = Split-Path -Parent $PSScriptRoot
Push-Location $repoRoot
try {
    switch ($Command) {
        "test" {
            & $PyA -m pytest
        }
        "test-all" {
            if (-not $env:RA2RL_INTEGRATION) {
                Write-Warning "RA2RL_INTEGRATION not set - integration cases will be skipped"
            }
            & $PyA -m pytest -m "unit or integration"
        }
        "lint" {
            & $PyA -m ruff check .
        }
        "server-up" {
            & $PyA -m openra_env.cli server start
        }
    }
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
