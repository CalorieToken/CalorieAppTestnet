# UX Tour v2.0 - Quick Reference Card

**Date:** 2025-11-18  
**Status:** ✅ READY FOR TESTING

## ✨ What's New

### Fixed
- ❌ `SendCalorieTestScreen` → ✅ `SendTestTokenScreen`
- ❌ `SendLipisaScreen` → ✅ `SendTestTokenScreen`
- ✅ Added `AddTrustlineScreen`
- ✅ Added `BarcodeScanScreen`
- ✅ Added `CameraScanScreen`
- ✅ Added `Web3BrowserScreen`
- ✅ Added `WebViewScreen`

### Enhanced Phases
- **Phase 4:** Now tests SendXRP, SendTestToken, AddTrustline (3 branches)
- **Phase 7b:** NEW - Barcode/QR scanning (2 branches)
- **Phase 9:** Now tests both Web3Browser and WebView (2 branches)

### New Utilities
- `find_screen_flexible()` - Smart screen name matching
- `find_label()` - Find labels by text keywords

## 🚀 Quick Start

```powershell
# Run tour (one phase at a time)
python -B scripts/complete_ux_tour.py

# Review results
cat docs/ux_tours/tour_*/analysis/phase_1_SUMMARY.md

# Fix issues from report
# Re-run to verify fixes
python -B scripts/complete_ux_tour.py
```

## 📊 13 Phases Overview

| # | Phase | Screens | Branches |
|---|-------|---------|----------|
| 1 | Onboarding | Intro → FirstUse → AccountChoice → Mnemonic → Verify → AccountNaming → Wallet | create_new, import_existing |
| 2 | Account Management | Account creation, switching, naming | single_account, multi_account |
| 3 | Wallet Core | Balance, history, refresh | - |
| 4 | Transactions | SendXRP, SendTestToken, AddTrustline | sendxrp, send_test_tokens, trustlines |
| 5 | NFT | NFT mint, display, metadata | - |
| 6 | DEX | Trading, swaps, order book | - |
| 7 | Food Tracking | Calorie logging, meals | - |
| 7b | Scanning | Barcode, QR, Camera | qr_scan, barcode_scan |
| 8 | Settings | Preferences, theme | - |
| 9 | Web3 Browser | Web3Browser, WebView | web3_browser, webview |
| 10 | Accessibility | Touch targets, contrast, responsive | - |
| 11 | Network | Failover, retry, offline | - |
| 12 | Data Integrity | Restart, persistence, recovery | - |
| 13 | Final Analysis | Compliance report, recommendations | - |

## 🎯 Per-Phase Workflow

```
┌─────────────────────────────────────┐
│ 1. Run Phase                        │
│    python -B complete_ux_tour.py    │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│ 2. Review Analysis                  │
│    phase_N_SUMMARY.md               │
│    - Compliance scores              │
│    - Issues by priority             │
│    - Fix recommendations            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│ 3. Fix HIGH Priority Issues         │
│    Use reference citations          │
│    Apply quick fixes                │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│ 4. Re-run Phase to Verify           │
│    Target: >80% compliance          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│ 5. Continue to Next Phase           │
│    Progress auto-saved              │
└─────────────────────────────────────┘
```

## 📈 Compliance Targets

- **Overall:** >80%
- **UI/UX:** >80%
- **XRPL:** >85%
- **Performance:** >75%
- **Accessibility:** >80%

## 🔧 Environment Variables

```powershell
# Visual mode (default: ON)
$env:TOUR_VISUAL="1"

# Slow motion for observation
$env:TOUR_SLOWMO="1"

# Force phone size (iPhone 11)
$env:TOUR_FORCE_PHONE="1"
$env:TOUR_PHONE_WIDTH="414"
$env:TOUR_PHONE_HEIGHT="896"
```

## 📝 Analysis Report Structure

```
phase_N_SUMMARY.md
├── Phase Status (✅/❌ functionality/performance/appearance)
├── 📊 Compliance Scorecard
│   ├── Overall: X%
│   ├── UI/UX: X%
│   ├── XRPL: X%
│   ├── Performance: X%
│   └── Accessibility: X%
├── Test Coverage (screens/features/buttons/inputs)
├── Issues Found (functional/layout/performance/errors)
├── Best Practice Violations (with references)
├── Required Fixes
│   ├── 🔴 High Priority
│   ├── 🟡 Medium Priority
│   └── 🟢 Low Priority
└── Next Steps (with compliance goals)
```

## 🐛 Common Issues

### "Screen not found"
```python
# Some screens are dynamic (SendTestTokenScreen)
# Tour uses flexible matching automatically
# Check screen registration in app.py
```

### Black Screen
```powershell
# Ensure visual mode enabled
$env:TOUR_VISUAL="1"
# Already using SDL2 backend (VMware compatible)
```

### Tour Hangs
```powershell
# Check last action in log
cat docs/ux_tours/tour_*/logs/tour_info.log
# Try non-blocking mode (experimental)
$env:TOUR_NONBLOCKING="1"
```

### Reset Progress
```powershell
# Start fresh from Phase 1
Remove-Item docs/ux_tours/tour_progress.json
python -B scripts/complete_ux_tour.py
```

## 📚 Reference Docs (9 Domains)

Validator checks against:
1. Kivy best practices
2. KivyMD best practices
3. Material Design 3
4. UI guidelines
5. XRPL best practices
6. IPFS best practices
7. BigchainDB patterns
8. FoodRepo API
9. Bitcoin dev resources

All in `docs/reference/`

## ✅ Success Checklist

- [ ] All 13 phases executed
- [ ] Overall compliance >80%
- [ ] No HIGH severity issues
- [ ] All critical screens tested
- [ ] All branches covered
- [ ] Analysis reports reviewed
- [ ] Fixes implemented and verified

## 📞 Support

- **Detailed docs:** `docs/UX_TOUR_GUIDE.md`
- **Update summary:** `docs/UX_TOUR_V2_UPDATES.md`
- **Logs:** `docs/ux_tours/tour_*/logs/`
- **Analysis:** `docs/ux_tours/tour_*/analysis/`

---

**Last Updated:** 2025-11-18  
**Version:** 2.0  
**Next Step:** Run tour → Review Phase 1 → Fix issues → Continue
