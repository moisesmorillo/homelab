from __future__ import annotations

import unittest

from tools.check_plaintext_secrets import (
    iter_kubernetes_secrets,
    secret_is_sops_encrypted,
)


class SecretValidationTests(unittest.TestCase):
    def test_rejects_plaintext_secret(self) -> None:
        secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "stringData": {"token": "plaintext"},
        }
        self.assertFalse(secret_is_sops_encrypted(secret))

    def test_rejects_fake_sops_metadata_with_plaintext(self) -> None:
        secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "stringData": {"token": "plaintext"},
            "sops": {"version": "3.9.0"},
        }
        self.assertFalse(secret_is_sops_encrypted(secret))

    def test_accepts_encrypted_sops_payload(self) -> None:
        secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "stringData": {"token": "ENC[AES256_GCM,data:example]"},
            "sops": {"version": "3.9.0"},
        }
        self.assertTrue(secret_is_sops_encrypted(secret))

    def test_finds_secret_nested_in_list(self) -> None:
        document = {
            "apiVersion": "v1",
            "kind": "List",
            "items": [
                {"apiVersion": "v1", "kind": "ConfigMap"},
                {"apiVersion": "v1", "kind": "Secret"},
            ],
        }
        locations = [item[0] for item in iter_kubernetes_secrets(document)]
        self.assertEqual(locations, ["document.items[1]"])


if __name__ == "__main__":
    unittest.main()
