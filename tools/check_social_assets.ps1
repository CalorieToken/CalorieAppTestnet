Param(
    [string]$Path = "assets/social-media/2025-11-18-docs-update"
)

Write-Host "== Social Media Asset Verification ==" -ForegroundColor Cyan
if (-not (Test-Path $Path)) {
    Write-Host "Directory not found: $Path" -ForegroundColor Red
    exit 1
}

$required = @(
    'square-1080x1080.png',
    'story-1080x1920.png',
    'twitter-1200x628.png',
    'linkedin-1200x627.png'
)

$optional = @(
    'email-header-1200x400.png',
    'youtube-community-1000x1000.png'
)

$present = Get-ChildItem -Path $Path -File | Select-Object -ExpandProperty Name

Write-Host "\nRequired Assets:" -ForegroundColor Yellow
$missing = @()
foreach ($r in $required) {
    if ($present -contains $r) {
        Write-Host "  [OK] $r" -ForegroundColor Green
    } else {
        Write-Host "  [MISSING] $r" -ForegroundColor Red
        $missing += $r
    }
}

Write-Host "\nOptional Assets:" -ForegroundColor Yellow
foreach ($o in $optional) {
    if ($present -contains $o) {
        Write-Host "  [OK] $o" -ForegroundColor Green
    } else {
        Write-Host "  [ABSENT] $o" -ForegroundColor DarkYellow
    }
}

Write-Host "\nSummary:" -ForegroundColor Cyan
Write-Host "  Present: $($present.Count)" -ForegroundColor Cyan
Write-Host "  Missing required: $($missing.Count)" -ForegroundColor Cyan

if ($missing.Count -eq 0) {
    Write-Host "All required assets present. Ready to commit." -ForegroundColor Green
    exit 0
} else {
    Write-Host "Missing required assets. Generate before committing." -ForegroundColor Red
    exit 2
}
