# Repository Cleanup Plan - CalorieAppTestnet Main Branch

## Executive Summary

The main branch currently contains **Universal App Builder** development material that should be **removed from public GitHub**. Only the finished CalorieApp code and essential documentation should remain public.

## Current Issues

1. **Universal App Builder directory is public** (`universal_app_builder/`)
   - Contains incomplete development work
   - Includes test projects, temporary workspaces, automation scripts
   - Should remain private until finished

2. **Development/test artifacts are public**:
   - Test logs (`ux_tour_phase1_*.log`)
   - Python cache (`__pycache__/`)
   - Coverage files (`.coverage`)
   - Local wallet data files

3. **Excessive documentation** for public consumption:
   - Many internal development checkpoint files
   - Detailed development progress documents
   - Technical implementation details meant for development

## Recommended Actions

### 🗑️ Files/Directories to DELETE from main branch

#### 1. Universal App Builder (Entire Directory)
```
universal_app_builder/           # DELETE - All unfinished work
```

#### 2. Test/Development Artifacts
```
ux_tour_phase1_20251119_070640.log    # DELETE
ux_tour_phase1_20251119_070729.log    # DELETE
.coverage                              # DELETE (already in .gitignore)
__pycache__/                           # DELETE (already in .gitignore)
wallet_data.bak                        # DELETE (user data)
wallet_data.dat                        # DELETE (user data)
wallet_data.dir                        # DELETE (user data)
wallet_state.json                      # DELETE (user data)
```

#### 3. Development Documentation (Internal Progress Tracking)
```
docs/development-progress/              # DELETE - Internal checkpoints
DEVELOPMENT_CHECKPOINT.md               # DELETE (if exists)
FINAL_PROJECT_STATUS.md                 # DELETE (if exists)
FINAL_SUMMARY.md                        # DELETE (if exists)
FRESH_USER_TEST_SUCCESS.md             # DELETE (if exists)
MNEMONIC_FEATURE_COMPLETE.md            # DELETE (if exists)
MNEMONIC_SCREENS_COMPLETE.md            # DELETE (if exists)
PROJECT_ORGANIZATION.md                 # DELETE (if exists)
REORGANIZATION_COMPLETE.md              # DELETE (if exists)
COMMIT_QUICK_REFERENCE.md               # DELETE - Internal dev reference
COMPREHENSIVE_TODO_LIST.md              # DELETE - Internal planning
GIT_COMMIT_GUIDE.md                     # DELETE - Internal process
```

#### 4. Internal Test Files (Keep in private repo only)
```
test_calorie_linking.py                 # DELETE - Internal test
test_keypair_import_screen.py           # DELETE - Internal test
test_fresh_user_mnemonic.py            # DELETE (if exists)
test_mnemonic_app.py                   # DELETE (if exists)
test_mnemonic_standalone.py            # DELETE (if exists)
demo_mnemonic_improvements.py          # DELETE (if exists)
```

### ✅ Files/Directories to KEEP (Public-Facing)

#### Essential Application Files
```
main.py                    # Core app
run.py                     # Run script
setup.py                   # Package setup
buildozer.spec            # Build config
requirements.txt          # Dependencies
requirements.in           # Dependency sources
pyproject.toml            # Project config
LICENSE                   # License
```

#### Source Code (Finished Features)
```
src/                      # All finished CalorieApp source code
  ├── core/              # App core
  ├── screens/           # All screens
  ├── utils/             # Utilities
  └── VERSION.py         # Version info
```

#### Essential Resources
```
assets/                   # App assets (images, etc.)
config/                   # Configuration files
data/                     # App data structures
scripts/                  # Public utility scripts (run.py, etc.)
```

#### Public-Safe Documentation ONLY
```
README.md                                 # Main readme
docs/
  ├── CHANGELOG.md                       # Version history
  ├── CONTRIBUTING.md                    # Contribution guide
  ├── TODO.md                           # Public roadmap
  ├── QUICK_START.md                    # Getting started
  ├── TRADEMARK.md                      # Trademark info
  ├── UX_TOUR_GUIDE.md                  # Public tour overview
  ├── TOKEN_SYSTEM_GUIDE.md             # Token usage
  ├── TRANSACTION_DISPLAY_GUIDE.md      # Transaction UI
  ├── FAUCET_TROUBLESHOOTING.md         # Faucet help
  ├── LEGAL_DISCLAIMER.md               # Legal info (if exists)
  └── OFFICIAL_PROJECT_DOCS.md          # Doc index
```

#### CI/CD & Quality
```
.github/                  # GitHub Actions workflows (CI/CD)
.gitignore               # Git ignore rules
.editorconfig            # Editor config
.pre-commit-config.yaml  # Pre-commit hooks
tests/                   # PUBLIC unit tests only (not internal dev tests)
```

#### Marketing/Release Materials
```
CHANGELOG.md                              # KEEP
RELEASE_STRATEGY_SUMMARY.md              # KEEP
SOCIAL_MEDIA_ANNOUNCEMENT_KIT.md         # KEEP
```

### 📝 Documentation to Simplify/Consolidate

Some docs contain too much internal detail. Consider:

1. **UX Tour docs** - Keep high-level guide, remove implementation details
2. **Development progress docs** - Merge relevant info into CHANGELOG, delete originals
3. **Internal guides** - Move to private notes or delete

## Implementation Steps

### Option 1: Clean Main Branch Directly (Recommended)

```powershell
# 1. Switch to main branch
git checkout main

# 2. Remove Universal App Builder completely
git rm -rf universal_app_builder/

# 3. Remove development artifacts
git rm ux_tour_phase1_*.log
git rm test_calorie_linking.py test_keypair_import_screen.py
git rm wallet_data.* wallet_state.json

# 4. Remove internal documentation
git rm COMMIT_QUICK_REFERENCE.md
git rm COMPREHENSIVE_TODO_LIST.md
git rm GIT_COMMIT_GUIDE.md
git rm -rf docs/development-progress/

# 5. Update .gitignore to prevent re-adding
# Add patterns for:
# - *.log (test logs)
# - wallet_data.* (local wallet files)
# - wallet_state.json
# - __pycache__/
# - .coverage

# 6. Commit the cleanup
git commit -m "chore: clean repository - remove development artifacts and unfinished Universal App Builder

- Remove universal_app_builder/ directory (development work, not ready for public)
- Remove internal development documentation and progress tracking
- Remove test artifacts and logs
- Remove local wallet data files
- Update .gitignore to prevent re-adding sensitive files

This cleanup ensures only finished CalorieApp code and essential documentation
remain public, while development work stays private until ready for release."

# 7. Force push to GitHub (THIS REWRITES HISTORY)
git push origin main --force-with-lease
```

### Option 2: Create Clean Public Branch

If you want to preserve history:

```powershell
# 1. Create new clean branch from main
git checkout main
git checkout -b public-release

# 2. Remove unwanted files (same as Option 1 steps 2-5)
# ... (same removal commands)

# 3. Commit
git commit -m "chore: prepare public release branch - remove internal development"

# 4. Push new branch
git push origin public-release

# 5. Update default branch on GitHub to public-release
# Then delete old main branch and rename public-release to main
```

## Risk Assessment

### Low Risk (Safe to Delete)
- `universal_app_builder/` - Exists on feature branch
- Test logs - Reproducible
- Cache files - Automatically regenerated
- Internal docs - Preserved in feature branch

### Medium Risk (Verify First)
- Test files in root - Check if needed for CI
- Some docs - May be referenced elsewhere

### High Risk (DO NOT DELETE)
- `src/` directory - Core application
- `README.md` - Primary documentation
- `LICENSE` - Legal requirement
- `.github/` - CI/CD

## Post-Cleanup Verification

After cleanup, main branch should contain:

1. ✅ Only **CalorieApp** source code
2. ✅ Essential **public documentation**
3. ✅ **Build/deployment** configs
4. ✅ **CI/CD** workflows
5. ✅ **License** and legal files
6. ✅ **Public assets** only

7. ❌ NO **Universal App Builder** code
8. ❌ NO **internal development** docs
9. ❌ NO **test artifacts** or logs
10. ❌ NO **user data** files

## GitHub Settings Recommendations

After cleanup, configure repository:

1. **Branch Protection** for main:
   - Require pull request reviews
   - Require status checks
   - Prevent force pushes (after initial cleanup)

2. **Secrets Management**:
   - Ensure no API keys in code
   - Use GitHub Secrets for CI/CD

3. **Collaborator Access**:
   - Review who has write access
   - Use teams for organization

## Summary

**Total files/directories to remove: ~50+**
- 1 major directory (`universal_app_builder/`)
- Multiple development documentation files
- Test artifacts and logs
- Local wallet data

**Remaining: Clean, professional public repository**
- Focused on finished CalorieApp
- Essential documentation only
- Ready for public consumption
