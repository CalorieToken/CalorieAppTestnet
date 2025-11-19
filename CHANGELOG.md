## [1.1.2] - 2025-11-19

### Added
- Dynamic social image generator with edge-to-edge typography (font fitting, glow)
- Consolidated social copy file (`docs/SOCIAL_COPY_2025-11-19.md`)
- Visual audit checklist (`docs/VISUAL_AUDIT_CHECKLIST_v1.1.2.md`)
- PR body template for visual refinement branch

### Changed
- Updated Telegram community invite link across all docs/config metadata
- Enhanced marketing asset generation performance (coarser gradient steps)
- Version badge styling widened for higher impact

### Notes
- This release focuses on outward-facing visual communication and readiness for social distribution.
- Remaining planned refinement tasks moved to upcoming version placeholder.

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

### Repository Hardening & Public-Safe Docs

#### Added
- OFFICIAL_PROJECT_DOCS.md: Canonical, public-safe documentation index
- STATUS_UPDATE_2025-11-18.md: Public snapshot of progress

#### Changed
- README.md: Removed links to private reference files; added official docs index
- docs/README.md: Switched to external references; added official docs index
- .gitignore: Allowlisted public UX tour guides while keeping internal files private

#### Privacy
- Reaffirmed separation between public documentation and private implementation/testing artifacts

---
# Changelog

All notable changes to CalorieApp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-11-18

### 🎉 Official CalorieToken Branding Integration

**Major Update:** This release officially integrates CalorieToken® branding, legal compliance, and trademark protections as we move toward public launch.

### Added

#### Legal & Compliance
- ✅ **Custom Dual License** - Clarified licensing terms for personal vs. commercial use
- ✅ **Trademark Guidelines** - Official CalorieToken® trademark usage policies (EUIPO registered)
- ✅ **Legal Entity Information** - Chamber of Commerce KVK: 84216352 (Netherlands)
- ✅ **Official Project Links** - Comprehensive links to CalorieToken resources

#### CalorieToken Integration
- ✅ **Official XRPL Token Details**
  - Mainnet Issuer: `rNqGa93B8ewQP9mUwpwqA19SApbf62U7PY`
  - Currency: Calorie ($CAL)
  - Network: XRP Ledger Mainnet + Testnet support
- ✅ **Project Reference Documentation** - Complete token specifications
- ✅ **Community Links** - Twitter, Telegram, Discord, and more
- ✅ **Trading Platform Integration** - Links to Sologenic, XPMarket, LiveCoinWatch

#### Developer Resources
- ✅ **GitHub Funding Configuration** - Support development via XRPL
- ✅ **Enhanced Metadata** - Updated `pyproject.toml` and `setup.py`
- ✅ **Official Website Badge** - Direct link to calorietoken.net

### Changed

#### Documentation
- 🔄 **README.md** - Added CalorieToken integration section and corrected license badge
- 🔄 **LICENSE** - Enhanced with trademark notices and official contact information
- 🔄 **Project Metadata** - Aligned all package information with CalorieToken branding

#### Branding
- 🎨 **Badge Updates** - Fixed license badge from MIT to Custom Dual
- 🎨 **Footer Information** - Added CalorieToken trademark notice
- 🎨 **Contact Details** - Official info@calorietoken.net throughout

### Security
- 🔒 **Issuer Verification** - Documented official XRPL issuer address to prevent fake tokens
- 🔒 **Legal Protection** - Trademark registration information for brand protection

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
