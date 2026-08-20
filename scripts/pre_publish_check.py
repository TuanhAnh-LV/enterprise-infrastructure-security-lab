#!/usr/bin/env python3
"""Fail when a repository contains common private artifacts or obvious secrets.

This lightweight check is intentionally conservative. It complements manual review;
it cannot prove that a repository is safe to publish.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SKIP_PARTS = {".git", ".venv", "venv", "__pycache__"}
FORBIDDEN_SUFFIXES = {
    ".iso",
    ".qcow",
    ".qcow2",
    ".img",
    ".ova",
    ".ovf",
    ".vmdk",
    ".vdi",
    ".p12",
    ".pfx",
    ".jks",
    ".keystore",
    ".pcap",
    ".pcapng",
    ".bak",
    ".backup",
}

PRIVATE_KEY_HEADER = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.IGNORECASE
)

CREDENTIAL_ASSIGNMENT = re.compile(
    r"(?ix)(?:"
    r"\bset\s+(?:password|passwd|psksecret)\s+"
    r"|\b(?:password|passwd|psksecret|api[_-]?key|access[_-]?token)\b\s*(?:=|:)\s*"
    r")[\"']?([^\s\"']+)"
)

ALLOWED_VALUE = re.compile(
    r"^(?:<[^>]+>|\$\{[^}]+\}|REDACTED|CHANGEME|EXAMPLE)$", re.IGNORECASE
)

TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".conf",
    ".cfg",
    ".xml",
    ".yml",
    ".yaml",
    ".json",
    ".py",
    ".sh",
    ".ps1",
    ".gitignore",
}


def is_skipped(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.relative_to(ROOT).parts)


def main() -> int:
    findings: list[str] = []

    for path in ROOT.rglob("*"):
        if not path.is_file() or is_skipped(path):
            continue

        relative = path.relative_to(ROOT)
        suffix = path.suffix.lower()

        if suffix in FORBIDDEN_SUFFIXES:
            findings.append(f"forbidden artifact: {relative}")
            continue

        if suffix not in TEXT_SUFFIXES and path.name != ".gitignore":
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"unreviewed binary file: {relative}")
            continue

        if PRIVATE_KEY_HEADER.search(content):
            findings.append(f"private-key material: {relative}")

        for line_number, line in enumerate(content.splitlines(), start=1):
            if "<" in line and ">" in line:
                # Public templates deliberately use angle-bracket placeholders.
                continue
            for match in CREDENTIAL_ASSIGNMENT.finditer(line):
                value = match.group(1).rstrip(",;)")
                if not ALLOWED_VALUE.fullmatch(value):
                    findings.append(
                        f"possible credential: {relative}:{line_number}"
                    )

    if findings:
        print("Pre-publication check FAILED:\n")
        for finding in sorted(set(findings)):
            print(f"- {finding}")
        print("\nReview each item. Do not publish until all findings are resolved.")
        return 1

    print("Pre-publication check passed: no blocked artifacts or obvious secrets found.")
    print("Manual review of screenshots, logs, addresses and personal data is still required.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
