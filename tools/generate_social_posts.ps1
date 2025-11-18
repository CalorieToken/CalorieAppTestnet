param(
  [string]$Date = (Get-Date -Format 'yyyy-MM-dd'),
  [switch]$ToClipboard
)

$updates = @{
  Twitter = @"
CalorieApp Testnet — Public docs + legal snapshot is live ✅

• Official docs index
• Public-safe UX tour guide
• Trademark + license in place

Follow progress: calorietoken.net  |  #XRPL #KivyMD #CalorieToken
"@;

  Telegram = @"
CalorieApp Testnet update ✅

We published a public‑safe documentation snapshot and legal hardening.

What’s included:
• Official docs index
• Public UX Tour guide
• Trademark + licensing readiness

Next: beta polish, performance + accessibility improvements.
Website: https://calorietoken.net
"@;

  Discord = @"
CalorieApp Testnet — Docs & Legal Snapshot ✅

- Official docs index
- Public-safe UX Tour guide
- Trademark + license integrated

Next up: beta stability + perf pass. Visit calorietoken.net
"@;

  LinkedIn = @"
We’ve published a public‑safe documentation and legal readiness snapshot for CalorieApp Testnet.

Highlights:
• Official documentation index
• Public overview of our automated UX tour
• Trademark + licensing in place (Custom Dual License)

Focus forward: beta stabilization, performance, and accessibility.
Learn more: https://calorietoken.net
"@;

  Instagram = @"
CalorieApp Testnet update ✅
Public docs + legal snapshot now live.

Docs index • UX tour (public) • Trademark + license

More soon as we polish beta and performance. 🔧🍏
Link in bio → calorietoken.net
"@;

  YouTube = @"
CalorieApp Testnet: public docs + legal snapshot now live ✅
Official docs index, public UX tour guide, and trademark/license are ready.
More updates soon as we polish beta and performance. calorietoken.net
"@;

  Email = @"
Subject: CalorieApp Testnet — Public Docs & Legal Snapshot (\$Date)

Hi everyone,

We’ve published a public‑safe documentation snapshot and legal readiness update for CalorieApp Testnet.

Included:
• Official documentation index
• Public overview of our automated UX tour
• Trademark + Custom Dual License

Next steps: beta polish, performance + accessibility improvements, and packaging.

Read more: https://calorietoken.net

Best,
CalorieToken Team
"@
}

$base = Join-Path "$PSScriptRoot" "..\docs\posts\$Date"
New-Item -ItemType Directory -Force -Path $base | Out-Null

foreach ($k in $updates.Keys) {
  $file = Join-Path $base ("{0}.txt" -f $k.ToLower())
  Set-Content -Path $file -Value $updates[$k].Trim() -Encoding UTF8
}

Write-Host ("Saved platform posts to {0}" -f $base) -ForegroundColor Green

# Default clipboard = Twitter
if ($ToClipboard) {
  $twFile = Join-Path $base "twitter.txt"
  Get-Content $twFile | Set-Clipboard
  Write-Host "Copied Twitter text to clipboard" -ForegroundColor Yellow
}

Write-Host "\nQuick copy commands:" -ForegroundColor Cyan
Write-Host ("Get-Content {0} | Set-Clipboard  # twitter" -f (Join-Path $base 'twitter.txt'))
Write-Host ("Get-Content {0} | Set-Clipboard  # telegram" -f (Join-Path $base 'telegram.txt'))
Write-Host ("Get-Content {0} | Set-Clipboard  # discord" -f (Join-Path $base 'discord.txt'))
Write-Host ("Get-Content {0} | Set-Clipboard  # linkedin" -f (Join-Path $base 'linkedin.txt'))
