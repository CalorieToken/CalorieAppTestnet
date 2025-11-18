# README: Social Media Posting Tools

## Quick Start

Generate and copy social posts with one command:

```powershell
# Copy Twitter post to clipboard
pwsh tools/copy_social_post.ps1 -Platform twitter -CopyToClipboard

# See LinkedIn post (no clipboard)
pwsh tools/copy_social_post.ps1 -Platform linkedin
```

## Available Platforms

- `twitter` - Twitter/X
- `telegram` - Telegram community
- `discord` - Discord announcements
- `linkedin` - LinkedIn professional
- `instagram` - Instagram feed/story
- `youtube` - YouTube community tab
- `email` - Email newsletter

## Visual Assets

**Location:** `assets/social-media/<date>-docs-update/`

**Required Images:**
- `square-1080x1080.png` - Universal (Instagram, Twitter, etc.)
- `story-1080x1920.png` - Stories/Reels vertical
- `twitter-1200x628.png` - Twitter card
- `linkedin-1200x627.png` - LinkedIn banner

## Generating Images

See `docs/posts/VISUAL_CONCEPTS_<date>.md` for:
- Design specifications
- AI prompts (Microsoft Designer, Copilot)
- Color palette (#00A651 green, #1E3A8A navy)
- Layout concepts

### Quick AI Prompt (Main Visual)

```
Create a clean social media post for CalorieToken blockchain project. Split design: top half bright green (#00A651), bottom half navy blue (#1E3A8A). CalorieToken logo at top center in white. Title "CalorieApp Testnet" below logo. Middle section has 3 white icons in a row: document, checkmark, lock, with labels "Official Docs", "Legal Ready", "Trademark ®". Bottom text "Public Snapshot Live" in white, "November 18, 2025" in light blue, website "calorietoken.net" in yellow. Modern, professional, clean style. Square format 1080x1080.
```

## Full Workflow

1. **Generate posts:**
   ```powershell
   pwsh tools/generate_social_posts.ps1 -ToClipboard
   ```

2. **Generate images:**
   - Use Microsoft Designer/Copilot with prompts from `VISUAL_CONCEPTS_<date>.md`
   - Save to `assets/social-media/<date>-docs-update/`

3. **Copy & post:**
   ```powershell
   # For each platform:
   pwsh tools/copy_social_post.ps1 -Platform twitter -CopyToClipboard
   # Paste text + upload image
   ```

4. **Commit (optional):**
   ```powershell
   git add assets/social-media/<date>-docs-update/
   git commit -m "social: add visual assets for <date> campaign"
   ```

## File Structure

```
docs/posts/
├── SOCIAL_POSTS_<date>.md          # All copy blocks
├── POSTING_GUIDE_WITH_VISUALS.md   # Complete guide
├── VISUAL_CONCEPTS_<date>.md       # Design specs & prompts
└── <date>/
    ├── twitter.txt
    ├── telegram.txt
    ├── discord.txt
    ├── linkedin.txt
    ├── instagram.txt
    ├── youtube.txt
    └── email.txt

assets/social-media/<date>-docs-update/
├── square-1080x1080.png
├── story-1080x1920.png
├── twitter-1200x628.png
└── linkedin-1200x627.png

tools/
├── generate_social_posts.ps1       # Creates text files
├── copy_social_post.ps1            # Copy to clipboard
└── prepare_public_commit.ps1       # Stages commit
```

## Tips

- **Hashtags:** Use #XRPL #KivyMD #CalorieToken for Twitter
- **Links:** Always include calorietoken.net
- **Images:** Keep professional, clean, on-brand (green/blue palette)
- **Timing:** Post across platforms within same day for consistency
- **Engagement:** Monitor first 2 hours, reply to comments

## Troubleshooting

**Q: Image folder not found?**  
A: Run `New-Item -ItemType Directory -Force -Path "assets\social-media\<date>-docs-update"`

**Q: Text files not generated?**  
A: Run `pwsh tools/generate_social_posts.ps1` first

**Q: Need to regenerate with different date?**  
A: Use `-Date` parameter: `pwsh tools/generate_social_posts.ps1 -Date "2025-12-01"`

---

**Last Updated:** 2025-11-18  
**Version:** 1.0
