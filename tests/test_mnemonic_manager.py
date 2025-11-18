import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.mnemonic_manager import (  # noqa: E402
    MnemonicManager,
    validate_mnemonic_words,
)


class TestMnemonicManager(unittest.TestCase):
    def setUp(self):
        self.mm = MnemonicManager()

    def test_generate_mnemonic_length(self):
        words = self.mm.generate_mnemonic()
        self.assertEqual(len(words), 12)

    def test_validate_generated_mnemonic(self):
        words = self.mm.generate_mnemonic()
        self.assertTrue(self.mm.validate_mnemonic(words))

    def test_parse_mnemonic_input(self):
        sample = "1. abandon 2. ability 3. able 4. about 5. above 6. absent 7. absorb 8. abstract 9. absurd 10. abuse 11. access 12. accident"
        parsed = self.mm.parse_mnemonic_input(sample)
        self.assertEqual(len(parsed), 12)
        self.assertTrue(validate_mnemonic_words(parsed))

    def test_wallet_generation(self):
        wallet, words = self.mm.generate_wallet_with_mnemonic()
        self.assertEqual(len(words), 12)
        self.assertTrue(self.mm.validate_mnemonic(words))
        self.assertTrue(hasattr(wallet, "classic_address"))


if __name__ == "__main__":
    unittest.main()
