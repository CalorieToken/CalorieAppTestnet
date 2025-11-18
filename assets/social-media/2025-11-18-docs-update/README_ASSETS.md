# Social Media Visual Assets (2025-11-18 Docs Update)

This folder should contain finalized visual creatives for the November 18, 2025 documentation + UX hardening announcement.

## Required Image Files
Place these exact filenames (PNG preferred, 72–150 DPI, RGB):

1. `square-1080x1080.png` – Primary universal post (Twitter/X, Instagram feed, Telegram, Discord)
2. `story-1080x1920.png` – Vertical story/reel (Instagram Story, LinkedIn Story, future YouTube Shorts teaser)
3. `twitter-1200x628.png` – Optimized landscape card for Twitter/X link amplification
4. `linkedin-1200x627.png` – Professional banner for LinkedIn update

Optional (future):
5. `email-header-1200x400.png` – Long form newsletter header
6. `youtube-community-1000x1000.png` – Square variant tuned for YouTube community posts

## Brand Style Checklist
Color Palette:
- Primary Green: `#00A651`
- Navy / Deep Blue: `#1E3A8A`
- Support Blue: `#3B82F6`
- Accent Yellow: `#FCD34D`

Typography Guidance (AI tools approximate):
- Headline: Bold geometric (Montserrat / Poppins style)
- Subtext: Regular sans (Inter / Open Sans style)
- Avoid overly condensed fonts; maintain readability on mobile.

## Mandatory Visual Elements
- CalorieToken logomark (shield / token emblem) top-left or centered
- Clear headline: “CalorieApp UX & Docs Upgrade” or variation
- Sub-highlight: “Security • Speed • User Experience” (bullet separators ok)
- Light watermark grid or subtle diagonal energy pattern (do not overpower text)
- High contrast word “LIVE” or “READY” tag (optional badge)

## AI Prompt Examples (Microsoft Designer / Copilot)
Paste and adapt per format:

Universal Square:
"Minimal professional fintech app announcement graphic, dark navy background (#1E3A8A) with subtle gradient, vibrant green accent (#00A651), CalorieToken shield logo, headline 'CalorieApp UX & Docs Upgrade', subtext 'Security • Speed • User Experience', clean geometric layout, modern material design shadows, sharp vector icons, high contrast, center composition, no stock photos, crisp UI framing"

Story Vertical:
"Vertical fintech app update story, dark navy to deep blue gradient background, CalorieToken shield logo at top, large bold headline 'Massive UX & Docs Upgrade', green accent bars (#00A651), subtle animated energy lines, modern material style, spacious layout, legible text, high resolution, no photorealistic images"

Twitter Card:
"Landscape professional fintech upgrade banner, dark navy background (#1E3A8A), green accent corner elements (#00A651), headline 'CalorieApp UX & Docs Upgrade', smaller subline 'Security • Speed • User Experience', minimal, clean, strong contrast, modern material aesthetic, subtle grid texture"

LinkedIn Banner:
"Professional clean SaaS-style banner, dark navy background, thin green accent line (#00A651), CalorieToken logo left, headline 'CalorieApp UX & Docs Upgrade', subtext 'Documentation Hardening • Performance • Accessibility', balanced whitespace, executive feel, minimal, high clarity"

## Asset Quality Review Before Commit
Run the asset check script:
```powershell
pwsh tools/check_social_assets.ps1
```
Ensure all required files show as PRESENT before committing.

## Commit Guidance
Once assets added:
```powershell
git add assets/social-media/2025-11-18-docs-update
git commit -m "assets: add finalized social visuals for 2025-11-18 docs + UX upgrade"
git push origin chore/repo-hardening
```

## Do Not Include
- Editable source files (.psd, .ai) unless intentionally open-sourced
- Images containing unreleased feature screenshots
- Raw AI generations without final cropping/alignment

## Version Tag
Release Cycle: `v1.1.1` Docs & UX Hardening
Date: 2025-11-18
