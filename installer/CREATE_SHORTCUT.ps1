# Run this if the installer shortcuts didn't work
# Right-click → Run with PowerShell

$installDir = Split-Path -Parent $PSScriptRoot
$shortcutPath = [Environment]::GetFolderPath("Desktop") + "\RHODECO ERP.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "$installDir\START_ERP.bat"
$shortcut.WorkingDirectory = $installDir
$shortcut.Description = "RHODECO ERP System v2.0"
$shortcut.Save()
Write-Host "Shortcut created on Desktop: $shortcutPath" -ForegroundColor Green
Pause
