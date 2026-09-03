#!/usr/bin/env python3
"""Reject operational topology data from the public repository surface."""

from __future__ import annotations

import ipaddress
import re
import subprocess
import sys
from pathlib import Path


FORBIDDEN_EXACT_PATHS = {
    "config/network.yaml",
    "docs/current-state.md",
}
FORBIDDEN_PATH_PREFIXES = (
    ".local/",
    "ansible/inventory/production/",
    "docs/private/",
)
PUBLIC_INVENTORY_PREFIXES = (
    "ansible/inventory/ci/",
    "ansible/inventory/example/",
)
TEXT_FILENAMES = {".editorconfig", ".gitignore", "Makefile"}
TEXT_SUFFIXES = {
    ".cfg",
    ".hcl",
    ".j2",
    ".md",
    ".py",
    ".sh",
    ".tf",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
DOCUMENTATION_NETWORKS = tuple(
    ipaddress.ip_network(cidr)
    for cidr in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24")
)
IPV4_PATTERN = re.compile(
    r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?(?![\d.])"
)
LIVE_MODE_PATTERN = re.compile(r"(?m)^\s*mode:\s*live(?:\s+#.*)?\s*$")
LIVE_APPLY_PATTERN = re.compile(
    r"(?m)^\s*networkd_apply:\s*true(?:\s+#.*)?\s*$"
)
NUMERIC_GUEST_IDENTIFIER_PATTERN = re.compile(
    r"(?i)\b(?:vm|guest|container|ct)[-_ ]?\d{2,}\b"
)


def public_paths(root: Path) -> list[Path]:
    """Return tracked and unignored untracked files in the intended public tree."""
    result = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [
        root / item.decode("utf-8")
        for item in result.stdout.split(b"\0")
        if item
    ]


def path_violations(relative_path: str) -> list[str]:
    """Reject paths reserved for private operational overlays."""
    normalized = relative_path.removeprefix("./")
    violations: list[str] = []

    if normalized in FORBIDDEN_EXACT_PATHS:
        violations.append("live-data path is forbidden in the public repository")
    if normalized.startswith(FORBIDDEN_PATH_PREFIXES):
        violations.append("private-overlay path is forbidden in the public repository")
    if normalized.startswith("ansible/inventory/") and not normalized.startswith(
        PUBLIC_INVENTORY_PREFIXES
    ):
        violations.append("only CI and example inventories may be public")

    return violations


def text_violations(text: str) -> list[str]:
    """Reject common operational markers and non-documentation IPv4 literals."""
    violations: list[str] = []

    if LIVE_MODE_PATTERN.search(text):
        violations.append("a public file enables live safety mode")
    if LIVE_APPLY_PATTERN.search(text):
        violations.append("a public file enables networkd_apply")
    if NUMERIC_GUEST_IDENTIFIER_PATTERN.search(text):
        violations.append("a public file contains a numeric VM/container identifier")

    for match in IPV4_PATTERN.finditer(text):
        token = match.group(0)
        try:
            address = ipaddress.ip_address(token.partition("/")[0])
        except ValueError:
            continue

        if address.is_loopback:
            continue
        if any(address in network for network in DOCUMENTATION_NETWORKS):
            continue
        violations.append(f"non-documentation IPv4 literal: {token}")

    return violations


def is_text_candidate(path: Path) -> bool:
    """Limit content inspection to source and documentation files."""
    return path.name in TEXT_FILENAMES or path.suffix in TEXT_SUFFIXES


def main() -> int:
    """Inspect the intended public surface and report every violation."""
    root = Path.cwd()
    violations: list[str] = []

    try:
        paths = public_paths(root)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Could not enumerate the public repository surface: {error}", file=sys.stderr)
        return 1

    for path in paths:
        relative_path = path.relative_to(root).as_posix()
        for violation in path_violations(relative_path):
            violations.append(f"{relative_path}: {violation}")

        if not path.is_file() or not is_text_candidate(path):
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            violations.append(f"{relative_path}: could not inspect text: {error}")
            continue

        for violation in text_violations(text):
            violations.append(f"{relative_path}: {violation}")

    if not violations:
        print("Public repository boundary is clean.")
        return 0

    print("Public repository boundary violations found:", file=sys.stderr)
    for violation in violations:
        print(f"- {violation}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
