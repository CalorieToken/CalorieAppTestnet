## [1.1.2] - 2025-11-19

### Added
- Dynamic social image generator (`tools/generate_social_image.py`) with edge‑to‑edge adaptive typography & glow layers
- Consolidated multi‑platform social copy (`docs/SOCIAL_COPY_2025-11-19.md`)
- Visual audit checklist (`docs/VISUAL_AUDIT_CHECKLIST_v1.1.2.md`) for structured refinement tracking
- PR body template (`docs/PR_BODY_feature_visual_refinement_v1.1.2.md`)
- Deprecated branch index (`docs/DEPRECATED_BRANCHES.md`)

### Changed
- README & public docs: removal of premature run/build instructions (pre‑release policy enforcement)
- Global Telegram community link updated across all documentation & metadata
- Social image generation performance (coarser gradient); robust font discovery (Windows + Pillow bundles)
- Version badge updated to 1.1.2

### Removed
- Direct executable examples (`python main.py`, `buildozer android debug`) from public README/docs

### Security / Compliance
- Reaffirmed pre‑release distribution boundaries (no APK guidance until stability milestone)

### Notes
- Focused on outward visual communication & brand consistency rather than core feature expansion.
- Pending refinement tasks deferred to 1.1.3.

## [1.1.3] - Unreleased

### Planned / In Progress
- Visual refinement pass (responsive polish, spacing normalization)
- Performance profiling for XRPL client manager
- Story/Reel social asset generation automation
- Optional CalorieDB sync activation & index optimization

### Potential Additions
- WalletConnect (Phase 1 activation)
- Accessibility contrast audit & fixes
- Image asset compression pipeline

---
## [1.1.1] - 2025-11-18

### Added
- `OFFICIAL_PROJECT_DOCS.md` public‑safe index
- `STATUS_UPDATE_2025-11-18.md` progress snapshot

### Changed
- README & docs index alignment; canonical documentation entry point introduced
- `.gitignore` adjustments: whitelist safe UX tour guides, preserve internal artifacts privacy

### Privacy
- Reinforced segregation between public documentation & internal implementation/testing assets

---
# Changelog

All notable changes to CalorieApp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-16

### Added
- Mnemonic (BIP39) 12‑word wallet recovery system
- Generic token framework + trustline management screen
- Unified UI headers & transaction visual indicators
- Multi‑server XRPL failover connectivity layer
- Password visibility toggle components
- Initial NFT & DEX screen scaffolds
- CalorieToken branding integration (issuer verification, badges, trademark docs)

### Changed
- README & LICENSE updated for Custom Dual License + trademark notice
- Consolidated header/layout strategy across 25+ screens
- Transaction history formatting & short address styling

### Security / Compliance
- Official issuer address documented to mitigate spoofing
- Custom Dual License + trademark usage guidelines published

---

## [1.0.0] - 2025-11-01

### 🚀 Initial Public Release (Testnet)

**First official release** of CalorieApp featuring multi-wallet XRPL support and food tracking capabilities.

### Features

#### Wallet Functionality
- Multi-wallet support on XRPL Testnet
- 12-word BIP39 mnemonic recovery phrases
- Secure encrypted wallet storage
- Real-time balance tracking

#### Transactions
- XRP send/receive capabilities
- Custom token support framework
- Transaction history tracking
- Multi-server failover (testnet)

#### Additional Features
- NFT minting interface
- DEX trading screens
- Food tracking integration
- Modern KivyMD 2.0 UI

#### Technical
- Python 3.12 support
- KivyMD 2.0 framework
- Conditional navigation system
- Responsive design (phone-first)

---

## Release Notes

### Versioning Strategy

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR** version: Incompatible API changes
- **MINOR** version: Backwards-compatible functionality additions
- **PATCH** version: Backwards-compatible bug fixes

### Development Status

**Current Phase:** Beta Development (Testnet)

🚧 **Note:** This application is under active development. Features and functionality are subject to change. Always verify XRPL issuer addresses to avoid fake tokens.

### Trademark Notice

CalorieToken® and "$CAL" are registered trademarks of CalorieToken (KVK: 84216352). See [TRADEMARK.md](docs/TRADEMARK.md) for usage guidelines.

### License

This project uses a **Custom Dual License**:
- ✅ Personal/Educational use: Permitted
- ⚠️ Commercial/Public use: Requires written permission

Contact: info@calorietoken.net

---

**For complete version history, see individual release notes in the repository.**

**Official Resources:**
- 🌐 Website: https://calorietoken.net
- 📄 Whitepaper: https://calorietoken.net/index.php/whitepaper/
- 🐦 Twitter: [@CalorieToken](https://twitter.com/CalorieToken)
- 💬 Telegram: [Community](https://t.me/+7YxaKdQYWNA0NDA0)
