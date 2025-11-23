# PowerShell script to activate Python venv
$envName = "venv"
$venvPath = Join-Path $PSScriptRoot $envName
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Host "Activating Python venv..."
    & $activateScript
} else {
    Write-Host "Virtual environment not found. Run 'make setup-env' first."
}
