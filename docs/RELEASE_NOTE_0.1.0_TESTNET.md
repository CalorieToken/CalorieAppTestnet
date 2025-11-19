# Release 0.1.0-testnet

Hardening & Compliance Milestone (2025-11-19)

## Summary
Initial testnet stabilization establishing privacy boundaries, legal clarity, and deferred experimental feature isolation.

## Key Changes
- Canonical extended legal disclaimer (`docs/LEGAL_DISCLAIMER.md`) + cross-links (LICENSE, CONTRIBUTING, TRADEMARK)
- Security audit: no secrets/mnemonics; wallet backup artifacts removed
- Feature flags: `ENABLE_WEB3_BROWSER`, `ENABLE_CALORIE_DB` default False
- Deferred components relocated under `src/_deferred/`
- .gitignore narrowed (added CalorieDB data dirs; removed overbroad binary patterns)
- XRPL ↔ CalorieDB sync service explicitly deferred
- Legacy branches `CalorieAppV11-2` / `CalorieAppV11-3` deleted (fully merged)

## Active Core
- Mnemonic (BIP39) wallet flows
- Multi-server XRPL failover connectivity
- Modular KV loading & responsive scaffolding
- Accessibility shortcuts framework (conditional)

## Deferred / Flagged
- Web3 Browser (Android WebView integration pending)
- CalorieDB prototype (public/private/IPFS sync pipeline)
- XRPL ↔ CalorieDB linking service

## Security & Privacy
- No hardcoded API keys, seeds, mnemonics, or passwords detected
- Wallet data persistence restricted to explicit filenames
- Experimental modules non-importing when flags disabled

## Upgrade Path
1. Visual polish & spacing normalization
2. Optional activation workflow for CalorieDB (post model review)
3. CI enforcement of PR-only modifications
4. Accessibility contrast audit & token metadata enhancements

## Usage Notice
This is a **beta testnet** release. Not suitable for production value transfer. Verify issuer addresses before interacting with tokens.

## Contact
info@calorietoken.net

---
Refer to `CHANGELOG.md` for historical context.
