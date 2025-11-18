import os
import sys
import traceback

# Avoid Kivy parsing CLI args
os.environ.setdefault("KIVY_NO_ARGS", "1")
# Keep logs readable
os.environ.setdefault("KIVY_LOG_LEVEL", "warning")

from kivy.lang import Builder

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KV_DIR = os.path.join(ROOT, "src", "core", "kv")


def iter_kv_files(base_dir: str):
    for root, _dirs, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith(".kv"):
                yield os.path.join(root, f)


def main():
    kv_files = sorted(iter_kv_files(KV_DIR))
    if not kv_files:
        print(f"No KV files found under {KV_DIR}")
        return 2

    print(f"Scanning {len(kv_files)} KV files under {KV_DIR}...\n")
    failures = []
    successes = []

    for kv in kv_files:
        rel = os.path.relpath(kv, ROOT)
        try:
            # Load into a separate Builder context to avoid rule collisions
            # Using the global Builder is typical; KV rules are idempotent if consistent
            Builder.load_file(kv)
            print(f"OK  - {rel}")
            successes.append(rel)
        except Exception as e:
            print(f"ERR - {rel}")
            tb = traceback.format_exc(limit=5)
            failures.append((rel, str(e), tb))

    print("\nSummary:")
    print(f"  Success: {len(successes)}")
    print(f"  Errors : {len(failures)}")

    if failures:
        print("\nFailures detail:\n")
        for rel, msg, tb in failures:
            print(f"-- {rel}")
            print(msg)
            print(tb)
            print()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
