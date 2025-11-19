# Roadmap v1.1.2 (Unreleased)

## Theme
Refinement & activation: polish visuals, performance tuning, optional feature enablement.

## Objectives
1. Visual Refinement & Consistency
2. Performance Profiling & Optimization
3. Accessibility / Contrast Enhancements
4. CalorieDB Selective Activation (Phase 1)
5. WalletConnect Phase 1 (Read-only / basic session)
6. Social Asset Automation (Story/Reel)

## Task Breakdown
### 1. Visual Refinement
- Normalize spacing scale (8 / 12 / 16 pattern)
- Audit font sizes vs size classes (xs-sm-md)
- Align button heights across wallet & transaction screens
- Introduce subtle elevation tokens (1,2,4)

### 2. Performance
- Profile XRPL network calls (cache hit ratio, latency)
- Introduce adaptive polling backoff
- Add lightweight metrics logger (opt-in)
- Memory footprint check for KV screen load

### 3. Accessibility
- Contrast scan on primary color combos (#1E3A8A / #00A651 / #FCD34D)
- Larger tap target verification (>=44dp)
- Dynamic font scale option toggle
- Screen reader label audit

### 4. CalorieDB Phase 1
- Enable encrypted local index only
- Add sync toggle (default OFF)
- Basic integrity check command
- Write minimal public-safe activation guide

### 5. WalletConnect Phase 1
- Implement connector state machine (INIT → CONNECTED → CLOSED)
- Add session request UI
- Log handshake events (debug only)
- Defer signing flows (Phase 2)

### 6. Social Asset Automation
- Add `generate_story_image.py` vertical variant
- Batch generation script for square + story
- Optional compression pass (pngquant or Pillow optimize)

## Risks & Mitigations
| Area | Risk | Mitigation |
|------|------|-----------|
| Performance changes | Over-optimization early | Profile first, code second |
| CalorieDB activation | Data integrity issues | Phase toggle & integrity checks |
| WalletConnect | Session security | Read-only initial scope |
| Accessibility | Scope creep | Limit to contrast & sizing baseline |

## Success Metrics
- <= 10% redundant XRPL calls after caching adjustments
- All critical screens pass contrast AA (or documented exceptions)
- CalorieDB toggle stable with no data corruption in local tests
- WalletConnect session establishes & terminates cleanly
- Story asset generation under 1 min per variant

## Timeline (Indicative)
Week 1: Profiling + visual audit
Week 2: Performance fixes + accessibility adjustments
Week 3: CalorieDB & WalletConnect scaffolding activation
Week 4: Asset automation + stabilization, pre-release testing

## Release Tag Target
`v1.1.2-rc1` then `v1.1.2` after validation.
