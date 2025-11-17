# Changelog

All notable changes to CalorieApp Testnet will be documented in this file.

# Changelog

All notable changes to CalorieApp Testnet will be documented in this file.

## [Unreleased]

### Added
- **Automated UX Tour**: Comprehensive UI/UX testing framework with 97 tests (100% pass rate)
- **CI/CD Integration**: GitHub Actions workflow for automated UX Tour on every PR/push
- **Offline Mode Testing**: Extended offline validation across all network-dependent screens
- **Documentation**: UX Tour Guide with complete usage and extension examples
- **Screen Name Standardization**: Unified snake_case naming convention across codebase

### Changed
- Updated .gitignore for better artifact and cache management
- Reorganized documentation with clear hierarchy and index
- Enhanced README with UX Tour badge and testing section
- Updated TODO.md to reflect completed improvements

### Removed
- Old UX Tour test runs (kept only latest)
- Backup KV files (calorieapptestnet.kv.old)
- Crash logs and temporary wallet data from root
- All __pycache__ directories
- Moved ACCOUNT_SECTION_FIXES.md to archive

### Fixed
- Import Extra Keys screen name mismatch (now import_extra_keys_screen)
- Conditional navigation configuration updated for renamed screens

### Changed
- Renamed `CalorieAppTestnetV11` class to `CalorieAppTestnet` for professional naming
- Renamed `calorieapptestnetv11.kv` to `calorieapptestnet.kv` for consistency
- Updated buildozer.spec version to 1.1.0 with correct requirements
- App title now displays version dynamically (e.g., "CalorieApp Testnet v1.1.0")
- Applied professional version naming throughout project

### Fixed
- Removed `shelve` from buildozer.spec requirements (it's a Python built-in)
- Added missing requirements to buildozer.spec (websockets, mnemonic, requests)
- Updated setup.py to include assets in package data

### Removed
- Temporary documentation files (CLEANUP_SUMMARY.md, POLISH_SUMMARY.md)

### Added
- Modern unified header layout across all screens with centered titles and visible CalorieApp logo
- Transaction history visual indicators (↑ sent, ↓ received, • other)
- Short peer address display in transaction history (first 6...last 4 characters)
- Bottom-left floating action button for menu access on drawer-enabled screens
- Decoded currency display in transaction history

### Changed
- Replaced all deprecated MDTopAppBar instances with modern MDBoxLayout headers
- Wrapped CalorieApp logo in light circular card (40dp radius) for better visibility
- Updated main.py with cleaner docstring and structure
- Consolidated old completion reports to docs/archive directory

### Removed
- Duplicate header layouts (removed old 3-column and in-page custom headers)
- Top-left menu buttons (replaced with bottom-left FAB)
- All deprecated MDBottomAppBar instances
- Old test/demo scripts: demo_mnemonic_improvements.py, test_*.py files
- Temporary files: fix_kv_bom.py, _header_snippet.txt, wallet_data.bak
- Automation backup directory from November 16, 2025
- All __pycache__ directories

### Fixed
- CalorieApp logo visibility with light background
- Layout consistency across all 25+ screens
- Deprecated KivyMD component warnings

## [1.1.0] - 2025-11-16

### Added
- Comprehensive mnemonic (BIP39) support for wallet backup and recovery
- 12-word recovery phrase generation and import
- Full-screen mnemonic display with copy functionality
- Interactive mnemonic verification during wallet creation
- Mnemonic-based wallet import flow
- Generic token system for flexible custom token support
- Token configuration system (token_config.py)
- Generic SendTestTokenScreen for all custom tokens
- Multiple XRPL testnet faucet support with automatic failover
- AddTrustlineScreen for managing XRPL trustlines
- Transaction display improvements with better formatting
- Currency code decoding for hex-encoded XRPL currencies

### Changed
- Modernized XRPL connectivity with robust multi-server failover
- Updated wallet creation flow to include mnemonic generation
- Enhanced wallet import to support both keypair and mnemonic methods
- Improved transaction history parsing and display
- Updated all screens to use unified styling patterns

### Removed
- Hardcoded token screens (SendLipisaScreen, SendCalorieTestScreen)
- Token-specific methods and flags (LIPISA_OFFLINE, CALORIETEST_OFFLINE)
- Deprecated older wallet import methods

### Fixed
- XRPL server connectivity issues with automatic failover
- Transaction history display errors
- Wallet switching transaction history bugs
- UI consistency across all screens

## [1.0.0] - 2025-10-31

### Added
- Initial release with core wallet functionality
- Multi-wallet support (create and import wallets)
- Encrypted wallet storage with password protection
- XRP payment sending and receiving
- Real-time balance tracking
- Transaction history
- NFT minting functionality
- DEX trading interface
- Food tracking features
- Conditional navigation system
- Password visibility toggles
- Settings screen with configuration options

### Technical Features
- KivyMD 1.2.0 Material Design UI
- Python 3.12 backend
- XRPL testnet integration
- Encrypted data storage with shelve
- httpx async networking
- Multi-server XRPL failover system

### Screens Implemented
- IntroScreen / FirstUseScreen
- LoginScreen
- WalletScreen
- CreateWalletScreen / ImportKeysScreen
- SendXRPScreen
- NFTMintScreen
- DEXTradeScreen
- FoodTrackScreen
- SettingsScreen
- WalletSetupScreen
- FirstAccountSetupScreen

---

## Legend

- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerability fixes
