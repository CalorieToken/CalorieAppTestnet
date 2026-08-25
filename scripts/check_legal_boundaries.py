"""Fail CI if current repository rights statements become contradictory."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(path: str, fragments: tuple[str, ...]) -> None:
    content = (ROOT / path).read_text(encoding="utf-8")
    missing = [fragment for fragment in fragments if fragment not in content]
    if missing:
        raise SystemExit(f"{path} is missing required legal text: {missing}")


def main() -> None:
    required = ("LICENSE", "COPYRIGHT.md", "NOTICE", "docs/TRADEMARK.md", "IP_EVIDENCE_REGISTER.md")
    missing = [path for path in required if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit(f"Missing legal boundary files: {missing}")

    require("LICENSE", ("NO NEW GENERAL LICENCE", "HISTORICAL LICENCE GRANTS", "Pieter", "Hendrikse"))
    require("COPYRIGHT.md", ("ICTHendrikse", "KvK 84216352", "26 August 2024"))
    require("docs/TRADEMARK.md", ("Pieter Hendrikse", "ICTHendrikse (KvK 73774693)", "019137415", "019125433"))
    require("IP_EVIDENCE_REGISTER.md", ("Official EUIPO certificate", "Do not commit certificates"))
    require("NOTICE", ("Third-party components", "Historic licence"))

    current_files = (
        "README.md",
        "LICENSE",
        "COPYRIGHT.md",
        "NOTICE",
        "docs/README.md",
        "docs/OFFICIAL_PROJECT_DOCS.md",
        "docs/LEGAL_DISCLAIMER.md",
        "docs/TRADEMARK.md",
    )
    forbidden_current_claims = (
        "registered trademark of CalorieToken",
        "registered trademarks owned by **CalorieToken**",
    )
    for path in current_files:
        content = (ROOT / path).read_text(encoding="utf-8")
        found = [claim for claim in forbidden_current_claims if claim in content]
        if found:
            raise SystemExit(f"{path} contains superseded ownership wording: {found}")

    print("Legal boundary checks passed")


if __name__ == "__main__":
    main()
