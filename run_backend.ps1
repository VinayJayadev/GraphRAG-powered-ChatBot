# PowerShell script to run the backend server
# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "Current directory: $PWD"
Write-Host "Starting GraphRAG ChatBot Backend Server..."
Write-Host "Server will be available at: http://localhost:8000"
Write-Host "API Documentation: http://localhost:8000/docs"
Write-Host ""
Write-Host "Press Ctrl+C to stop the server"
Write-Host ""

# Use the start.py script which handles Python path correctly
python start.py

