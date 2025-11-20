# Recovery Plan

**Version:** 0.0.0-recovery

## Phase Overview
| Phase | Goal | Deliverable | Exit Criteria |
|-------|------|-------------|---------------|
| 0 | Scaffold | Directory + spec stubs | Docs present, no code |
| 1 | Core Skeleton | Config + profile schema stub | Can load empty profile |
| 2 | DSL MVP | Parse minimal YAML screens | Generates single Kivy screen |
| 3 | Generator MVP | Emit Kivy project skeleton | App runs placeholder screens |
| 4 | Safety Layer | Syntax + rollback harness | Safe modify test passes |
| 5 | DSL Expansion | Add basic styling/nav depth | Complex example validates |
| 6 | Multi-Platform Abstraction | Add web CLI placeholder | Dual target builds |
| 7 | Optional Integrations | Decentralized stubs | Feature flags, isolated |

## Immediate Next Steps
1. Decide if rebuild is a priority now.
2. If yes: implement profile schema + loader (Phase 1).
3. Create minimal example `example_profile.yaml`.
4. Add parser for `screens` → internal list.
5. Emit a Kivy `main.py` with navigation for 2 screens.

## Non-Goals (Early)
- Full hosting automation
- Advanced security analysis
- Rich dynamic bindings

## Risks
- Rebuild time cost vs value for current objectives.
- Drift from prior undocumented decisions.

## Recommendation
Pause after Phase 3 to validate usefulness before deeper investment.
