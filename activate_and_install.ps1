# PowerShell script to activate venv and install requirements
$venv = "venv"
$activate = ".\$venv\Scripts\Activate.ps1"
if (Test-Path $activate) {
    Write-Host "Activating venv..."
    . $activate
    Write-Host "Installing requirements..."
    pip install -r requirements.txt
} else {
    Write-Host "Virtual environment not found. Run 'make setup-env' first."
}
