"""Centralized feature flags for deferred/experimental components.

Flags gate visibility and import of modules that are not part of the
current beta production surface. Each flag MUST default to False.

Contributing:
 - Add new flags here for any feature not ready for release.
 - Guard screen registration, menu items, and actions using these flags.
 - Do not perform side effects at import time.
"""

# Deferred screens / modules
ENABLE_WEB3_BROWSER = False  # Web3BrowserScreen (Android WebView pending)
ENABLE_CALORIE_DB = False    # CalorieDB decentralized scan recording pipeline

def is_enabled(name: str) -> bool:
    return {
        "web3_browser": ENABLE_WEB3_BROWSER,
        "calorie_db": ENABLE_CALORIE_DB,
    }.get(name, False)
