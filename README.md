# CalorieApp 🍎

[![CI](https://github.com/CalorieToken/CalorieAppTestnet/actions/workflows/ci.yml/badge.svg)](https://github.com/CalorieToken/CalorieAppTestnet/actions/workflows/ci.yml)
[![CodeQL](https://github.com/CalorieToken/CalorieAppTestnet/actions/workflows/codeql.yml/badge.svg)](https://github.com/CalorieToken/CalorieAppTestnet/actions/workflows/codeql.yml)
[![UX Tour](https://github.com/CalorieToken/CalorieAppTestnet/actions/workflows/ux_tour.yml/badge.svg)](https://github.com/CalorieToken/CalorieAppTestnet/actions/workflows/ux_tour.yml)
[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](https://github.com/CalorieToken/CalorieAppTestnet)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A mobile-first cryptocurrency wallet and food tracking application built with KivyMD, featuring robust XRPL integration and conditional navigation.

## 🌟 Features

### 🔐 Wallet Functionality
- **Multi-Wallet Support**: Create and import multiple XRPL wallets
- **Mnemonic Recovery**: 12-word BIP39 mnemonic phrase support for wallet backup/recovery
- **Secure Storage**: Encrypted wallet data with password protection
- **Balance Tracking**: Real-time XRP and custom token balances
- **Transaction History**: Complete transaction tracking with visual indicators

### 💸 Transactions
- **XRP Payments**: Send and receive XRP with multi-server failover
- **Token Support**: Generic token system for custom XRPL tokens
- **Trustline Management**: Add and manage XRPL trustlines
- **Robust Connectivity**: Automatic failover between multiple XRPL servers
- **Error Handling**: Graceful degradation with offline mode support

### 🎨 NFT Features
- **NFT Minting**: Create and mint NFTs on the XRPL
- **Custom Metadata**: Full control over NFT properties and metadata

### 📊 DEX Trading
- **Decentralized Exchange**: Trade tokens directly on the XRPL DEX
- **Market Making**: Create and manage trading offers

### 🍽️ Food Tracking
- **Calorie Monitoring**: Track daily food intake and calories
- **Nutrition Data**: Comprehensive food database integration

### ⚙️ Advanced Features
- **Conditional Navigation**: Intelligent navigation system that only creates drawers when needed
- **Performance Optimized**: Resource-efficient design with minimal memory footprint
- **Multi-Server XRPL**: Automatic failover between testnet servers
- **Password Visibility**: Enhanced UX with eye icon toggles

## 🛠️ Technical Stack

- **Frontend**: KivyMD 2.0.dev (master)
- **Backend**: Python 3.12
- **Blockchain**: XRPL (XRP Ledger) Testnet
- **Mnemonic**: BIP39 for 12-word recovery phrases
- **Networking**: httpx with async support
- **Encryption**: cryptography library
- **Data Storage**: shelve (encrypted)

## 🏗️ Project Structure

```
CalorieAppTestnet/
├── README.md              # You are here
├── LICENSE                # Custom dual license
├── main.py                # Application entry point
├── requirements.txt       # Python dependencies
├── setup.py              # Package configuration
├── buildozer.spec        # Android build config
├──
├── .github/              # CI/CD workflows
├── assets/               # Images and resources
├── docs/                 # 📚 All documentation
│   ├── QUICK_START.md
│   ├── CONTRIBUTING.md
│   ├── CHANGELOG.md
│   ├── TODO.md
│   └── ... (guides & references)
├── scripts/              # 🔧 Build & utility scripts
│   ├── ux_tour.py
│   ├── build_apk.bat
│   └── run.py
├── src/                  # 💻 Source code
│   ├── VERSION.py
│   ├── core/
│   ├── screens/
│   └── utils/
└── tests/               # 🧪 Unit tests
```

**Note**: We follow industry best practices with a clean root directory. See [Repository Organization](docs/REPOSITORY_ORGANIZATION.md) for details.

### Modular KV Layout (2025 Modernization)
The legacy monolithic `calorieapptestnet.kv` (≈4,400 lines) has been fully removed and replaced with a **modular KV system** located in `src/core/kv/`:

```
src/core/kv/
   base.kv                  # RootLayout + shared drawer item classes
   wallet_screen.kv         # Wallet UI
   send_xrp_screen.kv       # XRP send flow
   settings_screen.kv       # Settings
   login_screen.kv          # Authentication
   ... (20+ additional screen .kv files)
```

Loading order is deterministic:
1. `base.kv` first (shared classes)
2. All other `*.kv` files alphabetically

Benefits:
- Cleaner diffs & easier collaboration
- Eliminates duplicate widget warnings
- Faster targeted layout iteration
- Simplifies future theming upgrades

No fallback to the old monolithic file remains; if a new screen is added, just create a `snake_case_screen.kv` in this directory.

### Conditional Navigation System
The app features an intelligent navigation system that creates navigation drawers only for screens that need them:

**Screens WITH Navigation Drawers:**
- Wallet Screen
- Settings Screen  
- Food Tracking Screen
- DEX Trading Screen
- NFT Minting Screen

**Screens WITHOUT Navigation Drawers:**
- Login Screen
- Transaction Screens (Send XRP, Send Tokens)
- Setup/Import Screens
- Intro/First Use Screens
- Mnemonic Display/Verify Screens

### XRPL Multi-Server Failover
Robust connectivity with automatic failover:
1. Primary: `https://testnet.xrpl-labs.com`
2. Backup: `https://s.altnet.rippletest.net:51234`
3. Backup: `https://testnet.xrplapi.com`
4. Backup: `https://xrplcluster.com`

### XRPL Response Caching
Lightweight in-memory caching for select XRPL requests (e.g. `ServerInfo`) reduces redundant network calls and stabilizes performance under intermittent connectivity. Cache entries automatically expire after a short TTL.

## 🚀 Getting Started

👉 **See the [Quick Start Guide](docs/QUICK_START.md) for detailed setup instructions.**

### Prerequisites
- Python 3.12+
- pip package manager

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CalorieToken/CalorieAppTestnet.git
   cd CalorieAppTestnet
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

### Building APK (Android)

1. **Install Buildozer:**
   ```bash
   pip install buildozer
   ```

2. **Build APK:**
   ```bash
   buildozer android debug
   ```

## 📱 Usage

### First Time Setup
1. Launch the app
2. Choose to create a new wallet or import existing keys
3. Set up your secure password
4. Your wallet is ready to use!

### Sending Transactions
1. Navigate to the Wallet screen
2. Click "Send XRP" or token buttons
3. Enter recipient address and amount
4. Confirm transaction

### Food Tracking
1. Access the Food Tracker from the navigation menu
2. Log your meals and track calories
3. Monitor your daily nutrition goals

## 🔧 Development

### Project Structure
```
CalorieAppTestnet/
├── main.py                 # Application entry point
├── run.py                  # Alternative run script
├── buildozer.spec          # Android build configuration
├── requirements.txt        # Python dependencies
├── src/
│   ├── core/
│   │   ├── app.py          # Main application class
│   │   └── kv/                  # Modular KV layout files (replaces monolithic .kv)
│   ├── screens/            # All screen implementations
│   │   ├── WalletScreen.py
│   │   ├── SendXRPScreen.py
│   │   ├── SendTestTokenScreen.py
│   │   ├── MnemonicDisplayScreen.py
│   │   └── ... (25+ screens)
│   └── utils/              # Utility modules
│       ├── xrpl_client_manager.py    # XRPL connectivity
│       ├── conditional_navigation.py # Navigation system
│       ├── mnemonic_manager.py       # BIP39 mnemonic handling
│       ├── password_field_utils.py   # UI utilities
│       ├── robust_transaction.py     # Transaction handling
│       └── token_config.py           # Token configuration
├── assets/                 # App assets and images
│   └── images/            # Logo and UI images
├── config/                 # Configuration files
├── scripts/               # Utility scripts
└── docs/                  # Documentation
```

### Key Components

- **`XRPLClientManager`**: Handles XRPL connectivity with automatic failover
- **`ConditionalNavigationDrawer`**: Intelligent navigation system
- **`PasswordFieldWithToggle`**: Enhanced password input with visibility toggle
- **`robust_submit_and_wait`**: Transaction submission with retry logic

## 🧪 Testing

### Automated UX Tour
The app includes a comprehensive automated testing framework that validates all screens, flows, and features:

- **97 Tests**: Complete coverage of all UI components and flows
- **100% Pass Rate**: All tests passing in latest run
- **Screenshots**: Automated capture of all screens for visual verification
- **CI Integration**: Runs automatically on every PR and commit

Run the UX tour locally:
```bash
python scripts/ux_tour.py
```

Reports and screenshots are saved to `docs/ui_tour/<timestamp>/`

For more information, see the [UX Tour Guide](docs/UX_TOUR_GUIDE.md).

See also:
- [Project Status](docs/PROJECT_STATUS.md) - Current development state
- [Changelog](docs/CHANGELOG.md) - Version history
- [Roadmap](docs/TODO.md) - Future plans

### Manual Testing
The app has been extensively tested with:
- ✅ Navigation flow testing across all screens
- ✅ XRPL connectivity and failover scenarios
- ✅ Wallet creation and import processes
- ✅ Transaction sending and receiving
- ✅ Performance optimization validation
- ✅ Offline mode functionality

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](docs/CONTRIBUTING.md) for:
- Code style guidelines
- Development setup
- Testing requirements
- Pull request process

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌐 XRPL Testnet

This application uses the XRPL Testnet for development and testing. Testnet XRP has no real-world value and is used solely for testing purposes.

## 🔗 Links

- [XRPL Documentation](https://xrpl.org/)
- [KivyMD Documentation](https://kivymd.readthedocs.io/)
- [Buildozer Documentation](https://buildozer.readthedocs.io/)

## 🆘 Support

For issues and questions:
- Open an issue on GitHub
- Check the documentation
- Review existing issues and solutions

---

**Built with ❤️ for the XRPL community**