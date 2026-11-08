# PowerShell Build Script for Animation Forge Windows Installer (.msi / .exe)
$ErrorActionPreference = "Stop"
Write-Host "=== Animation Forge Windows Production Packaging ===" -ForegroundColor Cyan

# 1. Package Python FastAPI Sidecar via PyInstaller
Write-Host "[1/3] Building Python FastAPI Sidecar executable..."
pyinstaller --noconfirm --onefile --name "animation-forge-backend-x86_64-pc-windows-msvc" backend/main.py --distpath src-tauri/binaries

# 2. Build React + TypeScript Frontend
Write-Host "[2/3] Building React + TypeScript Frontend..."
Push-Location frontend
npm install
npm run build
Pop-Location

# 3. Build Tauri 2 Windows MSI & NSIS Installer
Write-Host "[3/3] Building Tauri 2 Windows Desktop Installer..."
npx @tauri-apps/cli@latest build
Write-Host "Build Complete! Installers located in src-tauri/target/release/bundle/" -ForegroundColor Green
