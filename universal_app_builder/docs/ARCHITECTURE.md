# Architecture (Spec Stub)

**Status:** SPEC-STUB | **Implements:** Nothing yet

## Purpose
Define intended high-level structure of Universal App Builder (UAB) to guide phased reconstruction.

## Intended Major Components
- Core package loader & configuration
- Profile schema (JSON/YAML) validator
- Feature DSL parser (tokenize → AST → semantic validation)
- Generators (initially: Kivy project skeleton)
- Safety layer (syntax / static security / rollback)
- Optional integrations (decentralized storage, hosting plugins) – DEFERRED

## Data Flow (Planned)
Profile → Validation → DSL Expansion → Generation Plan → File Emit → Post-Checks

## Out of Scope (Phase 1)
- Multi-platform abstraction
- Full hosting automation
- Decentralized persistence

## Risks
- Rebuilding DSL without original examples may drift from prior intent.
- Over-engineering early phases slows delivery.

## Reconstruction Notes
Original code absent; rebuild should prioritize *minimal viable generator* first.
