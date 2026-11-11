<#
.SYNOPSIS
    Starts the local Animation Forge development stack with one shared IPC token.

.DESCRIPTION
    Brings up, in order:
      1. ComfyUI (image generation service, default 127.0.0.1:8188)
      2. The API sidecar (default 127.0.0.1:8765)
      3. The Vite frontend dev server (default 127.0.0.1:1420)

    The API sidecar and the frontend must share the same ANIMATION_FORGE_IPC_TOKEN,
    because the Vite proxy injects it as the x-forge-token header. This script
    reads the token from a file so both processes always agree. If the file is
    missing it generates one.

    Services that are already listening are left alone, so the script is safe to
    re-run.

.PARAMETER ComfyRoot
    Root of the ComfyUI portable install.

.PARAMETER TokenFile
    File holding the shared IPC token.

.PARAMETER SkipComfyUI
    Do not start ComfyUI (useful when it is already running elsewhere).

.PARAMETER ReviewPort
    Also start the standalone Visual Development review UI on this port.
    Use 0 to skip it.

.EXAMPLE
    .\scripts\start_local_stack.ps1

.EXAMPLE
    .\scripts\start_local_stack.ps1 -ReviewPort 8790
#>
[CmdletBinding()]
param(
    [string]$ComfyRoot = 'D:\Downloads\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable',
    [string]$TokenFile = "$env:TEMP\opencode\forge_token.txt",
    [switch]$SkipComfyUI,
    [int]$ReviewPort = 8790,
    [int]$ApiPort = 8765,
    [int]$FrontendPort = 1420
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot

function Test-Port([int]$Port) {
    return $null -ne (Get-NetTCPConnection -State Listen -LocalPort $Port -ErrorAction SilentlyContinue)
}

function Wait-Port([int]$Port, [int]$Seconds = 60) {
    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Port $Port) { return $true }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

# --- shared IPC token -------------------------------------------------------
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $TokenFile) | Out-Null
if (-not (Test-Path $TokenFile)) {
    $bytes = New-Object byte[] 48
    [System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
    [System.IO.File]::WriteAllText($TokenFile, [Convert]::ToBase64String($bytes), (New-Object System.Text.UTF8Encoding($false)))
    Write-Host "Generated a new IPC token at $TokenFile"
}
$token = [System.IO.File]::ReadAllText($TokenFile)
if ($token.Length -lt 43) { throw "IPC token in $TokenFile is too short (needs 43+ characters)." }

# --- 1. ComfyUI ------------------------------------------------------------
if (-not $SkipComfyUI) {
    if (Test-Port 8188) {
        Write-Host "ComfyUI already listening on 8188 - left alone."
    } else {
        if (-not (Test-Path (Join-Path $ComfyRoot 'python_embeded\python.exe'))) {
            throw "ComfyUI not found at $ComfyRoot. Pass -ComfyRoot or -SkipComfyUI."
        }
        $env:PYTHONUTF8 = '1'
        Write-Host "Starting ComfyUI on 8188 ..."
        Start-Process -FilePath (Join-Path $ComfyRoot 'python_embeded\python.exe') `
            -ArgumentList '-s', 'ComfyUI\main.py', '--windows-standalone-build', '--fast',
                          'fp16_accumulation', '--port', '8188', '--disable-auto-launch' `
            -WorkingDirectory $ComfyRoot -WindowStyle Hidden | Out-Null
        Wait-Port 8188 120 | Out-Null
    }
}

# --- 2. API sidecar --------------------------------------------------------
if (Test-Port $ApiPort) {
    Write-Host "API sidecar already listening on $ApiPort - left alone."
} else {
    $env:ANIMATION_FORGE_IPC_TOKEN = $token
    $env:ANIMATION_FORGE_PORT = "$ApiPort"
    Write-Host "Starting API sidecar on $ApiPort ..."
    Start-Process -FilePath (Join-Path $repoRoot '.venv\Scripts\python.exe') `
        -ArgumentList '-m', 'backend.main' -WorkingDirectory $repoRoot -WindowStyle Hidden | Out-Null
    Wait-Port $ApiPort 60 | Out-Null
}

# --- 3. Vite frontend ------------------------------------------------------
if (Test-Port $FrontendPort) {
    Write-Host "Frontend already listening on $FrontendPort - left alone."
} else {
    $env:ANIMATION_FORGE_IPC_TOKEN = $token
    Write-Host "Starting frontend dev server on $FrontendPort ..."
    Start-Process -FilePath 'npm.cmd' -ArgumentList 'run', 'dev' `
        -WorkingDirectory (Join-Path $repoRoot 'frontend') -WindowStyle Hidden | Out-Null
    Wait-Port $FrontendPort 60 | Out-Null
}

# --- 4. optional standalone review UI --------------------------------------
if ($ReviewPort -gt 0) {
    if (Test-Port $ReviewPort) {
        Write-Host "Review UI already listening on $ReviewPort - left alone."
    } else {
        $project = Join-Path $repoRoot 'PROJECTS\VDEV_YS01_YS01_REVISED_V1'
        if (Test-Path $project) {
            Write-Host "Starting Visual Development review UI on $ReviewPort ..."
            Start-Process -FilePath (Join-Path $repoRoot '.venv\Scripts\python.exe') `
                -ArgumentList '-m', 'VISUAL_DEVELOPMENT.cli', 'review', '--project-dir', $project, '--port', "$ReviewPort" `
                -WorkingDirectory $repoRoot -WindowStyle Hidden | Out-Null
            Wait-Port $ReviewPort 30 | Out-Null
        }
    }
}

Write-Host ''
Write-Host 'Local stack status:'
foreach ($port in @(8188, $ApiPort, $FrontendPort, $ReviewPort)) {
    if ($port -gt 0) {
        $state = if (Test-Port $port) { 'UP  ' } else { 'DOWN' }
        Write-Host ("  {0} 127.0.0.1:{1}" -f $state, $port)
    }
}
Write-Host ''
Write-Host "Frontend:  http://127.0.0.1:$FrontendPort/  (click 'Visual Development' in the sidebar)"
Write-Host "Review UI: http://127.0.0.1:$ReviewPort/"
Write-Host "Token:     $TokenFile"
Write-Host "Restart the API or the frontend with the same token: `$env:ANIMATION_FORGE_IPC_TOKEN = (Get-Content '$TokenFile' -Raw)"
