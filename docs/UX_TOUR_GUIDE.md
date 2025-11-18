# Complete UX Tour System - User Guide

**Updated:** 2025-11-18  
**System Version:** 2.0 (Multi-phase with Best Practice Validation)

## 🎯 Overview

The Complete UX Tour (`complete_ux_tour.py`) is an automated end-to-end testing system that validates **every** screen, feature, and interaction in CalorieAppTestnet. It provides comprehensive analysis with best practice validation across 9 reference domains.

**⚠️ Note:** This replaces the older `ux_tour.py` system with enhanced capabilities.

## ✨ Key Features

### Comprehensive Coverage
- **13 Testing Phases** covering all app functionality
- **Branch Testing** for alternative user flows (create vs import, etc.)
- **Triple Validation** per phase: Functionality → Performance → Appearance
- **9 Reference Domains**: Kivy, KivyMD, Material Design 3, UI Guidelines, XRPL, IPFS, BigchainDB, FoodRepo, Bitcoin

### Automated Analysis
- Issue categorization (Functional, Layout, Performance, Errors)
- Best practice validation with reference citations
- Compliance scoring (target >80% per domain)
- Fix recommendations with quick-fix suggestions
- Per-phase analysis reports

### Output Structure
```
docs/ux_tours/{tour_id}/
├── screenshots/     # Before/after for every action
├── logs/           # Detailed execution logs
├── reports/        # Action summaries & metrics
└── analysis/       # Per-phase analysis + recommendations
    ├── phase_1_analysis.json      # Machine-readable
    └── phase_1_SUMMARY.md         # Human-readable
```

## 📋 Complete Phase List

### Phase 1: Onboarding / New User Flow
**Branches:** create_new, import_existing  
**Tests:** IntroScreen → FirstUseScreen → AccountChoiceScreen → MnemonicDisplayScreen → MnemonicVerifyScreen → FirstAccountSetupScreen → WalletScreen

### Phase 2: Account Management & Multi-Account
**Branches:** single_account, multi_account  
**Tests:** Account creation, switching, naming, management

### Phase 3: Wallet Core
**Tests:** Balance display, transaction history, refresh operations

### Phase 4: Transactions
**Branches:** sendxrp, send_test_tokens, trustlines  
**Tests:**
- SendXRPScreen
- SendTestTokenScreen (CAL, Lipisa)
- AddTrustlineScreen

### Phase 5: NFT Mint / Display
**Tests:** NFT minting interface, display gallery, metadata

### Phase 6: DEX / Trading
**Tests:** DEXTradeScreen, token swaps, order book

### Phase 7: Food Tracking UI
**Tests:** FoodTrackScreen, calorie logging, meal tracking

### Phase 7b: QR/Barcode Scanning
**Branches:** qr_scan, barcode_scan  
**Tests:**
- BarcodeScanScreen
- CameraScanScreen

### Phase 8: Settings / Preferences / Theme
**Tests:** SettingsScreen, theme switching, preferences

### Phase 9: Web3 Browser & WebView
**Branches:** web3_browser, webview  
**Tests:**
- Web3BrowserScreen
- WebViewScreen

### Phase 10: Accessibility & Responsive
**Tests:** Touch targets (48dp), contrast, screen readers, responsive layouts

### Phase 11: XRPL Network Resilience
**Tests:** Connection failover, retry logic, offline handling

### Phase 12: Persistence / Data Integrity
**Tests:** App restart, data recovery, wallet database integrity

### Phase 13: Final Analysis & Reporting
**Tests:** Comprehensive compliance report, final recommendations

## 🚀 Usage

### Basic Execution
```powershell
# Run one phase
python -B scripts/complete_ux_tour.py

# Review analysis
cat docs/ux_tours/tour_*/analysis/phase_*_SUMMARY.md

# Fix high-priority issues
# (see recommendations in analysis)

# Run next phase
python -B scripts/complete_ux_tour.py
```

### Environment Variables

#### Visual Mode (Default: ON)
```powershell
# Enable visual window (slower but visible)
$env:TOUR_VISUAL="1"
python -B scripts/complete_ux_tour.py

# Disable for faster headless execution
$env:TOUR_VISUAL="0"
python -B scripts/complete_ux_tour.py
```

#### Slow Motion (Default: OFF)
```powershell
# Add 0.4s delay between actions for manual observation
$env:TOUR_SLOWMO="1"
python -B scripts/complete_ux_tour.py
```

#### Phone Size Enforcement (Default: OFF)
```powershell
# Force phone-sized window (414x896 - iPhone 11 DP)
$env:TOUR_FORCE_PHONE="1"
$env:TOUR_PHONE_WIDTH="414"
$env:TOUR_PHONE_HEIGHT="896"
python -B scripts/complete_ux_tour.py
```

### Capturing Output
```powershell
# Log to file with timestamp
python -B scripts/complete_ux_tour.py 2>&1 | Tee-Object -FilePath "ux_tour_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
```

## 📊 Analysis Reports

### Compliance Scorecard (NEW in v2.0)
Each phase generates compliance scores:
- **Overall Compliance:** >80% target
- **UI/UX:** Material Design 3 adherence
- **XRPL:** Transaction reliability
- **Performance:** Response times <3s
- **Accessibility:** Touch targets, contrast

### Markdown Summary Format
```markdown
# Phase 1 - Analysis Summary

## 📊 Compliance Scorecard
- **Overall Compliance:** 85.2%
- **UI/UX Compliance:** 88.0%
- **XRPL Best Practices:** 90.5%
- **Performance:** 78.3%
- **Accessibility:** 82.1%

## Required Fixes
### 🔴 High Priority
- **Issue description**
  - Recommendation: Specific fix
  - Reference: `docs/reference/file.md#section`
  - Quick Fixes: [actionable steps]
```

## 🔧 Fix Workflow

1. **Review Analysis**: `cat docs/ux_tours/tour_*/analysis/phase_1_SUMMARY.md`
2. **Prioritize**: Focus on 🔴 High Priority issues
3. **Implement**: Use reference citations and quick fixes
4. **Verify**: Re-run phase to confirm fixes
5. **Continue**: Proceed to next phase when compliance >80%

## 🎯 Success Criteria

- ✅ All 13 phases executed
- ✅ Overall compliance >80%
- ✅ No HIGH severity issues
- ✅ All critical screens tested
- ✅ All branches covered

## 📚 Reference Documentation

Validation checks reference:
- `docs/reference/kivy_best_practices.md`
- `docs/reference/kivymd_best_practices.md`
- `docs/reference/material_design3_best_practices.md`
- `docs/reference/ui_guidelines.md`
- `docs/reference/xrpl_best_practices.md`
- `docs/reference/ipfs_best_practices.md`
- `docs/reference/bigchaindb_best_practices.md`
- `docs/reference/foodrepo_api_best_practices.md`
- `docs/reference/bitcoin_dev_resources.md`

---

## 🕰️ Legacy System (ux_tour.py)

The original `ux_tour.py` is still available for quick validation:
- **Add Trustline**: Currency/issuer inputs, limit field
- **NFT Mint**: URI and taxon inputs
- **DEX Trade**: Screen rendering and content
- **Create/Import Wallet**: Navigation and button presence
- **Import Choice**: Mnemonic vs keypair selection
- **Keypair Import**: Public/private key inputs and validation
- **Account Choice**: Create vs import account options
- **Wallet Setup**: Initial setup flow
- **Mnemonic Verify**: 12-word verification fields
- **Import Extra Keys**: Additional keypair import
- **Food Track**: Screen rendering
- **Mnemonic Display**: Recovery phrase and key display
- **Mnemonic Import**: 12-word import fields
- **First Use**: Password creation
- **Login**: Password entry and validation

### Offline Path Tests (10 tests)
- **Wallet Offline**: Balance shows "Offline Mode", trustlines show offline message
- **SendXRP Offline**: Balance and transaction list show offline state
- **Token Send Offline**: Offline state handling
- **Trustline Offline**: Form accessibility in offline mode
- **DEX Offline**: Screen accessibility in offline mode

## CI Integration

### GitHub Actions Workflow

The UX tour runs automatically on:
- Pull requests to `main`
- Pushes to `main`
- Manual workflow dispatch

Configuration: `.github/workflows/ux_tour.yml`

### CI Artifacts

After each run, the following artifacts are uploaded:
- `ux-tour-report` - Test report file
- `ux-tour-screenshots` - All captured screenshots

### Viewing CI Results

1. Go to Actions tab in GitHub
2. Select the workflow run
3. Scroll to Artifacts section
4. Download `ux-tour-report` or `ux-tour-screenshots`

## Extending the Tour

### Adding New Screen Tests

1. **Create navigation method**:
```python
def _to_new_screen(self, dt):
    try:
        self.app.manager.current = "new_screen_name"
        Clock.schedule_once(self._snap_new_screen, 0.5)
    except Exception as e:
        self.log(f"NewScreen nav failed: {e}")
        Clock.schedule_once(self._next_step, 0.2)
```

2. **Add assertion method**:
```python
def _snap_new_screen(self, dt):
    try:
        scr = self.app.manager.get_screen("new_screen_name")
        
        # Test header
        self.test("NewScreen header exists",
                 lambda: scr.ids.get("app_header") is not None)
        
        # Test specific widgets
        self.test("NewScreen input field exists",
                 lambda: scr.ids.get("input_field") is not None)
        
        # Capture screenshot
        self.snap("XX_new_screen")
        
        # Chain to next test
        Clock.schedule_once(self._next_step, 0.4)
    except Exception as e:
        self.log(f"NewScreen snap failed: {e}")
        Clock.schedule_once(self._next_step, 0.2)
```

3. **Update test chain**: Insert your new methods into the tour sequence

### Test Patterns

**Basic existence check**:
```python
self.test("Widget exists", lambda: scr.ids.get("widget_id") is not None)
```

**Text validation**:
```python
self.test("Label has text", lambda: getattr(scr.ids.get("label"), "text", "") != "")
```

**Input field test**:
```python
scr.ids["field"].text = "test_value"
self.test("Field accepts input", lambda: scr.ids["field"].text == "test_value")
```

**Icon button search**:
```python
icons = [w for w in scr.walk() if hasattr(w, 'icon') and w.icon == 'icon-name']
self.test("Icon button exists", lambda: len(icons) > 0)
```

**Dialog validation**:
```python
self.test("Dialog opened", lambda: hasattr(scr, "dialog") and scr.dialog is not None)
```

## Troubleshooting

### Test Failures

1. **Missing ID**: Add `id: widget_name` to the KV file
2. **Wrong screen name**: Check screen registration in `app.py`
3. **Timing issues**: Increase delay in `Clock.schedule_once`
4. **Dynamic content**: Use container checks instead of child counts

### CI Failures

1. Check the uploaded test report artifact
2. Review screenshots to identify visual issues
3. Run locally to reproduce: `python scripts/ux_tour.py`

### Common Issues

**"No Screen with name X"**: Screen not registered in app.py or name mismatch
**Widget not found**: Check KV file for correct ID assignment
**Test timeout**: Network issues or slow rendering; increase delays

## Best Practices

1. **Add IDs**: Every testable widget needs a unique `id` in KV
2. **Standardize names**: Use snake_case for screen names consistently
3. **Chain gracefully**: Always provide fallback in exception handlers
4. **Screenshot strategically**: Capture before and after user actions
5. **Test incrementally**: Add tests one screen at a time and validate

## Performance

- Full tour runs in ~30-45 seconds
- Generates ~100+ screenshots
- Report size: ~5KB
- Screenshot total: ~50-100MB

## Maintenance

### Regular Updates
- Add tests for new screens as they're implemented
- Update assertions when UI changes
- Keep screenshot baselines for visual regression testing

### Version Control
- Commit test reports for baseline comparison
- Use `.gitignore` to exclude screenshots (optional)
- Tag significant test coverage milestones

## Related Documentation

- [Project Organization](PROJECT_ORGANIZATION.md)
- [Development Progress](docs/development-progress/)
- [Quick Start Guide](QUICK_START.md)
