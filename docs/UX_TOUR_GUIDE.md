# UX Tour Automated Testing Guide

## Overview

The UX Tour is an automated end-to-end UI/UX testing framework that validates all app screens, flows, and components. It captures screenshots and generates detailed test reports.

## Running the Tour

### Local Execution

```powershell
# Run the full tour with online connectivity
python scripts/ux_tour.py

# Run with offline mode testing only
$env:OFFLINE_MODE="1"; python scripts/ux_tour.py
```

### Output

Reports and screenshots are saved to `docs/ui_tour/<timestamp>/`:
- `test_report.txt` - Summary of all tests with pass/fail status
- `*.png` - Screenshots of each screen and test state

## Test Coverage

### Online Path Tests (84 tests)
- **Wallet Screen**: Header, address, balance, buttons, account selector
- **Send XRP**: Form inputs, hints, validation, confirmation dialog, transactions
- **Settings**: Header, account list, refresh button
- **Token Send**: Dynamic screen creation, form fields, hints
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
