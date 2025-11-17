# Project TODO / Roadmap

Priority order: P0 (now), P1 (soon), P2 (later)

## ✅ Recently Completed
- [x] Unified screen names to consistent snake_case convention
- [x] Added comprehensive UX Tour automated testing (97 tests, 100% pass rate)
- [x] Added CI integration for UX Tour with artifact uploads
- [x] Expanded offline mode testing across all network-dependent screens
- [x] Created comprehensive UX Tour documentation and guides
- [x] Updated .gitignore for better artifact management
- [x] Cleaned up backup files and cache directories

## P0 — Stability & Consistency
- [x] Verify all screens use `AppHeader` with `id: app_header` where dynamic titles are needed. ✅ Completed via UX Tour
- [x] Ensure all transaction lists use consistent patterns ✅ Wallet, Send XRP, Send Token validated
- [x] Verify offline mode flows on all transaction/balance paths ✅ UX Tour includes offline tests
- [ ] Run `scripts/kv_sanity_check.py` in CI on every PR affecting `src/core/kv/**`
- [ ] Add quick smoke tests for `_get_tx_label` behavior across screens

## P1 — Developer Experience
- [x] CONTRIBUTING.md present with dev setup and guidelines ✅
- [ ] Pre-commit: enable by running `pre-commit install` and commit a formatting/lint pass
- [ ] Consolidate lint config: keep `.flake8` OR `[tool.flake8]` (pyproject); remove duplication
- [ ] Add `isort` config in `pyproject.toml` with Black profile
- [ ] Add `scripts/dev/` helpers: `lint`, `format`, `test`, `run` for Windows (BAT) and POSIX (sh)

## P1 — Documentation Polish
- [x] Update badges to include UX Tour workflow ✅
- [x] Add comprehensive UX Tour Guide with examples ✅
- [ ] Add Architecture diagram for navigation and XRPL client manager
- [ ] Add Troubleshooting doc: common Builder/indentation issues, GPU/driver notes

## P1 — CI Enhancements
- [x] Add UX Tour workflow for automated UI testing ✅
- [ ] Expand CI matrix to Windows for Kivy/SDL2 platform testing
- [ ] Cache pip better with `pip cache dir` and constraints
- [ ] Add lint-only workflow for faster PR feedback

## P2 — Performance & Resilience
- [x] Add in-memory cache for XRPL requests with TTL ✅ Implemented in xrpl_client_manager
- [ ] Rate-limit balance/tx polling with exponential backoff across all screens
- [ ] Lazy-load heavy modules (XRPL) in screens only when needed
- [ ] Defer layout work: show placeholders then fill to reduce cold-start lag

## P2 — Testing
- [x] Comprehensive UI/UX testing via automated tour ✅ 97 tests
- [ ] Add deterministic unit tests for `xrpl_client_manager` failover with mocked responses
- [ ] Add basic UI smoke test for KV load using Builder in headless mode
- [ ] Add tests for `currency_utils.decode_currency_code` edge-cases

## P2 — Packaging / Release
- [ ] Add release workflow to tag, generate changelog, and attach APK artifacts
- [ ] Add version gating: ensure `VERSION.py` and README badge stay in sync in CI
- [ ] Review `requirements.txt` for exact pins and add `constraints.txt` if needed

## Inbox / Investigate
- [ ] Consider moving dialogs to centralized factory for consistent styling
- [ ] Explore using `dotenv` for toggles (e.g., OFFLINE_MODE) in dev builds
- [ ] Profile cold-start time and identify lazy-load opportunities
