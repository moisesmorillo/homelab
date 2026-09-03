from __future__ import annotations

import unittest

from tools.check_public_boundary import path_violations, text_violations


class PublicBoundaryTests(unittest.TestCase):
    def test_rejects_private_overlay_path(self) -> None:
        self.assertTrue(path_violations(".local/config/network.yaml"))

    def test_rejects_live_data_path(self) -> None:
        self.assertTrue(path_violations("config/network.yaml"))

    def test_rejects_unapproved_inventory_directory(self) -> None:
        self.assertTrue(path_violations("ansible/inventory/live/hosts.yaml"))

    def test_rejects_private_ipv4_literal(self) -> None:
        private_address = ".".join(("192", "168", "50", "10"))
        self.assertTrue(text_violations(f"address: {private_address}\n"))

    def test_allows_documentation_ipv4_literal(self) -> None:
        self.assertFalse(text_violations("address: 192.0.2.10/24\n"))

    def test_rejects_numeric_guest_identifier(self) -> None:
        identifier = "-".join(("virtualization", "guest", str(424242)))
        violations = text_violations(f"placement: {identifier}\n")
        self.assertIn(
            "a public file contains a numeric VM/container identifier",
            violations,
        )

    def test_rejects_live_mode(self) -> None:
        self.assertTrue(text_violations("mode: live\n"))

    def test_rejects_enabled_network_apply(self) -> None:
        self.assertTrue(text_violations("networkd_apply: true\n"))


if __name__ == "__main__":
    unittest.main()
