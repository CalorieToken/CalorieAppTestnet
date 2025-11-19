"""Release Tagging Helper

Automates version bump, changelog scaffold, release note creation.
Usage:
  python scripts/tag_release.py --version 0.1.1-testnet --title "visual polish" --preview
  python scripts/tag_release.py --version 0.1.1-testnet --title "visual polish" --apply

Requires: clean working tree; run via PR process before tagging.
"""

from __future__ import annotations
import argparse, re, sys, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "src" / "VERSION.py"
CHANGELOG = ROOT / "CHANGELOG.md"
RELEASE_DIR = ROOT / "docs"

def read_version_py() -> str:
    text = VERSION_FILE.read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    return m.group(1) if m else "UNKNOWN"

def update_version_py(new_version: str, apply: bool):
    text = VERSION_FILE.read_text(encoding="utf-8")
    text = re.sub(r'__version__\s*=\s*"[^"]+"', f'__version__ = "{new_version}"', text)
    text = re.sub(r'__date__\s*=\s*"[^"]+"', f'__date__ = "{datetime.date.today()}"', text)
    if apply:
        VERSION_FILE.write_text(text, encoding="utf-8")
    return text

def append_changelog(new_version: str, title: str, apply: bool):
    entry = (
        f"## [{new_version}] - {datetime.date.today()}\n\n"
        f"### Pending\n"
        f"- Placeholder: {title}\n"
        f"- Fill in merged items before tag.\n\n"
    )
    original = CHANGELOG.read_text(encoding="utf-8")
    updated = entry + original
    if apply:
        CHANGELOG.write_text(updated, encoding="utf-8")
    return entry

def create_release_note(new_version: str, title: str, apply: bool):
    fname = RELEASE_DIR / f"RELEASE_NOTE_{new_version.replace('.', '_').upper()}.md"
    content = (
        f"# Release {new_version}\n\n"
        f"## Draft - {title}\n\n"
        "Populate after merging PRs.\n\n"
        "## Checklist\n"
        "- [ ] Changelog finalized\n"
        "- [ ] Version bump committed\n"
        "- [ ] Security scan re-run\n"
        "- [ ] Feature flags validated\n"
        "- [ ] Tag annotated & pushed\n"
    )
    if apply:
        fname.write_text(content, encoding="utf-8")
    return fname, content

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--version", required=True, help="New semantic version (e.g. 0.1.1-testnet)")
    p.add_argument("--title", required=True, help="Short release focus description")
    p.add_argument("--apply", action="store_true", help="Write changes to disk")
    p.add_argument("--preview", action="store_true", help="Preview without writing")
    args = p.parse_args()

    current = read_version_py()
    if current == args.version:
        print(f"Version already at {current}; no bump performed.")
        sys.exit(0)

    updated_version_py = update_version_py(args.version, apply=args.apply)
    changelog_entry = append_changelog(args.version, args.title, apply=args.apply)
    rn_path, rn_content = create_release_note(args.version, args.title, apply=args.apply)

    print("--- Version.py Updated ---")
    print(updated_version_py.splitlines()[0:8])
    print("--- Changelog Entry ---")
    print(changelog_entry)
    print("--- Release Note Path ---")
    print(rn_path)
    if not args.apply and not args.preview:
        print("(Run with --preview or --apply)")

if __name__ == "__main__":
    main()
