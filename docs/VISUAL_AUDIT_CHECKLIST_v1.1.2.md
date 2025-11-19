Title: Visual Audit Checklist v1.1.2
Date: 2025-11-19
Branch: feature/visual-refinement-v1.1.2

Objective
Ensure UI consistency, accessibility, and performance alignment ahead of v1.1.2 release.

Scope Areas
1. Spacing & Layout
2. Elevation & Shadows
3. Color & Contrast
4. Typography Hierarchy
5. Icons & Imagery
6. Component States
7. Responsiveness / Scaling
8. Accessibility (A11y)
9. Motion & Feedback
10. Performance Baselines

Checklist
## 1. Spacing & Layout
- [ ] Confirm consistent vertical rhythm (base unit 8px or defined token)
- [ ] Normalize padding/margin in KV files (`src/core/kv/*.kv`)
- [ ] Remove arbitrary inline spacing hacks
- [ ] Align form fields and buttons to grid

## 2. Elevation & Shadows
- [ ] Define elevation scale (e.g., 0, 2, 4, 8, 16)
- [ ] Replace ad-hoc shadow values with scale tokens
- [ ] Verify contrast of elevated surfaces vs background

## 3. Color & Contrast
- [ ] Audit palette usage (#00A651 primary, #1E3A8A secondary, #FCD34D accent)
- [ ] WCAG AA contrast for text on backgrounds
- [ ] No unintended grayscale placeholders in final UI

## 4. Typography Hierarchy
- [ ] Establish H1–H6 + body + caption sizes
- [ ] Ensure uniform font weight application
- [ ] Verify truncation/overflow handling for long labels

## 5. Icons & Imagery
- [ ] Standardize icon sizes (16/20/24/32)
- [ ] Replace low-res or stretched assets in `assets/images/`
- [ ] Provide alt text / descriptive context where applicable

## 6. Component States
- [ ] Hover / Press / Disabled states defined (visual + semantic)
- [ ] Loading indicators consistent (spinner style unified)
- [ ] Error states clearly communicated (color + messaging)

## 7. Responsiveness / Scaling
- [ ] Test common breakpoints / window sizes
- [ ] Confirm no clipped text or cropped buttons
- [ ] Dynamic resizing preserves hierarchy

## 8. Accessibility
- [ ] Minimum touch target size (48px equivalent)
- [ ] Focus outlines visible and consistent
- [ ] Color not sole carrier of meaning (add icon / label)

## 9. Motion & Feedback
- [ ] Animation durations standardized (e.g., 150–250ms)
- [ ] Avoid excessive bounce or opacity flicker
- [ ] Provide non-animated fallback if performance constrained

## 10. Performance Baselines
- [ ] Measure initial screen render time
- [ ] Profile heavy screens (Wallet, Trade)
- [ ] Identify layout thrash / unnecessary rebinds
- [ ] Record baseline FPS target and memory footprint

Data Capture Template
| Area | Metric | Baseline | Target | Notes |
|------|--------|----------|--------|-------|
| Render Time (Intro) | ms to interactive | TBD | < 1200ms | Optimize image loading |
| Wallet Screen FPS | average fps | TBD | > 55 | Reduce redraws |
| Memory Footprint | MB after 5 min | TBD | < 220MB | Cache pruning |

Action Log
- Pending: Initial measurement pass
- Pending: Spacing token extraction
- Pending: Elevation scale declaration file

Next Steps
1. Run measurement script (to be created) for baseline.
2. Introduce central design tokens module.
3. Patch KV layouts for spacing & elevation.
4. Re-measure and update table.

Sign-off Criteria
- All checklist items reviewed and either completed or documented.
- Baseline metrics captured and at least two improvements implemented.
- Accessibility items meet WCAG AA (contrast + focus).
