#!/usr/bin/env python3
"""Fail when a Kubernetes Secret is committed without encrypted SOPS payloads."""

from __future__ import annotations

import sys
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

import yaml


IGNORED_DIRECTORIES = {".ansible", ".git", ".venv"}
SECRET_PAYLOAD_FIELDS = ("data", "stringData")


def yaml_files(root: Path) -> list[Path]:
    """Return repository YAML files while skipping generated directories."""
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix in {".yaml", ".yml"}
        and not IGNORED_DIRECTORIES.intersection(path.parts)
    )


def iter_kubernetes_secrets(
    document: Any, location: str = "document"
) -> Iterator[tuple[str, Mapping[str, Any]]]:
    """Yield standalone Secrets and Secrets nested in Kubernetes List objects."""
    if not isinstance(document, Mapping):
        return

    if document.get("apiVersion") == "v1" and document.get("kind") == "Secret":
        yield location, document

    if document.get("kind") in {"List", "SecretList"}:
        items = document.get("items", [])
        if isinstance(items, list):
            for index, item in enumerate(items):
                yield from iter_kubernetes_secrets(item, f"{location}.items[{index}]")


def encrypted_payload(value: Any) -> bool:
    """Require every scalar payload value to use SOPS' ENC[...] representation."""
    if isinstance(value, str):
        return value.startswith("ENC[")
    if isinstance(value, Mapping):
        return all(encrypted_payload(item) for item in value.values())
    if isinstance(value, list):
        return all(encrypted_payload(item) for item in value)
    return False


def secret_is_sops_encrypted(secret: Mapping[str, Any]) -> bool:
    """Accept only Secrets with SOPS metadata and no plaintext payload value."""
    if not isinstance(secret.get("sops"), Mapping):
        return False

    return all(
        field not in secret or encrypted_payload(secret[field])
        for field in SECRET_PAYLOAD_FIELDS
    )


def main() -> int:
    """Scan every YAML document and report unsafe Kubernetes Secrets."""
    violations: list[str] = []

    for path in yaml_files(Path.cwd()):
        try:
            documents = yaml.safe_load_all(path.read_text(encoding="utf-8"))
            for index, document in enumerate(documents, start=1):
                for location, secret in iter_kubernetes_secrets(
                    document, f"document {index}"
                ):
                    if not secret_is_sops_encrypted(secret):
                        violations.append(f"{path}: {location}")
        except (OSError, UnicodeError, yaml.YAMLError) as error:
            violations.append(f"{path}: could not inspect YAML: {error}")

    if not violations:
        print("No plaintext Kubernetes Secrets found.")
        return 0

    print("Plaintext, fake-SOPS, or unreadable Secret files found:", file=sys.stderr)
    for violation in violations:
        print(f"- {violation}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
