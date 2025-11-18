# 🚀 CalorieApp Quick Start Guide

## 📱 Running the App

### Option 1: Enhanced Launcher (Recommended)
```bash
python run.py
```

### Option 2: Original Launcher  
```bash
python main.py
```

## 🔧 Development Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Application
```bash
python run.py
```

## 📱 Building APK

### Windows
```bash
# Run the build script
build_apk.bat
```

### Linux/macOS
```bash
# Make script executable
chmod +x build_apk.sh

# Run the build script
./build_apk.sh
```

### Manual Build
```bash
# Install buildozer
pip install buildozer

# Build debug APK
buildozer android debug

# Build release APK
buildozer android release
```

## 🌐 GitHub Upload

### Initial Upload
```bash
git add .
git commit -m "CalorieApp production-ready release"
git push origin main
```

### Regular Updates
```bash
git add .
git commit -m "Your update message"
git push
```

## 📂 Key Files

- **`run.py`** - Enhanced launcher with dependency checks
- **`main.py`** - Original launcher (compatibility)
- **`requirements.txt`** - Python dependencies
- **`buildozer.spec`** - Android build configuration
- **`README.md`** - Complete project documentation

## 🛠️ Troubleshooting

### App Won't Start
1. Check dependencies: `pip install -r requirements.txt`
2. Try original launcher: `python main.py`
3. Check Python version: `python --version` (requires 3.8+)

### APK Build Issues
1. Install buildozer: `pip install buildozer`
2. Clean build: `buildozer android clean`
3. Check buildozer.spec configuration

### Missing Images
- All images should be in `assets/images/` directory
- Check KV file paths point to correct location

## ✅ Features

- 🔐 **Multi-Wallet Support** - Create and manage multiple XRPL wallets
- 🔑 **Mnemonic Recovery** - 12-word BIP39 recovery phrases for backup
- 💸 **XRP Transactions** - Send and receive XRP with robust connectivity
- 🪙 **Custom Tokens** - Generic token system for XRPL tokens
- 📊 **Transaction History** - Visual indicators (↑ sent, ↓ received)
- 🎨 **NFT Minting** - Create NFTs on the XRPL
- 📈 **DEX Trading** - Trade tokens on decentralized exchange
- 🍽️ **Food Tracking** - Monitor calories and nutrition
- 🧭 **Smart Navigation** - Conditional navigation system with bottom-left menu
- 🎨 **Modern UI** - Unified layout with visible CalorieApp logo
- 🔒 **Enhanced Security** - Encrypted storage with password protection

## 🎯 Ready For

- ✅ Development and testing
- ✅ APK building and distribution
- ✅ GitHub repository upload
- ✅ Production deployment