# CalorieApp Project

Welcome to the organized CalorieApp project! 🚀

## Quick Start

### Windows
```cmd
scripts\run.bat
```

### Linux/Mac
```bash
./scripts/run.sh
```

### Python
```bash
python main.py
```

## Project Structure

```
CalorieAppTestnet/
├── main.py                 # Main entry point
├── setup.py                # Python package setup
├── src/                    # Source code
│   ├── core/               # Core application logic
│   │   ├── app.py         # Main application class
│   │   └── calorieapptestnetv11.kv  # UI layout
│   ├── screens/            # All screen classes
│   │   ├── WalletScreen.py
│   │   ├── CreateWalletScreen.py
│   │   └── ...
│   └── utils/              # Utility functions
│       ├── faucet_manager.py
│       └── ...
├── config/                 # Configuration files
│   ├── requirements.txt
│   └── buildozer.spec
├── docs/                   # Documentation
│   ├── README.md
│   └── *.md files
├── tests/                  # Test files
├── data/                   # Application data
├── assets/                 # Images and resources
├── scripts/                # Launch scripts
└── archive/                # Backup files
```

## Development

### Install Dependencies
```bash
pip install -r config/requirements.txt
```

### Development Mode
```bash
pip install -e .
```

## Features

✅ **Organized Structure**: Clean separation of concerns  
✅ **Navigation Control**: Smart navigation drawer management  
✅ **Wallet Management**: Multi-wallet XRPL support  
✅ **Transaction History**: Complete transaction tracking  
✅ **Modern UI**: KivyMD Material Design 3  
✅ **Cross-platform**: Windows, Linux, Mac support  

## Recent Improvements

- ✅ Complete project reorganization
- ✅ Fixed navigation drawer control
- ✅ Enhanced import structure
- ✅ Added proper Python packaging
- ✅ Created launch scripts for all platforms
- ✅ Organized documentation