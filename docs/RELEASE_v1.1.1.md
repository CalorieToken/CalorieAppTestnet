# Release v1.1.1 – Repository Hardening & UX / Docs Upgrade (2025-11-18)

## Summary (Copy/Paste Friendly)
Repository hardening, modular KV layouts (24+ screens), public-safe documentation index, enhanced security & mnemonic UX, social automation tooling. Tag: `v1.1.1`.

## Highlights
### 1. Structure & Hardening
- Introduced modular `src/core/kv/` layout replacing single monolithic KV file.
- Added CI workflows: lint, CodeQL, KV sanity, UX tour.
- Added `.editorconfig`, `.pre-commit-config.yaml` for consistent formatting.

### 2. UX Consistency
- Text wrapping normalized with `text_size` across all major screens.
- Wallet, mnemonic verify, send, DEX & NFT screens reorganized for clarity.
- Navigation logic consolidated (conditional drawers only where needed).

### 3. Security & Reliability
- Clipboard auto-clear utility.
- Enhanced mnemonic management and dialog UX flows.
- Encryption scaffolding for CalorieDB components.
- XRPL client manager with failover and performance groundwork.

### 4. Documentation & Public-Safe Index
- `OFFICIAL_PROJECT_DOCS.md` central entry point.
- Privacy filtering (internal architecture withheld; public guides exposed).
- Added trademark file and clarified dual licensing usage boundaries.

### 5. Automation / Social Media
- PowerShell scripts: generate posts, copy to clipboard, asset verification.
- Image generator for branded square social image.
- Visual concepts & posting guide for multi-platform rollout.

### 6. Future Foundations
- CalorieDB scaffolding: encryption, linking, sync modules (inactive by default).
- WalletConnect preliminary connector setup.
- Performance layer (cache, debouncer, resource guard) prepared.

## File Impact Overview
- 33K insertions, 5.7K deletions.
- Added extensive KV screen library + utility modules.
- Replaced deleted legacy screen files with expanded screen set under `src/screens/`.

## Upgrade Notes
No breaking API changes expected for external integrators. Downstream adaptation: update any tooling that referenced legacy `Screens/*.py` paths to new `src/screens/` hierarchy.

## Social Post (Short)
CalorieApp UX & Docs upgrade LIVE → faster flows, stronger security, improved mnemonic UX. Focus: Security • Speed • UX. #CalorieApp #XRPL

## Next (v1.1.2 Targets)
See top-of-file CHANGELOG section `[1.1.2] - Unreleased` for roadmap.

## Tag
`git checkout main && git pull && git show v1.1.1 --oneline`

## Verification Checklist
- [x] Tag points to merged commit including KV layouts
- [x] LICENSE reflects trademark & dual license
- [x] CHANGELOG updated with next version placeholder
- [x] Social automation scripts functional on Windows
- [x] Tests pass (mnemonic, version, XRPL manager)

## Acknowledgements
Built with KivyMD 2.0.dev and XRPL community support.
