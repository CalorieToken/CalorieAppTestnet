# CalorieApp Version Information

__version__ = "0.1.0-testnet"
__build__ = "hardening-milestone"
__date__ = "2025-11-19"
__status__ = "beta"

# Release Notes
"""
Release 0.1.0-testnet - Hardening & Compliance Milestone
=======================================================

Scope:
 - Repository privacy hardening (removal of build/run instructions; deferred experimental modules)
 - Comprehensive legal disclaimer infrastructure (multi-tier + canonical file)
 - Feature flag system isolating Web3 browser & CalorieDB prototypes
 - Security audit (no secrets; wallet backups purged; narrowed .gitignore patterns)
 - Deferred XRPL ↔ CalorieDB sync service clarification
 - Branch cleanup (legacy V11 branches retired)

Highlights:
 - ✅ Multi-server XRPL failover layer retained
 - ✅ BIP39 mnemonic flow intact & gated
 - ✅ Screens modularized; KV loading improved
 - ✅ Accessibility & responsive scaffolds preserved
 - ✅ CalorieDB + Web3 features explicitly deferred & non-importing

Risk & Status:
 - Testnet-only beta; not production hardened for value transfer
 - Experimental components behind False flags to prevent accidental exposure

Next Targets:
 - Tag follow-up release for visual polish
 - Optional activation path for CalorieDB after security model revision
 - Add CI enforcement for PR-based changes
"""