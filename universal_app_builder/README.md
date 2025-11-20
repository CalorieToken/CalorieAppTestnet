# Universal App Builder (Reconstructed)

This directory is a **reconstruction scaffold** for the former Universal App Builder (UAB) specifications. All original implementation source files were removed earlier and were never committed to version control, so they cannot be restored via git.

## Current Status
- Implementation: **Missing** (no builder/ modules, no code generation)
- Test suite: Placeholder only (adjusted to report missing implementation)
- Documentation: Being rebuilt from memory/spec outlines
- Purpose: Preserve intent; enable phased future rebuild if desired

## What Was Lost (High-Level Intent)
- Feature DSL parser & generators
- Multi-platform profile-driven project scaffolder
- Self-modification safety utilities (syntax, security, sandbox, rollback)
- Decentralized integration stubs (IPFS, BigchainDB, DID)
- Hosting/provider plugin interfaces

## What Exists Now
- `__init__.py` (stub)
- `test_self_modification.py` (relocated; emits missing implementation notice)
- `docs/` placeholders:
  - `INDEX.md`
  - `ARCHITECTURE.md`
  - `FEATURE_DSL_SPEC.md`
  - `ETHICAL_USAGE.md`
  - `TESTING_SELF_MODIFICATION.md`
  - `RECOVERY_PLAN.md`

## Recovery Principles
1. **Truthful State** – We start from zero implementation.
2. **Phased Rebuild** – Define minimal viable core before advanced features.
3. **Isolation** – Keep UAB separate from CalorieApp to avoid coupling.
4. **Safety First** – Re‑implement test harness before allowing code mutation.
5. **Auditability** – Every recovered module must include rationale & provenance notes.

## Suggested Rebuild Phases (See `RECOVERY_PLAN.md` for detail)
1. Core package skeleton & config loader
2. Profile schema & validation
3. Feature DSL minimal grammar (components + layout)
4. Single-platform generator (Kivy) MVP
5. Safety harness (syntax + rollback)
6. DSL expansion (styling, navigation, data bindings)
7. Multi-platform adapters (CLI placeholder)
8. Optional decentralized integrations (deferred)

## Important Disclaimer
This reconstructed directory does **not** represent working software. It is an organized placeholder to prevent further confusion, document intended architecture, and enable an intentional rebuild if prioritized.

## Next Decisions
Please indicate:
- Proceed with Phase 1 rebuild? (Yes/No)
- Link this directory from root `README.md`? (Default: No until implementation begins)
- Prioritize which advanced areas (DSL vs Safety vs Hosting) after MVP?

---
*Reconstruction version:* `0.0.0-recovery`
