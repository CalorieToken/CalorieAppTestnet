# XRPL Improvement Automation - Manual Patch Checklist

Remaining manual steps (see CALORIEAPP_AUTOMATION_GUIDE.md for details):
1. Address derivation: Replace direct stored address usage with derive_classic_address(public_key) where applicable.
2. Integrate AddTrustlineScreen: Register in ScreenManager and add navigation entry.
3. WalletScreen trustline display: Add method to fetch and render trustlines (see AddTrustlineScreen for patterns).
4. Multi-account support (optional): Introduce accounts list structure and selection logic.
5. Test sequence: Launch app -> create account -> connect XRPL -> add trustline -> send issued token.

Created by apply_to_calorieapp.ps1 on $timestamp
