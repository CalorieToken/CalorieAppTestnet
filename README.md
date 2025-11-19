# CalorieApp 🍎

[![CI](https://github.com/CalorieToken/CalorieAppTestnet/actions/workflows/ci.yml/badge.svg)](https://github.com/CalorieToken/CalorieAppTestnet/actions/workflows/ci.yml)
[![CodeQL](https://github.com/CalorieToken/CalorieAppTestnet/actions/workflows/codeql.yml/badge.svg)](https://github.com/CalorieToken/CalorieAppTestnet/actions/workflows/codeql.yml)
[![UX Tour](https://github.com/CalorieToken/CalorieAppTestnet/actions/workflows/ux_tour.yml/badge.svg)](https://github.com/CalorieToken/CalorieAppTestnet/actions/workflows/ux_tour.yml)
[![Version](https://img.shields.io/badge/version-1.1.1-blue.svg)](https://github.com/CalorieToken/CalorieAppTestnet)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Custom%20Dual-orange.svg)](LICENSE)
[![Website](https://img.shields.io/badge/website-calorietoken.net-green.svg)](https://calorietoken.net)
[![XRPL](https://img.shields.io/badge/XRPL-Mainnet%20%26%20Testnet-blue.svg)](https://xrpl.org/)

A mobile-first cryptocurrency wallet and food tracking application for **CalorieToken** on the XRP Ledger, built with KivyMD.

> **Latest Update (2025-11-18 – v1.1.1):** Repository hardening, public-safe documentation index, UX layout consistency, security enhancements. See [CHANGELOG](docs/CHANGELOG.md#111---2025-11-18). Pending merge from branch `chore/repo-hardening`.

## 🪙 CalorieToken Integration

**Official CalorieToken XRPL Token:**
- **Currency:** Calorie
- **Ticker:** $CAL
- **Issuer:** `rNqGa93B8ewQP9mUwpwqA19SApbf62U7PY`
- **Network:** XRP Ledger Mainnet (Testnet for development)
- **Website:** [calorietoken.net](https://calorietoken.net)
- **Whitepaper:** [Read here](https://calorietoken.net/index.php/whitepaper/)

> **"Aiming to be the world's food token"**  
> CalorieToken targets the worldwide food & beverage industry with blockchain-based payment solutions.

**Learn More:**
- [Official Documentation Index](docs/OFFICIAL_PROJECT_DOCS.md)
- [Trademark Guidelines](docs/TRADEMARK.md) - Usage policies
- [CalorieToken Website](https://calorietoken.net) - Official resources

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

**Note**: We follow industry best practices with a clean root directory. Additional internal references are intentionally withheld until stable release.

### Layout Organization (Modernized)
The UI is organized into maintainable, screen-focused KV files with a clear loading order. This approach improves iteration speed and keeps layouts consistent without exposing internal file structure. The modernized setup enables:
- Cleaner diffs and easier collaboration
- Reduced duplication and warnings
- Faster targeted layout updates

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

## 🚀 Getting Started (Public-Safe)

> Execution and build instructions are intentionally withheld until a stable, review-approved release milestone. The repository at this stage is for transparency of progress, documentation, and ongoing refactor history — not for end-user execution or distribution.

If you are an authorized collaborator and require internal run/build procedures, request access privately (info@calorietoken.net). All prior direct run examples (e.g. `python main.py`, `buildozer android debug`) have been removed to prevent premature usage of unfinished systems.

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

### Development Viewport & Responsive Overrides
During active development and automated UX tours we often want a consistent, phone-sized viewport while still preserving full adaptive behavior for tablets and desktops in production.

Environment overrides (all optional):

| Variable | Example | Purpose |
|----------|---------|---------|
| `DEV_PHONE_VIEWPORT` | `390x844` | Forces window size (if `APP_FORCE_WIDTH/HEIGHT` not set) to a modern phone logical resolution (portrait enforced). |
| `FORCE_SIZE_CLASS` | `sm` / `phone` | Pins responsive size class regardless of window width (use `phone` as alias for `sm`). |
| `TOUR_FORCE_PHONE` | `1` | In UX tour runs auto-sets `DEV_PHONE_VIEWPORT=390x844` and `FORCE_SIZE_CLASS=sm` if unset. |
| `TOUR_PHONE_WIDTH` / `TOUR_PHONE_HEIGHT` | `414` / `896` | Fine-grained control for UX tour window size when `TOUR_FORCE_PHONE` is enabled. |

Example (PowerShell):
```powershell
$env:DEV_PHONE_VIEWPORT="390x844"; $env:FORCE_SIZE_CLASS="sm"; python -B scripts/complete_ux_tour.py
```

Production builds simply omit these variables and the app reverts to automatic breakpoint detection (`xs`, `sm`, `md`, `lg`, `xl`). The responsive system caches scaling factors to minimize recomputation while keeping layout adjustments correct on window resize.

Breakpoints remain unchanged ensuring cross-platform compatibility; overrides are strictly opt-in for development convenience.

### Debug Overlay (Development Only)
Activation mechanics exist but invocation commands are withheld pre-release. Overlay shows breakpoint class, scaling factors, and dimensions when enabled internally.

This displays a small badge in the top-right corner showing:
- Current size class (xs/sm/md/lg/xl)
- Lock icon (🔒) when `FORCE_SIZE_CLASS` is active
- DP and font scale factors
- Current window dimensions

The overlay updates in real-time during window resizes and is automatically removed in production (when `DEBUG_RESPONSIVE` is unset).

### CI Testing Strategy
Automated UX validation runs are supported to help catch regressions across device sizes. Details of internal test tooling are intentionally minimized here for security and competitive reasons. See `docs/UX_TOUR_GUIDE.md` for a public overview of the process.

## 🧪 Testing

### Automated UX Tour
We use an automated UX tour to validate major screens and flows and to generate visual reports for review. High-level, public-safe documentation is available here:

- [UX Tour Guide](docs/UX_TOUR_GUIDE.md)

Implementation details and internal scripts are withheld to protect the project’s integrity until formal release.

See also:
- [Project Status](docs/PROJECT_STATUS.md) - Current development state
- [Changelog](docs/CHANGELOG.md) - Version history
- [Roadmap](docs/TODO.md) - Future plans

### UI/UX References (Public)
- KivyMD Documentation: https://kivymd.readthedocs.io/
- Kivy Documentation: https://kivy.org/doc/stable/
- Material Design 3: https://m3.material.io/

### Manual Testing
Internal test cycles include navigation, XRPL connectivity/failover simulation, wallet creation/import flows, transaction lifecycle validation, performance sampling, and offline mode handling. Detailed invocation steps are withheld until stable release.

## 🤝 Contributing

We welcome contributions! Please read our [Contributing Guide](docs/CONTRIBUTING.md) for:
- Code style guidelines
- Development setup
- Testing requirements
- Pull request process

## 📄 License

This project is licensed under a **Custom Dual License** - see the [LICENSE](LICENSE) file for details.

**Summary:**
- **Personal Use:** Permitted for educational, research, and non-commercial purposes
- **Commercial/Public Use:** Requires explicit written permission from CalorieToken

**Contact for commercial licensing:** info@calorietoken.net

**Trademark Notice:** CalorieToken® and related branding are registered trademarks. See [TRADEMARK.md](docs/TRADEMARK.md).

## 🌐 XRPL Testnet

This application uses the XRPL Testnet for development and testing. Testnet XRP has no real-world value and is used solely for testing purposes.

## 🔗 Links

### Official CalorieToken Resources
- [CalorieToken Website](https://calorietoken.net)
- [Whitepaper](https://calorietoken.net/index.php/whitepaper/)
- [Twitter/X](https://twitter.com/CalorieToken)
- [Telegram Community](https://t.me/+7YxaKdQYWNA0NDA0)
- [Discord Developers](https://discord.gg/hcjJgdyDGd)
- [All Links (Linktree)](https://linktr.ee/CalorieToken)

### Technical Documentation
- [XRPL Documentation](https://xrpl.org/)
- [KivyMD Documentation](https://kivymd.readthedocs.io/)
- [Buildozer Documentation](https://buildozer.readthedocs.io/)

### Trading & Token Info
- [Sologenic DEX](https://sologenic.org/trade?network=mainnet&market=43616C6F72696500000000000000000000000000%2BrNqGa93B8ewQP9mUwpwqA19SApbf62U7PY%2FXRP)
- [XPMarket](https://xpmarket.com/token/Calorie-rNqGa93B8ewQP9mUwpwqA19SApbf62U7PY)
- [LiveCoinWatch](https://www.livecoinwatch.com/price/Calorie-CAL)

## 🆘 Support

**For App/Development Issues:**
- Open an issue on [GitHub](https://github.com/CalorieToken/CalorieAppTestnet/issues)
- Check the [documentation](docs/README.md)
- Join [Discord Developers Server](https://discord.gg/hcjJgdyDGd)

**For CalorieToken Project:**
- Email: info@calorietoken.net
- Telegram: [Community Chat](https://t.me/+7YxaKdQYWNA0NDA0)
- Twitter: [@CalorieToken](https://twitter.com/CalorieToken)

---

**Built with ❤️ for CalorieToken and the XRPL community**

---

**CalorieToken® | Chamber of Commerce KVK: 84216352**  
*Trademark registered with EUIPO | See [TRADEMARK.md](docs/TRADEMARK.md) for usage guidelines*