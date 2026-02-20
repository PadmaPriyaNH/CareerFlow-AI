#!/usr/bin/env powershell
# CareerFlow AI - Complete Startup Script
# Run this: .\start_all.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "CareerFlow AI - Complete Startup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Ollama is installed
Write-Host "[1/3] Checking Ollama installation..." -ForegroundColor Yellow
$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {
    Write-Host "ERROR: Ollama is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Download from: https://ollama.ai" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Ollama found at: $($ollama.Source)" -ForegroundColor Green

# Check if Python virtual environment exists
Write-Host ""
Write-Host "[2/3] Checking Python environment..." -ForegroundColor Yellow
if (-not (Test-Path ".\.venv\Scripts\activate.ps1")) {
    Write-Host "ERROR: Virtual environment not found" -ForegroundColor Red
    Write-Host "Run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Virtual environment found" -ForegroundColor Green

# Check Ollama service
Write-Host ""
Write-Host "[3/3] Checking Ollama service..." -ForegroundColor Yellow
$ollama_running = $null
try {
    $ollama_running = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
    Write-Host "✓ Ollama is already running" -ForegroundColor Green
} catch {
    Write-Host "⚠ Ollama is not running. Starting it..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "IMPORTANT: A new window will open with Ollama service." -ForegroundColor Cyan
    Write-Host "Keep that window open while using CareerFlow AI." -ForegroundColor Cyan
    Start-Sleep -Seconds 2
    
    # Start Ollama in a new window
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "ollama serve"
    Write-Host "Waiting for Ollama to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
}

# Check if Mistral model is available
Write-Host ""
Write-Host "Checking AI model (mistral)..." -ForegroundColor Yellow
$models = $null
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
    $models = $response.Content | ConvertFrom-Json
    $has_mistral = $models.models | Where-Object { $_.name -like "mistral*" }
    
    if ($has_mistral) {
        Write-Host "✓ Mistral model is available" -ForegroundColor Green
    } else {
        Write-Host "⚠ Mistral model not found. Downloading..." -ForegroundColor Yellow
        & ollama pull mistral
    }
} catch {
    Write-Host "⚠ Could not verify model. It will be loaded on first use." -ForegroundColor Yellow
}

# Activate venv and start Django
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Starting CareerFlow AI..." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""

& ".\.venv\Scripts\activate.ps1"
python manage.py runserver

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "CareerFlow AI is running!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application at:" -ForegroundColor Cyan
Write-Host "  Web App:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "  Admin:    http://localhost:8000/admin/" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press CTRL+C to stop the server" -ForegroundColor Yellow
