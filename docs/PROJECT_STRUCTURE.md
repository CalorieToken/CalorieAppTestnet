# Project Structure 🏗️

This document provides an overview of the CalorieApp Testnet codebase structure.

## Directory Tree

```
CalorieAppTestnet/
├── .github/
│   └── workflows/
│       ├── ci.yml              # Main CI pipeline
│       └── ux_tour.yml         # Automated UI/UX testing
│
├── assets/
│   └── images/
│       └── CalorieLogoTranspa.png
│
├── config/
│   ├── buildozer.spec          # Android build config (backup)
│   └── requirements.txt        # Dependencies (backup)
│
├── data/                       # App data directory (runtime)
│
├── docs/
│   ├── archive/                # Historical documentation
│   ├── ui_tour/                # UX Tour test results
│   │   └── 20251117-042836/   # Latest test run
│   ├── FAUCET_TROUBLESHOOTING.md
│   ├── FINAL_BUG_FIX_SUMMARY.md
│   ├── KIVYMD_2.0_UPGRADE.md
│   ├── KV_MODULARIZATION_PHASE_A_COMPLETE.md
│   ├── MODERNIZATION_SUMMARY.md
│   ├── MULTI_FAUCET_IMPLEMENTATION.md
│   ├── README.md               # Documentation index
│   ├── TOKEN_SYSTEM_GUIDE.md
│   ├── TRANSACTION_DISPLAY_GUIDE.md
│   ├── UX_TOUR_COMPLETE.md
│   ├── UX_TOUR_GUIDE.md
│   └── WALLET_SWITCHING_TRANSACTION_HISTORY_FIXES.md
│
├── scripts/
│   ├── clean_wallet_database.py
│   ├── repair_wallet_data.py
│   ├── run.bat                 # Windows launcher
│   ├── run.sh                  # Unix launcher
│   ├── split_kv_files.py       # KV modularization tool
│   └── ux_tour.py              # Automated UI testing
│
├── src/
│   ├── core/
│   │   ├── kv/                 # Modular KV layout files
│   │   │   ├── base.kv
│   │   │   ├── account_choice_screen.kv
│   │   │   ├── account_naming_screen.kv
│   │   │   ├── add_trustline_screen.kv
│   │   │   ├── create_extra_wallet_screen.kv
│   │   │   ├── create_import_wallet_screen.kv
│   │   │   ├── create_wallet_screen.kv
│   │   │   ├── dex_trade_screen.kv
│   │   │   ├── first_use_screen.kv
│   │   │   ├── food_track_screen.kv
│   │   │   ├── import_choice_screen.kv
│   │   │   ├── import_extra_keys_screen.kv
│   │   │   ├── import_keys_screen.kv
│   │   │   ├── intro_screen.kv
│   │   │   ├── keypair_import_screen.kv
│   │   │   ├── login_screen.kv
│   │   │   ├── mnemonic_display_screen.kv
│   │   │   ├── mnemonic_import_screen.kv
│   │   │   ├── mnemonic_verify_screen.kv
│   │   │   ├── nft_mint_screen.kv
│   │   │   ├── send_test_token_screen.kv
│   │   │   ├── send_xrp_screen.kv
│   │   │   ├── settings_screen.kv
│   │   │   ├── wallet_screen.kv
│   │   │   └── wallet_setup_screen.kv
│   │   ├── __init__.py
│   │   └── app.py              # Main application class
│   │
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── AccountChoiceScreen.py
│   │   ├── AccountNamingScreen.py
│   │   ├── AddTrustlineScreen.py
│   │   ├── CreateExtraWalletScreen.py
│   │   ├── CreateImportWalletScreen.py
│   │   ├── CreateWalletScreen.py
│   │   ├── DEXTradeScreen.py
│   │   ├── FirstAccountSetupScreen.py
│   │   ├── FirstUseScreen.py
│   │   ├── FoodTrackScreen.py
│   │   ├── ImportChoiceScreen.py
│   │   ├── ImportExtraKeysScreen.py
│   │   ├── ImportKeysScreen.py
│   │   ├── IntroScreen.py
│   │   ├── KeypairImportScreen.py
│   │   ├── LoginScreen.py
│   │   ├── MnemonicDisplayScreen.py
│   │   ├── MnemonicImportScreen.py
│   │   ├── MnemonicVerifyScreen.py
│   │   ├── NFTMintScreen.py
│   │   ├── SendTestTokenScreen.py
│   │   ├── SendXRPScreen.py
│   │   ├── SettingsScreen.py
│   │   ├── WalletScreen.py
│   │   └── WalletSetupScreen.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── conditional_navigation.py      # Smart navigation system
│   │   ├── currency_utils.py              # Currency formatting
│   │   ├── mnemonic_manager.py            # BIP39 support
│   │   ├── password_field_utils.py        # Password UI helpers
│   │   ├── robust_transaction.py          # Transaction retry logic
│   │   ├── storage_paths.py               # Data storage paths
│   │   ├── token_config.py                # Token definitions
│   │   └── xrpl_client_manager.py         # Multi-server XRPL client
│   │
│   └── __init__.py
│
├── tests/
│   ├── __init__.py
│   ├── test_mnemonic_manager.py
│   ├── test_version.py
│   └── test_xrpl_client_manager.py
│
├── .editorconfig               # Editor settings
├── .flake8                     # Linting configuration
├── .gitignore                  # Git ignore rules
├── .pre-commit-config.yaml     # Pre-commit hooks
├── buildozer.spec              # Android build configuration
├── build_apk.bat               # Windows APK build script
├── build_apk.sh                # Unix APK build script
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guidelines
├── LICENSE                     # Custom dual license
├── main.py                     # Application entry point
├── PROJECT_STATUS.md           # Current project status
├── PROJECT_STRUCTURE.md        # This file
├── pyproject.toml              # Python project config
├── QUICK_START.md              # Quick start guide
├── README.md                   # Project overview
├── requirements.txt            # Python dependencies
├── run.py                      # Alternative entry point
├── setup.py                    # Package setup
├── TODO.md                     # Project roadmap
└── VERSION.py                  # Version information
```

## Key Components

### Core Application

#### `src/core/app.py`
Main application class that:
- Initializes KivyMD Material 3 theme
- Registers all screens
- Manages XRPL connectivity with multi-server failover
- Handles conditional navigation drawer system
- Configures offline mode support

#### `src/core/kv/`
Modular KV layout system (20+ files):
- **base.kv**: Shared classes and root layout
- **<screen>_screen.kv**: Individual screen layouts
- Loaded in deterministic order (base.kv first, then alphabetically)
- Replaces legacy monolithic 4,400-line KV file

### Screens (25+)

All screens follow consistent patterns:
- Material 3 design with AppHeader
- Standardized snake_case naming
- Conditional navigation drawer support
- Offline mode awareness

**Authentication Flow:**
- IntroScreen → FirstUseScreen/LoginScreen → WalletScreen

**Wallet Management:**
- WalletScreen (main hub)
- CreateWalletScreen, ImportKeysScreen
- MnemonicDisplayScreen, MnemonicImportScreen, MnemonicVerifyScreen
- AccountChoiceScreen, WalletSetupScreen

**Transactions:**
- SendXRPScreen (XRP transfers)
- SendTestTokenScreen (generic token transfers)
- AddTrustlineScreen (trustline management)

**Advanced Features:**
- NFTMintScreen (NFT creation)
- DEXTradeScreen (decentralized trading)
- FoodTrackScreen (calorie tracking)
- SettingsScreen (configuration)

### Utilities

#### `xrpl_client_manager.py`
Robust XRPL connectivity:
- Multi-server automatic failover
- Request caching with TTL
- Online/offline detection
- Helper methods for common operations

#### `conditional_navigation.py`
Smart navigation system:
- Creates drawers only for screens that need them
- FAB-based menu access
- Reduces resource usage

#### `mnemonic_manager.py`
BIP39 mnemonic support:
- 12-word phrase generation
- Wallet derivation from mnemonic
- Secure phrase validation

#### `token_config.py`
Generic token system:
- Flexible token definitions
- Supports any XRPL token
- No hardcoded token screens

### Testing

#### `scripts/ux_tour.py`
Automated UI/UX testing:
- 97 comprehensive tests
- Screenshot capture
- Report generation
- CI/CD integration

**Coverage:**
- All 25+ screens
- Form validation
- Dialog behavior
- Offline mode states
- Transaction flows

#### `tests/`
Unit tests:
- Mnemonic manager tests
- XRPL client tests
- Version validation

### Configuration

#### `buildozer.spec`
Android build configuration:
- Package name, version, permissions
- Dependencies and requirements
- Build options and architecture

#### `requirements.txt`
Python dependencies:
- Kivy 2.3.0 + KivyMD 2.0.dev
- xrpl-py, httpx, websockets
- cryptography, mnemonic
- Development tools (pytest, black, flake8)

## Data Flow

### Wallet Creation Flow
```
FirstUseScreen (password) → WalletSetupScreen (choice)
  ↓
CreateWalletScreen (generate mnemonic)
  ↓
MnemonicDisplayScreen (show & copy)
  ↓
MnemonicVerifyScreen (confirm)
  ↓
WalletScreen (ready)
```

### Transaction Flow
```
WalletScreen → SendXRPScreen (enter details)
  ↓
Confirmation Dialog → Submit to XRPL
  ↓
Update balance & history → Return to WalletScreen
```

### XRPL Connectivity
```
App startup → XRPLClientManager
  ↓
Try primary server → Success/Fail
  ↓ (if fail)
Try backup servers → Success/Fail
  ↓ (if all fail)
Enable offline mode → Show offline UI
```

## Build Process

### Development
```bash
python main.py              # Run app
python scripts/ux_tour.py   # Run automated tests
pytest tests/               # Run unit tests
```

### Production (Android APK)
```bash
buildozer android debug     # Debug build
buildozer android release   # Release build
```

## Code Standards

### Python
- Python 3.12+
- Black formatting
- Flake8 linting
- Type hints recommended

### KV Files
- Modular structure (one screen per file)
- Consistent indentation (4 spaces)
- Descriptive IDs for testable widgets
- Follow Material 3 guidelines

### Documentation
- Comprehensive docstrings
- Inline comments for complex logic
- Up-to-date README and guides
- Changelog for all versions

## CI/CD Pipeline

### GitHub Actions Workflows

**ci.yml** (Main CI):
- Linting and formatting checks
- Unit test execution
- Python 3.12 on Ubuntu

**ux_tour.yml** (UI Testing):
- Full UX tour execution
- Screenshot capture
- Test report generation
- Artifact uploads
- Windows environment

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

## Resources

- [Quick Start Guide](QUICK_START.md)
- [UX Tour Guide](docs/UX_TOUR_GUIDE.md)
- [Documentation Index](docs/README.md)
- [Project Roadmap](TODO.md)

---

**Last Updated**: November 17, 2025
