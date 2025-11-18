import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.xrpl_client_manager import XRPLClientManager  # noqa: E402


class TestXRPLClientManager(unittest.TestCase):
    def test_initialize_manager(self):
        # Use a reduced server list for quicker testing
        manager = XRPLClientManager(servers=["https://testnet.xrpl-labs.com"], timeout=5)
        # Either connected or not; ensure attributes exist
        self.assertIsNotNone(manager.servers)
        self.assertTrue(isinstance(manager.servers, list))

    def test_status_structure(self):
        manager = XRPLClientManager(servers=["https://testnet.xrpl-labs.com"], timeout=5)
        status = manager.get_status()
        self.assertIn("connected", status)
        self.assertIn("current_server", status)
        self.assertIn("failed_servers", status)
        self.assertIn("available_servers", status)

    def test_force_reconnect(self):
        manager = XRPLClientManager(servers=["https://testnet.xrpl-labs.com"], timeout=5)
        result = manager.force_reconnect()
        self.assertIsInstance(result, bool)


if __name__ == "__main__":
    unittest.main()
