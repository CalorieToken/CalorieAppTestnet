Param(
  [string]$Version = 'v1.1.1'
)

Write-Host "== CalorieApp Release Summary ($Version) ==" -ForegroundColor Cyan

$releaseFile = "docs/RELEASE_$Version.md".Replace(':','_')
if (-not (Test-Path $releaseFile)) {
  # fallback for v1.1.1 naming
  $releaseFile = "docs/RELEASE_v1.1.1.md"
}

if (Test-Path $releaseFile) {
  Write-Host "-- Release Notes --" -ForegroundColor Yellow
  Get-Content $releaseFile | Select-Object -First 40 | ForEach-Object { Write-Host $_ }
  Write-Host "... (truncated)" -ForegroundColor DarkGray
} else {
  Write-Host "Release file not found: $releaseFile" -ForegroundColor Red
}

Write-Host "\n-- Social (Short) --" -ForegroundColor Yellow
Write-Host "CalorieApp UX & Docs upgrade LIVE → faster flows, stronger security, improved mnemonic UX. Focus: Security • Speed • UX. #CalorieApp #XRPL" -ForegroundColor Green

Write-Host "\n-- Social (Standard) --" -ForegroundColor Yellow
Write-Host "CalorieApp UX & Documentation upgrade is LIVE: faster multi-screen flow, improved mnemonic verification, hardened security layers, and a public-safe docs index." -ForegroundColor Green

Write-Host "\n-- Image Hint --" -ForegroundColor Yellow
Write-Host "Use: assets/social-media/2025-11-18-docs-update/square-1080x1080.png" -ForegroundColor Green

Write-Host "\n-- Next Version Placeholder --" -ForegroundColor Yellow
Select-String -Path CHANGELOG.md -Pattern "1.1.2" | ForEach-Object { $_.Line } | ForEach-Object { Write-Host $_ }

Write-Host "\nDone." -ForegroundColor Cyan