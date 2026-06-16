# RHODECO ERP - Biometric Punch Import Script
# Date: May 15, 2026
# Run this in PowerShell: .\send_punches_may15.ps1

$url = "http://127.0.0.1:5000/timekeeping/biometric/punch"
$headers = @{ "Content-Type" = "application/json" }

$punches = @(
    # Santos, Juan A. - On time
    @{ biometric_id="001"; datetime="2026-05-15 07:58:00"; type="IN";  device_id="DEVICE_001" },
    @{ biometric_id="001"; datetime="2026-05-15 17:02:00"; type="OUT"; device_id="DEVICE_001" },

    # Reyes, Maria C. - On time, 2.25hrs OT
    @{ biometric_id="002"; datetime="2026-05-15 08:03:00"; type="IN";  device_id="DEVICE_001" },
    @{ biometric_id="002"; datetime="2026-05-15 19:15:00"; type="OUT"; device_id="DEVICE_001" },

    # Dela Cruz, Pedro B. - LATE 17 mins
    @{ biometric_id="003"; datetime="2026-05-15 08:22:00"; type="IN";  device_id="DEVICE_001" },
    @{ biometric_id="003"; datetime="2026-05-15 17:00:00"; type="OUT"; device_id="DEVICE_001" },

    # Garcia, Ana L. - On time, 1.5hrs OT
    @{ biometric_id="004"; datetime="2026-05-15 07:55:00"; type="IN";  device_id="DEVICE_001" },
    @{ biometric_id="004"; datetime="2026-05-15 18:30:00"; type="OUT"; device_id="DEVICE_001" },

    # Mendoza, Rico T. - On time
    @{ biometric_id="005"; datetime="2026-05-15 08:01:00"; type="IN";  device_id="DEVICE_001" },
    @{ biometric_id="005"; datetime="2026-05-15 17:05:00"; type="OUT"; device_id="DEVICE_001" },

    # Bautista, Luisa M. - On time, 3hrs OT
    @{ biometric_id="006"; datetime="2026-05-15 08:00:00"; type="IN";  device_id="DEVICE_001" },
    @{ biometric_id="006"; datetime="2026-05-15 20:00:00"; type="OUT"; device_id="DEVICE_001" },

    # Torres, Felix R. - On time
    @{ biometric_id="007"; datetime="2026-05-15 07:50:00"; type="IN";  device_id="DEVICE_001" },
    @{ biometric_id="007"; datetime="2026-05-15 17:10:00"; type="OUT"; device_id="DEVICE_001" },

    # Aquino, Rosa V. - On time, 0.5hr OT
    @{ biometric_id="008"; datetime="2026-05-15 08:05:00"; type="IN";  device_id="DEVICE_001" },
    @{ biometric_id="008"; datetime="2026-05-15 17:30:00"; type="OUT"; device_id="DEVICE_001" },

    # Lim, Carlos D. - ABSENT (no punch - intentionally skipped)

    # Cruz, Elena P. - On time
    @{ biometric_id="010"; datetime="2026-05-15 08:00:00"; type="IN";  device_id="DEVICE_001" },
    @{ biometric_id="010"; datetime="2026-05-15 17:00:00"; type="OUT"; device_id="DEVICE_001" }
)

$names = @{
    "001"="Santos, Juan A."
    "002"="Reyes, Maria C."
    "003"="Dela Cruz, Pedro B. [LATE 17min]"
    "004"="Garcia, Ana L."
    "005"="Mendoza, Rico T."
    "006"="Bautista, Luisa M."
    "007"="Torres, Felix R."
    "008"="Aquino, Rosa V."
    "010"="Cruz, Elena P."
}

Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "  RHODECO Biometric Punch Import" -ForegroundColor Cyan
Write-Host "  Date: May 15, 2026" -ForegroundColor Cyan
Write-Host "  Total punches: $($punches.Count)" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

$success = 0
$failed  = 0

foreach ($punch in $punches) {
    $body = $punch | ConvertTo-Json
    $name = $names[$punch.biometric_id]
    $label = "$($punch.type) | Bio $($punch.biometric_id) | $name | $($punch.datetime)"

    try {
        $response = Invoke-RestMethod -Method Post -Uri $url -ContentType "application/json" -Body $body
        Write-Host "  OK  $label" -ForegroundColor Green
        $success++
    } catch {
        Write-Host "  FAIL $label" -ForegroundColor Red
        Write-Host "       Error: $_" -ForegroundColor DarkRed
        $failed++
    }

    Start-Sleep -Milliseconds 200
}

Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "  Done! $success sent, $failed failed" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next step: Open http://127.0.0.1:5000/timekeeping" -ForegroundColor Yellow
Write-Host "           Set date to May 15, 2026 and verify records." -ForegroundColor Yellow
Write-Host ""

if ($failed -gt 0) {
    Write-Host "Some punches failed. Make sure the ERP server is running on port 5000." -ForegroundColor Red
}
