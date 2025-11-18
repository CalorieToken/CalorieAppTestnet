param(
    [switch]$CopyToClipboard,
    [ValidateSet('twitter','telegram','discord','linkedin','instagram','youtube','email')]
    [string]$Platform = 'twitter'
)

Write-Host "== Social Post Copy Helper ==" -ForegroundColor Cyan

$date = Get-Date -Format 'yyyy-MM-dd'
$postsDir = Join-Path "$PSScriptRoot" "..\docs\posts\$date"

if (-not (Test-Path $postsDir)) {
    Write-Host "Generating social posts for $date..." -ForegroundColor Yellow
    & "$PSScriptRoot\generate_social_posts.ps1"
}

$textFile = Join-Path $postsDir "$Platform.txt"
$imageDir = Join-Path "$PSScriptRoot" "..\assets\social-media\$date-docs-update"

if (Test-Path $textFile) {
    Write-Host "`n📝 $Platform POST:" -ForegroundColor Green
    Get-Content $textFile | Write-Host
    
    if ($CopyToClipboard) {
        Get-Content $textFile | Set-Clipboard
        Write-Host "`n✅ Copied to clipboard!" -ForegroundColor Green
    }
} else {
    Write-Error "Post file not found: $textFile"
}

Write-Host "`n📸 VISUAL ASSETS:" -ForegroundColor Cyan
if (Test-Path $imageDir) {
    Get-ChildItem $imageDir -Filter *.png | ForEach-Object {
        Write-Host "  • $($_.Name)" -ForegroundColor Yellow
    }
    Write-Host "`nLocation: $imageDir"
} else {
    Write-Host "  ⚠️ Image directory not found: $imageDir" -ForegroundColor Yellow
    Write-Host "  Generate images using prompts in:" -ForegroundColor DarkGray
    Write-Host "  docs\posts\VISUAL_CONCEPTS_$date.md" -ForegroundColor DarkGray
}

Write-Host "`n💡 RECOMMENDED IMAGE:" -ForegroundColor Cyan
switch ($Platform) {
    'twitter' { Write-Host "  Use: square-1080x1080.png OR twitter-1200x628.png" }
    'telegram' { Write-Host "  Use: square-1080x1080.png" }
    'discord' { Write-Host "  Use: square-1080x1080.png OR story-1080x1920.png" }
    'linkedin' { Write-Host "  Use: linkedin-1200x627.png" }
    'instagram' { Write-Host "  Use: square-1080x1080.png (feed) OR story-1080x1920.png (story)" }
    'youtube' { Write-Host "  Use: square-1080x1080.png" }
    'email' { Write-Host "  Use: linkedin-1200x627.png OR square-1080x1080.png" }
}

Write-Host "`n🔄 QUICK COPY OTHER PLATFORMS:" -ForegroundColor Cyan
@('twitter','telegram','discord','linkedin','instagram','youtube','email') | Where-Object { $_ -ne $Platform } | ForEach-Object {
    Write-Host "  pwsh tools\copy_social_post.ps1 -Platform $_ -CopyToClipboard" -ForegroundColor DarkGray
}
