# Roadmap: Next Milestone (Target: v0.1.1-testnet)

## Objective
Incremental quality improvements: visual polish, accessibility, performance profiling, preparatory groundwork for optional CalorieDB activation.

## Pillars
1. Visual Consistency & Spacing
2. Accessibility & Contrast
3. XRPL Performance Profiling
4. Deferred Feature Security Modeling
5. Release Automation Maturity

## Detailed Items
| Category | Task | Notes |
|----------|------|-------|
| Visual | Normalize padding across form screens | Use consistent dp scale helpers |
| Visual | Introduce design tokens (colors, spacing) | Centralize in `src/core/design_tokens.py` |
| Accessibility | Contrast audit (AA baseline) | Add script to scan KV color usage |
| Accessibility | Keyboard focus ring improvements | Extend `AccessibleButton` styling |
| Performance | Profile XRPL failover latency | Add timed metrics & histogram logging |
| Performance | Cache trustline queries | Reduce repeated `AccountLines` calls |
| CalorieDB | Threat model draft | Document data surfaces & encryption boundaries |
| CalorieDB | Anonymization verification tests | Ensure removal of PII before public sync |
| Release Automation | Enforce PR-only tag creation | Guard via branch protection + workflow checks |
| Tooling | Add secret scanning workflow | GitHub action or trufflehog integration |
| Testing | Expand unit tests for feature flags | Ensure disabled state blocks imports |

## Stretch Goals
- WalletConnect Phase 1 session handshake sandbox.
- Dynamic theme accessibility auto-adjust (contrast-aware palette fallback).
- Basic metric export endpoint (local debug only).

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Premature CalorieDB exposure | Keep flags false; add activation checklist |
| UI regression from spacing refactor | Snapshot KV layout diff; gradual module approach |
| Performance tuning introduces race conditions | Add deterministic test harness wrappers |

## Exit Criteria (v0.1.1-testnet)
- All visual spacing tasks merged.
- Contrast audit summary committed.
- XRPL latency metrics recorded & baseline documented.
- CalorieDB threat model doc approved.
- Release automation workflow validated via dry-run.

## Audit Reminder
No production token/value features until post-threat model & second security audit.
