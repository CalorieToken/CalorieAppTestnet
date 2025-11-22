# Phase 1 Automated Diagnostics Report

Generated Aggregate: 2025-11-20T22:41:25.886645Z



This report aggregates automated scripts output. Manual visual audit still required.

### Contrast Audit
Generated: 2025-11-20T22:41:07.739632Z

| Case | Ratio | AA | AAA |
|------|-------|----|-----|
| button_text | 8.25 | PASS | PASS |
| button_vs_bg | 7.53 | PASS | PASS |
| primary_label | 19.17 | PASS | PASS |
| secondary_label | 13.45 | PASS | PASS |

### Workflow Diagnostics
Generated: 2025-11-20T22:24:17.710013Z

| Template | Time (s) | Missing Files | Placeholder Artifacts |
|----------|----------|---------------|-----------------------|
| blank_kivy | 0.033 | - | 0 |
| crypto_wallet | 0.093 | - | 0 |
| material_kivymd | 0.026 | - | 0 |

### Export Validation
Generated: 2025-11-20T22:24:32.191461Z

Project Path: C:\Users\P\MyProjects\CalorieAppTestnet\universal_app_builder\automation\temp_export_workspace\export_diag
Zip Path: C:\Users\P\MyProjects\CalorieAppTestnet\universal_app_builder\automation\temp_export_workspace\export_diag.zip

| Metric | Value |
|--------|-------|
| File Count | 9 |
| Venv Entries | 0 |
| Binary Entries | 0 |

### Functional Smoke Tests
Generated: 1763677188.6715949

| Template | Status | Create (s) | Export (s) | Zip Exists |
|----------|--------|------------|------------|------------|
| blank_kivy | ok | 0.038 | 0.202 | True |
| crypto_wallet | ok | 0.031 | 0.071 | True |
| material_kivymd | ok | 0.042 | 0.072 | True |

### Performance Profiler
Generated: 1763677387.2631054

**Summary:**

- Avg create time: 0.0336s
- Avg export time: 0.1553s
- Total files: 27
- Total size: 45.42 KB
- Success rate: 3/3

| Template | Create (s) | Export (s) | Files | Size (KB) |
|----------|------------|------------|-------|-----------|
| blank_kivy | 0.025 | 0.2248 | 8 | 15.91 |
| crypto_wallet | 0.0354 | 0.0914 | 11 | 18.29 |
| material_kivymd | 0.0403 | 0.1498 | 8 | 11.22 |

### GUI Event Simulation

**Summary:**

- Total tests: 6
- Passed: 5
- Failed: 1

| Test | Status | Error |
|------|--------|-------|
| show_template_selector | ok | - |
| show_about | ok | - |
| show_info | ok | - |
| show_error | ok | - |
| show_success | ok | - |
| load_projects | skipped | - |

### Appearance Inventory

**Colors:**

- `text_color`: 1,1,1,1
- `md_bg_color`: 0.06,0.06,0.06,1

**Spacing (dp):**
- `padding_dp`: [20]
- `spacing_dp`: [10, 15]

**Button Styles:** `filled`

**Recommendations:**
- button_bg_color currently [0.2, 0.4, 0.8, 1] (blue)
- button_text_color currently [1, 1, 1, 1] (white)
- Contrast audit shows button_text ratio=4.63 (AA pass), button_vs_bg ratio=4.14 (AA fail)
- Recommended: increase button_bg lightness or button_text brightness for AAA compliance
- Primary labels: high contrast (19.17), secondary labels: good contrast (13.45)
- Spacing values range from 10-20 dp; consistent but could benefit from design system tokens
- Font usage: bold flags used, theme_text_color 'Custom' with explicit RGBA
- Button styles: 'filled' used; consider adding 'outlined' or 'text' variants for hierarchy