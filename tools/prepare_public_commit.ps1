param(
    [switch]$Auto,
    [string]$Branch = "chore/repo-hardening"
)

Write-Host "== CalorieAppTestnet: Public-Safe Commit Helper ==" -ForegroundColor Cyan

# Verify git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "git not found in PATH. Please install Git and retry."; exit 1
}

# Show current branch
$currentBranch = (git rev-parse --abbrev-ref HEAD).Trim()
Write-Host ("Current branch: {0}" -f $currentBranch) -ForegroundColor Yellow
if ($currentBranch -ne $Branch) {
    Write-Host ("[i] Target branch set to: {0}" -f $Branch)
}

# Files to add (public-safe)
$files = @(
    "README.md",
    "docs/README.md",
    "docs/OFFICIAL_PROJECT_DOCS.md",
    "docs/STATUS_UPDATE_2025-11-18.md",
    "docs/UX_TOUR_GUIDE.md",
    "docs/UX_TOUR_V2_UPDATES.md",
    "docs/UX_TOUR_QUICK_REF.md",
    "docs/CHANGELOG.md",
    ".gitignore"
)

# Include tools scripts
$toolFiles = Get-ChildItem -Path "$PSScriptRoot" -Filter *.ps1 | ForEach-Object { (Resolve-Path $_.FullName).Path }

Write-Host "\nPlanned staging set (public-safe):" -ForegroundColor Cyan
$files | ForEach-Object { Write-Host "  + $_" }
$toolFiles | ForEach-Object { Write-Host ("  + {0}" -f (Resolve-Path -Relative $_)) }

if ($Auto) {
    foreach ($f in $files) { if (Test-Path $f) { git add -- $f } }
    foreach ($tf in $toolFiles) { git add -- (Resolve-Path -Relative $tf) }
} else {
    Write-Host "\nTip: Re-run with -Auto to stage automatically." -ForegroundColor DarkGray
}

Write-Host "\nGit status (short):" -ForegroundColor Cyan
 git status -s

$today = (Get-Date -Format 'yyyy-MM-dd')
$commitMsg = @"
docs: public-safe documentation refresh and legal hardening

- Add official docs index and public status update
- Sanitize README and docs index (remove private links)
- Allowlist public UX tour guides; keep internals private
- Update CHANGELOG for repository hardening (1.1.1)

[date: $today]
"@

Set-Content -Path "$PSScriptRoot\_commit_message.txt" -Value $commitMsg -Encoding UTF8
Write-Host "\nPrepared commit message at tools/_commit_message.txt" -ForegroundColor Green
Write-Host "\nTo commit and push:" -ForegroundColor Cyan
Write-Host "git commit -F tools/_commit_message.txt"
Write-Host ("git push origin {0}" -f $currentBranch)
