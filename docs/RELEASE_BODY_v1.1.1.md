# v1.1.1 – Repository Hardening & UX / Docs Upgrade (2025-11-18)

## TL;DR
Hardening release: modular KV layouts (24+ screens), security & mnemonic UX improvements, public-safe documentation index, social media automation, groundwork for CalorieDB & WalletConnect.

## Highlights
**Structure & CI**: Added lint, UX tour, CodeQL, KV sanity workflows; introduced `.editorconfig`, pre-commit config; replaced monolithic KV with `src/core/kv/*` modular set.

**UX Consistency**: Unified label wrapping (`text_size`), reorganized Wallet, Send, Mnemonic, DEX, NFT screens, selective navigation drawers, improved dialog clarity.

**Security & Reliability**: Clipboard auto-clear, enhanced mnemonic manager, encryption scaffolding, XRPL client manager with failover & performance hooks.

**Documentation**: `OFFICIAL_PROJECT_DOCS.md` public-safe index; added trademark & license clarifications; archived internal milestone and improvement summaries.

**Automation & Social**: Post generation scripts, image generator, asset verification, multi-platform copy packs, visual concept specifications.

**Foundations**: CalorieDB (sync, linking, encryption modules – inactive by default), WalletConnect connector placeholders, performance layer (cache, debouncer, resource guard).

## Breaking Changes
None expected for external consumers. Update internal references from legacy `Screens/*.py` to new `src/screens/*` paths.

## Upgrade Guide
1. Pull latest `main`.
2. Adjust any tooling expecting single KV file to load modular KV directory.
3. (Optional) Use social scripts for announcement.

## Social (Short)
CalorieApp UX & Docs upgrade LIVE → faster flows, stronger security, improved mnemonic UX. Focus: Security • Speed • UX. #CalorieApp #XRPL

## Next (v1.1.2 Targets)
Visual refinement pass, performance profiling, story/reel asset automation, potential WalletConnect Phase 1 activation, accessibility contrast audit, CalorieDB selective activation.

## Checks
✔ Tag `v1.1.1` points to merged commit
✔ CHANGELOG next section `[1.1.2] - Unreleased` added
✔ Release notes & body prepared
✔ Social scripts functional on Windows PowerShell
✔ Core tests pass

## Acknowledgements
Built with KivyMD 2.0.dev & XRPL community support.
