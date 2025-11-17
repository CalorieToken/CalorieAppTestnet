# Generic Test Token System

## Overview

The CalorieApp now uses a flexible, generic token system that makes it easy to add new test tokens without hardcoding specific token details throughout the codebase.

## What Changed

### Removed (Deprecated)
- **SendLipisaScreen.py** - Hardcoded Lipisa token send screen
- **SendCalorieTestScreen.py** - Hardcoded CalorieTest token send screen  
- Lipisa and CalorieTest-specific methods in WalletScreen.py
- LIPISA_OFFLINE and CALORIETEST_OFFLINE global flags

### Added (New Generic System)
- **src/utils/token_config.py** - Centralized token configuration
- **src/screens/SendTestTokenScreen.py** - Generic token send screen
- Flexible architecture for adding new tokens

## How to Add a New Test Token

### Step 1: Configure the Token

Edit `src/utils/token_config.py` and add your token to the `TOKENS` dictionary:

```python
TOKENS = {
    "my_custom_token": {
        "name": "MyCustomToken",
        "currency_code": "4D79437573746F6D546F6B656E00000000000000",  # Hex-encoded
        "issuer": "rYourIssuerAddress...",
        "default_limit": "100000000000",
        "active": True
    }
}
```

#### Token Configuration Fields:
- **name**: Display name for the token (e.g., "MyToken")
- **currency_code**: XRPL currency code in hexadecimal format
- **issuer**: XRPL address of the token issuer
- **default_limit**: Default trustline limit
- **active**: Set to `True` to enable, `False` to disable

### Step 2: Create a Screen Instance

In `src/core/app.py`, add a new screen instance in the `build()` method:

```python
# Add after other screen initialization
self.send_mytoken_screen = SendTestTokenScreen(
    client=client, 
    token_id="my_custom_token",  # Must match key in token_config.py
    name="send_mytoken_screen"
)

# Add to screen manager
self.manager.add_widget(self.send_mytoken_screen)
```

### Step 3: Add UI Elements (Optional)

If you want to display the token balance in the WalletScreen or add navigation buttons:

1. **Edit the KV file** (`src/core/calorieapptestnet.kv`) to add:
   - Balance display labels
   - Navigation buttons
   - Trustline buttons

2. **Add navigation methods** to WalletScreen.py if needed:
```python
def send_mytoken_screen(self):
    self.manager.current = "send_mytoken_screen"
```

### Step 4: Update Navigation (Optional)

If the new token screen should not have a navigation drawer, add it to `src/utils/conditional_navigation.py`:

```python
DRAWER_DISABLED_SCREENS = {
    # ... existing screens ...
    "send_mytoken_screen",
}
```

## Benefits of the Generic System

1. **Centralized Configuration**: All token details in one place
2. **Reusable Code**: One screen class handles all tokens
3. **Easy Maintenance**: Add/remove tokens by editing config only
4. **Scalable**: Support unlimited tokens without code duplication
5. **Clean Architecture**: Separation of concerns between UI and data

## Converting Currency Codes

XRPL requires currency codes in hexadecimal format. To convert:

```python
# Example: Convert "MyToken" to hex
token_name = "MyToken"
hex_code = token_name.encode('utf-8').hex().upper()
# Pad to 40 characters
hex_code = hex_code + "0" * (40 - len(hex_code))
print(hex_code)  # 4D79546F6B656E0000000000000000000000000000
```

Or use an online converter: [String to Hex Converter](https://www.convertstring.com/EncodeDecode/HexEncode)

## Example: Full Token Addition

Here's a complete example adding a "TestCoin" token:

**1. src/utils/token_config.py:**
```python
TOKENS = {
    "testcoin": {
        "name": "TestCoin",
        "currency_code": "54657374436F696E00000000000000000000000000",
        "issuer": "rN7n7otQDd6FczFgLdlqtyMVrn3HMgkDy5",
        "default_limit": "100000000000",
        "active": True
    }
}
```

**2. src/core/app.py (in build method):**
```python
self.send_testcoin_screen = SendTestTokenScreen(
    client=client, 
    token_id="testcoin",
    name="send_testcoin_screen"
)
self.manager.add_widget(self.send_testcoin_screen)
```

**3. src/screens/WalletScreen.py:**
```python
def send_testcoin_screen(self):
    self.manager.current = "send_testcoin_screen"
```

**4. src/utils/conditional_navigation.py:**
```python
DRAWER_DISABLED_SCREENS = {
    # ... existing ...
    "send_testcoin_screen",
}
```

That's it! Your new token is ready to use.

## Migration Notes

If you were using Lipisa or CalorieTest before:
- Old screen files have been removed
- Update any bookmarks/saved references
- Use the new generic system for future tokens
- The wallet will still work with existing XRPL trustlines

## Support

For questions or issues with the token system, check:
- `src/utils/token_config.py` - Token configuration
- `src/screens/SendTestTokenScreen.py` - Generic send screen implementation
- XRPL Documentation: https://xrpl.org/

## Future Enhancements

Potential improvements to the system:
- Dynamic UI generation from token config
- Token registry/discovery service
- Multi-token trustline management screen
- Token swap/exchange features
- Historical price data integration
