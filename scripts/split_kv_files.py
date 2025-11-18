#!/usr/bin/env python3
"""
KV File Splitter
Automates extraction of screen definitions from monolithic calorieapptestnet.kv
into individual files in src/core/kv/ directory.
"""
import os
import re

# Path configuration
MONOLITHIC_KV = r"c:\Users\P\MyProjects\CalorieAppTestnet\src\core\calorieapptestnet.kv"
KV_OUTPUT_DIR = r"c:\Users\P\MyProjects\CalorieAppTestnet\src\core\kv"

# Screen name to file name mapping (snake_case convention)
SCREEN_MAPPING = {
    "WalletScreen": "wallet_screen.kv",
    "SendXRPScreen": "send_xrp_screen.kv",
    "NFTMintScreen": "nft_mint_screen.kv",
    "CreateImportWalletScreen": "create_import_wallet_screen.kv",
    "DEXTradeScreen": "dex_trade_screen.kv",
    "FoodTrackScreen": "food_track_screen.kv",
    "SettingsScreen": "settings_screen.kv",
    "IntroScreen": "intro_screen.kv",
    "FirstUseScreen": "first_use_screen.kv",
    "ImportKeysScreen": "import_keys_screen.kv",
    "ImportExtraKeysScreen": "import_extra_keys_screen.kv",
    "CreateWalletScreen": "create_wallet_screen.kv",
    "CreateExtraWalletScreen": "create_extra_wallet_screen.kv",
    "WalletSetupScreen": "wallet_setup_screen.kv",
    "LoginScreen": "login_screen.kv",
    "MnemonicDisplayScreen": "mnemonic_display_screen.kv",
    "MnemonicImportScreen": "mnemonic_import_screen.kv",
    "AccountChoiceScreen": "account_choice_screen.kv",
    "ImportChoiceScreen": "import_choice_screen.kv",
    "KeypairImportScreen": "keypair_import_screen.kv",
    "MnemonicVerifyScreen": "mnemonic_verify_screen.kv",
    "AccountNamingScreen": "account_naming_screen.kv",
    "AddTrustlineScreen": "add_trustline_screen.kv",
}

def read_monolithic_kv():
    """Read the monolithic KV file."""
    with open(MONOLITHIC_KV, 'r', encoding='utf-8') as f:
        return f.readlines()

def find_screen_boundaries(lines):
    """
    Find start/end line numbers for each screen definition.
    Returns dict: {screen_name: (start_line, end_line)}
    """
    boundaries = {}
    current_screen = None
    start_line = 0
    indent_stack = []
    
    for i, line in enumerate(lines):
        # Check for screen definition start
        match = re.match(r'^<(\w+)>:', line)
        if match:
            # Save previous screen if exists
            if current_screen:
                boundaries[current_screen] = (start_line, i - 1)
            
            current_screen = match.group(1)
            start_line = i
            indent_stack = [0]  # Reset indent tracking
            continue
        
        # Track indentation to detect screen end
        if current_screen and line.strip():
            indent = len(line) - len(line.lstrip())
            if indent == 0 and line.startswith('<'):
                # New top-level definition, previous screen ended
                boundaries[current_screen] = (start_line, i - 1)
                current_screen = None
    
    # Handle last screen
    if current_screen:
        boundaries[current_screen] = (start_line, len(lines) - 1)
    
    return boundaries

def extract_screen_content(lines, start, end):
    """Extract lines for a specific screen."""
    return ''.join(lines[start:end + 1])

def split_kv_files():
    """Main function to split KV file."""
    print("Reading monolithic KV file...")
    lines = read_monolithic_kv()
    
    print("Finding screen boundaries...")
    boundaries = find_screen_boundaries(lines)
    
    print(f"Found {len(boundaries)} screen definitions")
    
    # Ensure output directory exists
    os.makedirs(KV_OUTPUT_DIR, exist_ok=True)
    
    # Extract each screen
    extracted_count = 0
    for screen_name, output_file in SCREEN_MAPPING.items():
        if screen_name in boundaries:
            start, end = boundaries[screen_name]
            content = extract_screen_content(lines, start, end)
            
            output_path = os.path.join(KV_OUTPUT_DIR, output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Extracted {screen_name} → {output_file} ({end - start + 1} lines)")
            extracted_count += 1
        else:
            print(f"✗ Warning: {screen_name} not found in monolithic file")
    
    print(f"\n✓ Extraction complete: {extracted_count}/{len(SCREEN_MAPPING)} screens")
    print(f"Output directory: {KV_OUTPUT_DIR}")

if __name__ == "__main__":
    split_kv_files()
