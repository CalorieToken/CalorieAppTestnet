import os
import sys
import unittest

# Ensure src is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestVersionInfo(unittest.TestCase):
    def test_version_constants(self):
        from VERSION import __status__, __version__

        self.assertRegex(__version__, r"^\d+\.\d+\.\d+$")
        self.assertIn(__status__, ["stable", "beta", "alpha", "production-ready"])


if __name__ == "__main__":
    unittest.main()
