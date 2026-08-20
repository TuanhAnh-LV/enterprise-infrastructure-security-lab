# Security and Responsible Use

This repository documents a defensive cybersecurity lab operated in an isolated, authorized environment.

## Public-content rules

- Never commit passwords, API keys, VPN pre-shared keys, private keys, recovery keys, session cookies, or authentication tokens.
- Never upload production IP addresses, customer names, internal domain names, personal data, or unredacted screenshots.
- Do not upload proprietary FortiGate, Cisco, Windows, EVE-NG, or other vendor images.
- Do not upload live packet captures or logs until they have been reviewed and sanitized.
- Keep all testing inside systems you own or are explicitly authorized to assess.

Configuration files in this repository use values such as `<STRONG_PASSWORD>` and `<STRONG_PSK>`. Replace them only in a private working copy or through a secure secret-management process. Run `python3 scripts/pre_publish_check.py` before publishing changes.

## Reporting an issue

If sensitive data is accidentally committed, remove access to the exposed credential immediately, rotate it, and remove the data from the repository history before making the repository public again.

