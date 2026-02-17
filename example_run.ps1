# ZEGA Grand Forge - Owner Edition
# Optimized for modified PS7 Green (#58f01b)

# --- Branding ---
$green = "Green"
$red   = "Red"
$gray  = "Gray"
$SrcDir = ".\examples"

Clear-Host
Write-Host "==========================================================" -ForegroundColor $green
Write-Host "                ZEGA GRAND FORGE PROTOCOL                 " -ForegroundColor $green
Write-Host "==========================================================" -ForegroundColor $green
Write-Host "[STATUS] Syncing Toolchain..." -ForegroundColor $gray

# 1. Environment Check
if (!(Get-Command zscomp -ErrorAction SilentlyContinue)) {
    Write-Host "[!] 'zscomp' function not found. Forge aborted." -ForegroundColor $red
    return
}

# 2. Start Forge Timer
$Timer = [System.Diagnostics.Stopwatch]::StartNew()
$Success = 0

# 3. Mass Compilation
$Scripts = Get-ChildItem -Path $SrcDir -Filter *.zs

foreach ($Script in $Scripts) {
    Write-Host ">>> FORGING: " -NoNewline -ForegroundColor $gray
    Write-Host "$($Script.Name)" -ForegroundColor $green
    
    # Execute global profile command
    zscomp $Script.FullName
    
    if ($?) { $Success++ }
}

# 4. Summary
$Timer.Stop()
Write-Host "`n----------------------------------------------------------" -ForegroundColor $gray
Write-Host "  COMPLETED: $($Success) / $($Scripts.Count) Modules" -ForegroundColor $green
Write-Host "  TIME:      $([math]::Round($Timer.Elapsed.TotalSeconds, 2))s" -ForegroundColor $gray
Write-Host "==========================================================" -ForegroundColor $green