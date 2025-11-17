"""Storage path management for wallet data.

Provides separate storage locations for:
- Development (project folder)
- Frozen exe (user's AppData folder)

Usage:
    from src.utils.storage_paths import WALLET_DATA_PATH
    with shelve.open(WALLET_DATA_PATH) as db:
        ...
"""

import os
import sys
from pathlib import Path


def get_wallet_data_path() -> str:
    """Get the appropriate wallet_data path based on runtime environment.

    Returns:
        Path string for shelve database (without extension)
    """
    if getattr(sys, "frozen", False):
        # Running as frozen exe - use AppData
        appdata = os.getenv("APPDATA") or os.path.expanduser("~")
        app_dir = os.path.join(appdata, "CalorieAppTestnet")
        os.makedirs(app_dir, exist_ok=True)
        return os.path.join(app_dir, "wallet_data")
    else:
        # Development mode - use project folder
        return "wallet_data"


def get_app_data_dir() -> Path:
    """Get the application data directory.

    Returns:
        Path object to the app data directory
    """
    if getattr(sys, "frozen", False):
        appdata = os.getenv("APPDATA") or os.path.expanduser("~")
        app_dir = Path(appdata) / "CalorieAppTestnet"
        app_dir.mkdir(exist_ok=True)
        return app_dir
    else:
        return Path.cwd()


# Global constant for easy import
WALLET_DATA_PATH = get_wallet_data_path()
