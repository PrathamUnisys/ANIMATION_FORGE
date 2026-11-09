<#
.SYNOPSIS
    Pre-render environment guard for the Animation Forge V2 pipeline.

.DESCRIPTION
    This machine has 11.7 GB RAM, of which ~0.8 GB is free while the Ollama desktop app
    is resident at ~4.0 GB. Every render batch therefore risks page-thrashing. This script
    measures the real state, optionally reclaims Ollama's memory, and refuses to start a
    batch when there is not enough headroom.

    It reports; it does not guess. Every number printed comes from the OS or nvidia-smi.

.PARAMETER StopOllama
    Stop the Ollama desktop app and server before measuring. Reclaims ~4 GB RAM.
    Off by default: stopping someone else's process must be explicit.

.PARAMETER MinFreeRamGb
    Refuse to pass if free physical RAM is below this. Default 3.0.

.PARAMETER MinFreeVramMb
    Refuse to pass if free VRAM is below this. Default 6000.

.PARAMETER MinFreeDiskGb
    Refuse to pass if the target drive has less free space. Default 20.

.PARAMETER Drive
    Drive letter to check for disk headroom. Default D.

.PARAMETER Force
    Report the same numbers but always exit 0 (use for diagnostics, never for a batch).

.EXAMPLE
    .\env_guard.ps1 -StopOllama
    .\env_guard.ps1 -StopOllama -MinFreeRamGb 4

.OUTPUTS
    Exit code 0 = safe to render. 1 = insufficient headroom. 2 = a required tool is missing.
#>
[CmdletBinding()]
param(
    [switch]$StopOllama,
    [double]$MinFreeRamGb = 3.0,
    [int]$MinFreeVramMb = 6000,
    [double]$MinFreeDiskGb = 20,
    [string]$Drive = 'D',
    [switch]$Force
)

$ErrorActionPreference = 'Stop'

function Get-Snapshot {
    $os = Get-CimInstance Win32_OperatingSystem
    $freeRamGb = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
    $totalRamGb = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
    $commitLimitGb = [math]::Round($os.TotalVirtualMemorySize / 1MB, 2)
    $committedGb = [math]::Round(($os.TotalVirtualMemorySize - $os.FreeVirtualMemory) / 1MB, 2)

    $vramFreeMb = $null
    $vramTotalMb = $null
    $nvsmi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
    if ($nvsmi) {
        $line = (& $nvsmi.Source --query-gpu=memory.total,memory.used --format=csv,noheader,nounits 2>$null) -join ''
        if ($line -match '^\s*(\d+)\s*,\s*(\d+)') {
            $vramTotalMb = [int]$Matches[1]
            $vramFreeMb = [int]$Matches[1] - [int]$Matches[2]
        }
    }

    $disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='${Drive}:'" -ErrorAction SilentlyContinue
    $diskFreeGb = if ($disk) { [math]::Round($disk.FreeSpace / 1GB, 1) } else { $null }

    [pscustomobject]@{
        FreeRamGb     = $freeRamGb
        TotalRamGb    = $totalRamGb
        CommitLimitGb = $commitLimitGb
        CommittedGb   = $committedGb
        VramFreeMb    = $vramFreeMb
        VramTotalMb   = $vramTotalMb
        DiskFreeGb    = $diskFreeGb
    }
}

function Show-Snapshot($s, $label) {
    Write-Host ""
    Write-Host "  $label" -ForegroundColor Cyan
    Write-Host ("    RAM free      : {0,6} GB / {1} GB" -f $s.FreeRamGb, $s.TotalRamGb)
    Write-Host ("    Commit        : {0,6} GB / {1} GB" -f $s.CommittedGb, $s.CommitLimitGb)
    if ($null -ne $s.VramFreeMb) {
        Write-Host ("    VRAM free     : {0,6} MB / {1} MB" -f $s.VramFreeMb, $s.VramTotalMb)
    } else {
        Write-Host  "    VRAM free     : nvidia-smi unavailable"
    }
    Write-Host ("    {0}: free        : {1,6} GB" -f $Drive, $s.DiskFreeGb)
}

Write-Host "=== Animation Forge :: env_guard ===" -ForegroundColor White
Write-Host "Thresholds: RAM >= $MinFreeRamGb GB free | VRAM >= $MinFreeVramMb MB free | ${Drive}: >= $MinFreeDiskGb GB free"

$before = Get-Snapshot
Show-Snapshot $before "BEFORE"

$ollama = Get-Process -Name 'ollama app','ollama' -ErrorAction SilentlyContinue
if ($ollama) {
    $held = [math]::Round((($ollama | Measure-Object WorkingSet64 -Sum).Sum) / 1MB, 0)
    Write-Host ""
    Write-Host "  Ollama resident, holding ~$held MB." -ForegroundColor Yellow
    if ($StopOllama) {
        Write-Host "  Stopping Ollama (-StopOllama)..." -ForegroundColor Yellow
        try {
            & ollama stop *> $null 2>&1
        } catch { }
        $ollama | Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        $after = Get-Snapshot
        Show-Snapshot $after "AFTER"
        $reclaimed = [math]::Round($after.FreeRamGb - $before.FreeRamGb, 2)
        Write-Host ("    Reclaimed ~{0} GB RAM" -f $reclaimed) -ForegroundColor Green
        $current = $after
    } else {
        Write-Host "  Not stopping it. Re-run with -StopOllama to reclaim ~$held MB." -ForegroundColor Yellow
        $current = $before
    }
} else {
    Write-Host ""
    Write-Host "  Ollama not running." -ForegroundColor Green
    $current = $before
}

# ---------------------------------------------------------------- evaluations
$failures = New-Object System.Collections.Generic.List[string]

if ($current.FreeRamGb -lt $MinFreeRamGb) {
    $failures.Add("RAM: $($current.FreeRamGb) GB free < $MinFreeRamGb GB required")
}
if ($null -eq $current.VramFreeMb) {
    $failures.Add("VRAM: nvidia-smi unavailable, cannot verify headroom")
} elseif ($current.VramFreeMb -lt $MinFreeVramMb) {
    $failures.Add("VRAM: $($current.VramFreeMb) MB free < $MinFreeVramMb MB required")
}
if ($null -eq $current.DiskFreeGb) {
    $failures.Add("DISK: drive ${Drive}: not found")
} elseif ($current.DiskFreeGb -lt $MinFreeDiskGb) {
    $failures.Add("DISK: ${Drive}: $($current.DiskFreeGb) GB free < $MinFreeDiskGb GB required")
}

Write-Host ""
if ($failures.Count -eq 0) {
    Write-Host "RESULT: PASS - safe to start a render batch." -ForegroundColor Green
    exit 0
}

Write-Host "RESULT: FAIL - do not start a render batch." -ForegroundColor Red
foreach ($f in $failures) { Write-Host "  - $f" -ForegroundColor Red }

if ($Force) {
    Write-Host "  (-Force set: exiting 0 anyway for diagnostics)" -ForegroundColor Yellow
    exit 0
}
exit 1
